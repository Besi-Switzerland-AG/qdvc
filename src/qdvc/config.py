import logging
import os
import posixpath
import re
from contextlib import contextmanager
from functools import partial

from funcy import cached_property, compact, memoize

from qdvc.exceptions import QdvcException, NotQdvcRepoError

logger = logging.getLogger(__name__)


class ConfigError(QdvcException):
    """QDVC config exception."""

    def __init__(self, msg):
        super().__init__(f"config file error: {msg}")


@memoize
def get_compiled_schema():
    from voluptuous import Schema

    from .config_schema import SCHEMA

    return Schema(SCHEMA)


class Config(dict):
    """Class that manages configuration files for a DVC repo.
    Args:
        qdvc_dir (str): optional path to `.qdvc` directory, that is used to
            access repo-specific configs like .qdvc/config and
            .qdvc/config.local.
        validate (bool): optional flag to tell qdvc if it should validate the
            config or just load it as is. 'True' by default.
    Raises:
        ConfigError: thrown if config has an invalid format.
    """

    APPNAME = "qdvc"
    APPAUTHOR = "besi"

    SYSTEM_LEVELS = ("system", "global")
    REPO_LEVELS = ("repo", "local")
    # In the order they shadow each other
    LEVELS = SYSTEM_LEVELS + REPO_LEVELS

    CONFIG = "config"
    CONFIG_LOCAL = "config.local"

    def __init__(
        self, qdvc_dir=None, validate=True, config=None
    ):  # pylint: disable=super-init-not-called

        self.qdvc_dir = qdvc_dir

        if not qdvc_dir:
            try:
                from qdvc.repo import Repo

                self.qdvc_dir = Repo.find_qdvc_dir()
            except NotQdvcRepoError:
                self.qdvc_dir = None
        else:
            self.qdvc_dir = os.path.abspath(os.path.realpath(qdvc_dir))
        self.load(validate=validate, config=config)

    @classmethod
    def get_dir(cls, level: str):
        from appdirs import site_config_dir, user_config_dir

        assert level in ("global", "system")

        if level == "global":
            return user_config_dir(cls.APPNAME, cls.APPAUTHOR)
        if level == "system":
            return site_config_dir(cls.APPNAME, cls.APPAUTHOR)

    @cached_property
    def files(self):
        files = {
            level: os.path.join(self.get_dir(level), self.CONFIG)
            for level in ("system", "global")
        }

        if self.qdvc_dir is not None:
            files["repo"] = os.path.join(self.qdvc_dir, self.CONFIG)
            files["local"] = os.path.join(self.qdvc_dir, self.CONFIG_LOCAL)
        return files

    @staticmethod
    def init(qdvc_dir):
        """Initializes qdvc config.
        Args:
            qdvc_dir (str): path to .qdvc directory.
        Returns:
            qdvc.config.Config: config object.
        """
        config_file = os.path.join(qdvc_dir, Config.CONFIG)
        open(config_file, "w+", encoding="utf-8").close()
        return Config(qdvc_dir)

    def load(self, validate=True, config=None):
        """Loads config from all the config files.
        Raises:
            ConfigError: thrown if config has an invalid format.
        """
        conf = self.load_config_to_level()

        if config is not None:
            merge(conf, config)

        if validate:
            conf = self.validate(conf)

        self.clear()
        self.update(conf)

        # Add resolved default cache.dir
        if "cache" in self and not self["cache"].get("dir") and self.qdvc_dir:
            self["cache"]["dir"] = os.path.join(self.qdvc_dir, "cache")

    def _load_config(self, level):
        from configobj import ConfigObj

        filename = self.files[level]  # type: ignore

        if os.path.lexists(filename):
            with open(filename, mode="r", encoding=None) as fobj:
                conf_obj = ConfigObj(fobj)
        else:
            conf_obj = ConfigObj()
        return _lower_keys(conf_obj.dict())

    def _save_config(self, level, conf_dict):
        from configobj import ConfigObj

        filename = self.files[level]  # type: ignore

        logger.debug("Writing '%s'.", filename)

        os.makedirs(os.path.dirname(filename))

        config = ConfigObj(compact(conf_dict))
        with open(filename, "wb") as fobj:
            config.write(fobj)
        config.filename = filename

    def load_one(self, level):
        conf = self._load_config(level)
        conf = self._load_paths(conf, self.files[level])  # type: ignore

        # Auto-verify sections
        for key in get_compiled_schema().schema:
            conf.setdefault(key, {})

        return conf

    @staticmethod
    def _load_paths(conf, filename):
        abs_conf_dir = os.path.abspath(os.path.dirname(filename))

        def resolve(path):
            from .config_schema import RelPath

            if os.path.isabs(path) or re.match(r"\w+://", path):
                return path

            # on windows convert slashes to backslashes
            # to have path compatible with abs_conf_dir
            if os.path.sep == "\\" and "/" in path:
                path = path.replace("/", "\\")

            return RelPath(os.path.join(abs_conf_dir, path))

        return Config._map_dirs(conf, resolve)

    @staticmethod
    def _to_relpath(conf_dir, path):
        from dvc.utils import relpath

        from .config_schema import RelPath

        if re.match(r"\w+://", path):
            return path

        if isinstance(path, RelPath) or not os.path.isabs(path):
            path = relpath(path, conf_dir)
            return path.replace(os.sep, posixpath.sep)

        return path

    @staticmethod
    def _save_paths(conf, filename):
        conf_dir = os.path.dirname(filename)
        rel = partial(Config._to_relpath, conf_dir)

        return Config._map_dirs(conf, rel)

    @staticmethod
    def _map_dirs(conf, func):
        from voluptuous import ALLOW_EXTRA, Schema

        dirs_schema = {}
        return Schema(dirs_schema, extra=ALLOW_EXTRA)(conf)

    def load_config_to_level(self, level=None):
        merged_conf = {}
        for merge_level in self.LEVELS:
            if merge_level == level:
                break
            if merge_level in self.files:  # type: ignore
                merge(merged_conf, self.load_one(merge_level))
        return merged_conf

    def read(self, level=None):
        # NOTE: we read from a merged config by default, same as git config
        if level is None:
            return self.load_config_to_level()
        return self.load_one(level)

    @contextmanager
    def edit(self, level=None, validate=True):
        # NOTE: we write to repo config by default, same as git config
        level = level or "repo"
        if self.qdvc_dir is None and level in self.REPO_LEVELS:
            raise ConfigError("Not inside a QDVC repo")

        conf = self.load_one(level)
        yield conf

        conf = self._save_paths(conf, self.files[level])  # type: ignore

        merged_conf = self.load_config_to_level(level)
        merge(merged_conf, conf)

        if validate:
            self.validate(merged_conf)

        self._save_config(level, conf)
        self.load(validate=validate)

    @staticmethod
    def validate(data):
        from voluptuous import Invalid

        try:
            return get_compiled_schema()(data)
        except Invalid as exc:
            raise exc


def merge(into, update):
    """Merges second dict into first recursively"""
    for key, val in update.items():
        if isinstance(into.get(key), dict) and isinstance(val, dict):
            merge(into[key], val)
        else:
            into[key] = val


def _lower_keys(data):
    return {
        k.lower(): _lower_keys(v) if isinstance(v, dict) else v for k, v in data.items()
    }

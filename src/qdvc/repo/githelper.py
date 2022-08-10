from git.repo import Repo as GitRepo


def checkout_master(repo: GitRepo):
    if repo.heads:
        repo.heads.master.checkout()
    if repo.remotes:
        repo.remotes[0].pull()

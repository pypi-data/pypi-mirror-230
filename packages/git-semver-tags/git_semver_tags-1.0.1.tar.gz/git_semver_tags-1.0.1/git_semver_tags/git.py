from subprocess import Popen, PIPE
import os

from .version import Version


__all__ = ['highest_tagged_git_version']


def highest_tagged_git_version(repo_location):
    """Ask the git repo what the most recent tagged commit on the index is."""

    with Popen(
            ['git', 'describe', '--tags', 'HEAD'],
            stdin=PIPE, stdout=PIPE, stderr=PIPE,
            cwd=os.path.abspath(repo_location),
        ) as cli_cmd:

        stdout, stderr = cli_cmd.communicate()

    tags = str(stdout, encoding='utf-8').splitlines()

    # take the first found by git that's a semver-like tag
    # (since they're in order)
    for tag in tags:
        try:
            return Version(tag)
        except:
            pass

    return None


def tag_datetime(repo_location, tag):
    """Ask the repo for the date the tag was created"""

    with Popen(
            ['git', 'tag', '--list', tag, '--format=%(taggerdate:unix)'],
            stdin=PIPE, stdout=PIPE, stderr=PIPE,
            cwd=os.path.abspath(repo_location),
        ) as cli_cmd:

        stdout, stderr = cli_cmd.communicate()

    if not stdout:
        return None
        
    tag_unix_date = str(stdout, encoding='utf-8').splitlines()[0]

    if not tag_unix_date:
        return None

    return datetime.fromtimestamp(int(tag_unix_date))
from .version import Version
from .git import highest_tagged_git_version

import sys


# try:
current_version = highest_tagged_git_version('.')

if len(sys.argv) == 2:
    target_version = Version(sys.argv[1])
    if current_version in target_version:
        print("Repo is currently ON the target version: repo working on [%s]" % (current_version.release_build))
    elif target_version > current_version:
        print("Repo is currently BEHIND the target: repo working on [%s]" % (current_version.release_build))
    elif target_version < current_version:
        print("Repo is currently AHEAD of the target: repo working on [%s]" % (current_version.release_build))
else:
    print("Currently on %s (Tag: [%s])" % (current_version.release_build, current_version.tag))
# except:
#     print("Can't tell what version we're on, if we're in a git repo.")



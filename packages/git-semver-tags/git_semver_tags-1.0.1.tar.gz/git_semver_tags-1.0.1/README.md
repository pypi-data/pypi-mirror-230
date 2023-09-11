# git-semver-tags
Read and make sense of Git tags following the semver spec

# Quickstart

Install: `pip intall git-semver-tags`

Import and simply pass in strings:

```python
from git_semver_tags import Version
v = Version('1.2.3-alpha+b1234')
```

# Run tests

To verify sanity, run a suite of examples to exercise it by changing to the module's test directory and running 

`./tests/git_semver_tags> python -m unittest discover`
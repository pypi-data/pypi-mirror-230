"""
    Git tag semantic versioning 

    A bit of a simpler, more direct comparitor for parsing and
    sorting git tags that are semver strings.

    The base semver spec doesn't allow for a `v` prefix, nor
    does it deal gracefully with git's "you're X commits ahead 
    of this tag" suffix.

    Based on Semantic Versioning 2 at https://semver.org/
"""
import re, os, sys


__all__ = ['Version']


class Version(object):
    """Parses a string and breaks it into bits useful for comparison.
    """
    
    PRERELEASE_DELIMITER = '.'
    BUILD_DELIMITER = '.'

    # https://regex101.com/r/TY1gRx/11
    SEMVER_PATTERN = re.compile(r'''
    ^ (?:v[.-_]?)? # prefix derpy-ness
      (?P<major>0|[1-9]\d*|[x*])
      # allow break from semver so versions can be shorter
      (?:\.(?P<minor>0|[1-9]\d*|[x*])
        (?:\.(?P<patch>0|[1-9]\d*|[x*]) )?
      )?
    (?:-(?P<prerelease>
     # don't capture the git stuff, if there
     (?! \d+-g[a-f0-9]+ )
     # generic prerelease info
     (?: 0 | [1-9]\d*? | \d*?[a-zA-Z-][0-9a-zA-Z-]*? )
     (?: \. (?: 0 | [1-9]\d*? | \d*?[a-zA-Z-][0-9a-zA-Z-]*? )
     )*
    ))?
    # git describe for a tag
    (?: \+ (?P<buildmetadata>[0-9a-zA-Z-]+?(?:\.[0-9a-zA-Z-]+?)*))?
    (?:-(?P<git>(?P<ahead>\d+)-g(?P<commit>[a-f0-9]+))?)?
    $''', re.I + re.X)



    
    # keep a copy to prevent re-parsing the same values
    _cache = {}
    
    __slots__ = ('major', 'minor', 'patch', 'build', 'prerc', '_raw', '_match_dict')
        
    def __new__(cls, version_string):
        if version_string in cls._cache:
            return cls._cache[version_string]
        else:
            return super(Version, cls).__new__(cls)
    
    
    def __init__(self, version_string=None):
        if not version_string:
            version_string = '*'
        try:
            info = self.SEMVER_PATTERN.match(version_string).groupdict()
        except AttributeError:
            raise ValueError('String given does not match version pattern')
        
        self._raw = version_string
        self._cache[version_string] = self
        
        self._match_dict = info
                
        # allow wildcard matching for inclusion tests
        if info['major'] in ('x', '*'):
            self.major = None
        else:
            self.major = int(info['major'] or 0)
            
        if info['minor'] in ('x', '*'):
            self.minor = None
        elif info['minor'] is None and self.major is None:
            self.minor = None
        else:
            self.minor = int(info['minor'] or 0)
                
        if info['patch'] in ('x', '*'):
            self.patch = None
        elif info['patch'] is None: #and self.minor is None:
            self.patch = None
        else:
            self.patch = int(info['patch'] or 0)
            
        self.prerc = self._break_up(info['prerelease'], delimiter=self.PRERELEASE_DELIMITER)
                
        self.build = self._break_up(info['buildmetadata'], delimiter=self.BUILD_DELIMITER)
        
        
    @property
    def tag(self):
        return self._raw
        
            
    def __contains__(self, other):
        """Check if other falls within our version.

        NOTE: This is _NOT_ a greater than comparison!
            It's a direct match and assumes our version
            is spec'd such that it _can_ contain others.

        None in a value is essentially a wildcard.

        For example, a release candidate would fall under
        its final release, but a later release candidate
        does _not_ contain an earlier one!
        """
        if self.major is None:
            return True
        if self.major != other.major:
            return False
        if self.minor is None:
            return True
        if self.minor != other.minor:
            return False
        if self.patch is None:
            return True
        if self.patch != other.patch:
            return False
        
        # releases are don't have prelease bits,
        # so all other parts the same, a full
        # release contains any candidate
        if self.is_release():
            return True
        return self.prerc == other.prerc
        
    
    # convenience properties

    @property
    def commits_ahead(self):
        """How many commits ahead the current git index is from the tag, if available."""
        return int(self._match_dict['ahead'] or 0) or None
        
    @property
    def commit(self):
        """Commit hash (shortened) of the tag, if available."""
        return self._match_dict['commit']

    @property
    def release(self):
        """Release Version object with no qualifiers"""
        return Version('%d.%d.%d' % self.release_tuple)
    
    @property
    def release_tuple(self):
        """Release 3-tuple"""
        return (self.major, self.minor, self.patch)
    
    @property
    def release_full(self):
        """Release string, including only prerelease, if any"""
        v = '%d.%d.%d' % self.release_tuple
        if self.prerc:
            v += '-' + '.'.join(self.prerc)
        return v
        
    @property
    def release_build(self):
        """Full release string, including build qualifier, if any"""
        v = self.release_full
        if self.build:
            v += '+' + '.'.join(self.build)
        return v


    def is_release(self):
        """Not a release if we're not on it or prerelease qualifiers are included."""
        return not self.prerc and not self.commits_ahead

    def __bool__(self):
        """True if a pure version (no pre-release qualifier)"""
        return self.is_release()
        
    # convenience alias
    __nonzero__ = __bool__
    
    def __len__(self):
        return NotImplemented
        
        
    @property
    def _comparator_tuple(self):
        return self.major, self.minor, self.patch, self.prerc, self.build
    

    def __repr__(self):
        s = '%s.%s.%s' % (self.major, self.minor, self.patch)
        if self.prerc:
            if self.commit:
                s += (' [%s' % self.commit)
                if self.commits_ahead:
                    s += (' (%d ahead)' % self.commits_ahead)
                s += ']'
            else:
                s += ('-%s' % (self.PRERELEASE_DELIMITER.join(str(v) for v in self.prerc),))
        if self.build:
            s += ('(build %s)' % ( self.BUILD_DELIMITER.join(str(v) for v in self.build),))
        return s
    
    
    @staticmethod
    def _break_up(some_string, delimiter='.'):
        """Comparisons should be done piece-wise, not straight alphabetically.
        Pass in a delimiter to break a tuple of the contents.

        Slightly different from just `.split` since it'll attempt to cast ints
        for better numerical comparison.
        """
        if some_string is None:
            return tuple()
        parts = []
        for part in some_string.split(delimiter):
            try:
                parts.append(int(part))
            except ValueError:
                parts.append(part)
        return tuple(parts)
    

    @staticmethod
    def _compare_tuple__gt__(left, right):
        "Compare using the rules from semver (§11.4.1-4)"
        assert isinstance(left, (tuple, list)) or isinstance(right, (tuple, list)), 'Comparison must be between ordered iterables'
        for l,r in zip(left, right):
            if isinstance(l, int):
                if isinstance(r, int): # §11.4.1 (int vs int)
                    if l > r: return True
                    if r > l: return False
                    continue # equiv goes to next part of tuples
                else:
                    return False # §11.4.3 (int < str)
            elif isinstance(l, str):
                if isinstance(r, int):
                    return True # §11.4.3 (str > int)
                elif isinstance(r, str):
                    if l > r:
                        return True
                    continue # equiv goes to next part of tuples
                else:
                    raise NotImplementedError
            else:
                return NotImplementedError
        if len(left) > len(right):
            return True # §11.4.4
        return False
    

    @staticmethod
    def _compare_tuple__lt__(left, right):
        "Compare using the rules from semver (§11.4.1-4)"
        assert isinstance(left, (tuple, list)) or isinstance(right, (tuple, list)), 'Comparison must be between ordered iterables'
        for l,r in zip(left, right):
            if isinstance(l, int):
                if isinstance(r, int): # §11.4.1 (int vs int)
                    if l < r: return True
                    if r < l: return False
                    continue # equiv goes to next part of tuples
                else:
                    return True # §11.4.3 (int < str)
            elif isinstance(l, str):
                if isinstance(r, int):
                    return False # §11.4.3 (str > int)
                elif isinstance(r, str):
                    if l < r:
                        return True
                    continue # equiv goes to next part of tuples
                else:
                    raise NotImplementedError
            else:
                return NotImplementedError
        if len(left) < len(right):
            return True # §11.4.4
        return False
    

    @staticmethod
    def _compare_tuple__eq__(left, right):
        assert isinstance(left, (tuple, list)) or isinstance(right, (tuple, list)), 'Comparison must be between ordered iterables'
        if len(left) != len(right):
            return False
        for l,r in zip(left, right):
            if l != r:
                return False
        else:
            return True
    

    def __gt__(self, other):
        """        
        NOTE: wildcards are considered the base release for comparison
            Thus a wildcard is always less than a specific value.
            And, of course, two wildcards can't be greater than another.
            (The opposite is true for __contains__)
        """
        # coerce for comparison, if needed
        if isinstance(other, str):
            other = Version(other)
        # don't try to make sense of things that, well, don't make sense
        if not isinstance(other, type(self)):
            return NotImplementedError

        # check major
        if self.major is None: # wildcard is less
            if other.major is None: # ... unless both wildcards
                return False
            else:
                return False
        if other.major is None: # anything beats wildcard
            return True
        if self.major < other.major:
            return False
        if self.major > other.major:
            return True

        # check minor
        if self.minor is None: # wildcard is less
            if other.minor is None: # ... unless both wildcards
                return False
            else:
                return False
        if other.minor is None: # anything beats wildcard
            return True
        if self.minor < other.minor:
            return False
        if self.minor > other.minor:
            return True

        # check patch
        if self.patch is None: # wildcard is less
            if other.patch is None: # ... unless both wildcards
                return False
            else:
                return False
        if other.patch is None: # anything beats wildcard
            return True
        if self.patch < other.patch:
            return False
        if self.patch > other.patch:
            return True

        # check pre-release
        # NOTE: this divergese from semver: 
        #       if a commit is ahead, it's ahead _of the version_ it's tagged on
        # (This is part of why this was initially sketched together)
    
        # equivalent prereleases are resovled by which is further ahead
        if self._compare_tuple__eq__(self.prerc, other.prerc):
            # tiebreak on commits ahead
            return (self.commits_ahead or 0) > (other.commits_ahead or 0)
        
        # compare prerelease info directly
        if     self.prerc and     other.prerc:
            return self._compare_tuple__gt__(self.prerc, other.prerc)
        
        # prereleases !> releases
        if     self.prerc and not other.prerc:   
            return False
        
        # releases > prereleases
        if not self.prerc and     other.prerc:
            return True
        
        # trivial case (technically unreachable from __eq__ above)
        if not self.prerc and not other.prerc:
            # tiebreak on commits ahead
            return (self.commits_ahead or 0) > (other.commits_ahead or 0)
                
        # unreachable default
        return NotImplemented


    def __lt__(self, other):
        # coerce for comparison, if needed
        if isinstance(other, str):
            other = Version(other)
        # don't try to make sense of things that, well, don't make sense
        if not isinstance(other, type(self)):
            return NotImplementedError

        # check major
        if self.major is None: # wildcard is less
            if other.major is None: # ... unless both wildcards
                return False
            else:
                return True
        if other.major is None: # anything beats wildcard
            return False
        if self.major < other.major:
            return True
        if self.major > other.major:
            return False

        # check minor
        if self.minor is None: # wildcard is less
            if other.minor is None: # ... unless both wildcards
                return False
            else:
                return True
        if other.minor is None: # anything beats wildcard
            return False
        if self.minor < other.minor:
            return True
        if self.minor > other.minor:
            return False

        # check patch
        if self.patch is None: # wildcard is less
            if other.patch is None: # ... unless both wildcards
                return False
            else:
                return True
        if other.patch is None: # anything beats wildcard
            return False
        if self.patch < other.patch:
            return True
        if self.patch > other.patch:
            return False

        # check pre-release
        # NOTE: this divergese from semver: 
        #       if a commit is ahead, it's ahead _of the version_ it's tagged on
        # (This is part of why this was initially sketched together)
        
        # equivalent prereleases are resovled by which is further ahead
        if self._compare_tuple__eq__(self.prerc, other.prerc):
            # tiebreak on commits ahead
            return (self.commits_ahead or 0) < (other.commits_ahead or 0)
        
        # compare prerelease info directly
        if     self.prerc and     other.prerc:
            return self._compare_tuple__lt__(self.prerc, other.prerc)
        
        # prereleases < releases
        if     self.prerc and not other.prerc:   
            return True
        
        # releases !< prereleases
        if not self.prerc and     other.prerc:
            return False
        
        # trivial case (technically unreachable from __eq__ above)
        if not self.prerc and not other.prerc:
            # tiebreak on commits ahead
            return (self.commits_ahead or 0) < (other.commits_ahead or 0)
                
        # unreachable default
        return NotImplemented


    def __eq__(self, other):
        # coerce for comparison, if needed
        if isinstance(other, str):
            other = Version(other)
        # don't try to make sense of things that, well, don't make sense
        if not isinstance(other, type(self)):
            return NotImplementedError

        # check major
        if self.major != other.major:
            return False

        # check minor
        if self.minor != other.minor:
            return False

        # check patch
        if self.patch != other.patch:
            return False

        # check pre-release... sorta        
        # v1.0.0-2-ga1b2c3 <?> v1.0.0-2-gf3d2 
        #   Even if we're using git describe --tags,
        #   if num ahead is the same but commits are different that's just
        #   diverged history, NOT equivalence
        # Boils down to the same thing: not equal
        
        # equivalent prereleases are resovled by which is further ahead
        if self._compare_tuple__eq__(self.prerc, other.prerc):
            # tiebreak on commits ahead
            return (self.commits_ahead or 0) == (other.commits_ahead or 0)

        # unreachable default
        return NotImplemented

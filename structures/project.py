from typing import List

from .version import Version


class Project:
    def __init__(self, **kwargs):
        self.name = None
        self.url = None
        self.versions: List[Version] = []

        # caller must provide a name or url
        if not ('name' in kwargs or 'url' in kwargs):
            raise Exception('Project must have a name or url.')

        # load all attributes into the project
        for k, val in kwargs.items():
            setattr(self, k, val)

    def get_version(self, **kwargs):
        """Gets a version matching all parameters or returns None."""

        # linear search function; potential for being slow...
        for v in self.versions:
            match = True
            for param, val in kwargs.items():
                if getattr(v, param, None) != val:
                    match = False
                    break
            if match:
                return v

        return None

    def _get_or_add_version(self, **kwargs):
        """Finds a matching version or adds a new one."""
        version = self.get_version(**kwargs)
        if not version:
            version = Version(**kwargs)
            self.versions.append(version)

        return version

    def __repr__(self):
        return 'Project(%s)' % ', '.join([
            '%s=%s' % (a, repr(getattr(self, a)))
            for a in dir(self)
            if getattr(self, a)
               and not a.startswith('__')
               and not callable(getattr(self, a))
        ])

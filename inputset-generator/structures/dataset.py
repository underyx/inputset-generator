from pathlib import Path
from typing import List, Optional
from types import MethodType

from structures.projects import Project


class Dataset:
    def __init__(self, registry: str = None):
        from apis import apis
        from structures.projects import Project, projects
        from structures.versions import Version, versions
        from functions import functions
        from util import get_user_name, get_user_email

        # validate registry name (if provided) and set
        if registry and registry not in apis:
            raise Exception('Invalid registry. Valid types are: %s'
                            % list(apis))
        self.registry = registry

        # set project/version types (defaults to the vanilla classes)
        self.types = {'project': projects.get(registry, Project),
                      'version': versions.get(registry, Version)}

        # register the various transformation functions
        for name, function in functions.items():
            setattr(self, name, MethodType(function, self))

        # a dataset contains projects
        self.projects: List[Project] = []

        # set default dataset metadata
        self.name = None
        self.version = None
        self.description = None
        self.readme = None
        self.author = get_user_name()  # default to git user.name
        self.email = get_user_email()  # default to git user.email

    def load_file(self, path: str, fileargs: str = None) -> None:
        """Uses a file handler to load a dataset from file."""
        from loaders.file import file_loaders

        # check if the path is valid
        if not Path(path).is_file():
            raise Exception('Invalid path; file does not exist.')

        # check if the filetype is valid
        extension = Path(path).suffix
        loader = file_loaders.get(extension, None)
        if not loader:
            raise Exception("Invalid input file type '%s'. Valid types"
                            "are: %s." % (extension, list(file_loaders)))

        # load initial data from the file
        print('Loading %s' % path)
        if fileargs:
            loader().load(self, path, fileargs)
        else:
            loader().load(self, path)

    def load_weblist(self, name: str) -> None:
        """Loads a weblist from the registry."""
        from loaders.weblist import weblist_loaders

        # check if the registry has been set
        if not self.registry:
            raise Exception('Registry has not been set. Valid '
                            'registries are: %s' % str(weblist_loaders))

        # check if the name is valid
        loader = weblist_loaders.get(self.registry, None)
        if not loader:
            raise Exception('Invalid weblist for %s. Valid weblists'
                            'are: %s' % (self.registry, str(weblist_loaders)))

        # load initial data from the weblist
        print("Loading '%s' from %s" % (name, self.registry))
        loader().load(self, name)

    def set_meta(self, name=None, version=None, description=None,
                 readme=None, author=None, email=None):
        """Sets dataset metadata."""
        if not (name or version or description
                or readme or author or email):
            raise Exception('Error setting metadata. Must provide at '
                            'least one of name, version, description, '
                            'readme, author, or email.')

        # override existing data only if the override is not None
        self.name = name or self.name
        self.version = version or self.version
        self.description = description or self.description
        self.readme = readme or self.readme
        self.author = author or self.author
        self.email = email or self.email

    '''
    def load_project_metadata(self) -> None:
        """Downloads all projects' metadata."""
        from registries import mapping

        # check if the registry has been set
        if not self.registry:
            raise Exception('Registry has not been set. Valid '
                            'registries are: %s' % list(mapping))

        for project in self.projects:
            print("Retrieving details of %s" % project)
            self.registry.load_project_metadata(project)

    def load_project_versions(self, historical: str) -> None:
        """Downloads all projects' versions."""
        from registries import mapping

        # check if the registry has been set
        if not self.registry:
            raise Exception('Registry has not been set. Valid '
                            'registries are: %s' % list(mapping))

        for project in self.projects:
            print("Retrieving versions of %s" % project)
            self.registry.load_project_versions(project, historical)
    '''

    '''
    def save(self, path: str = None) -> None:
        # file name is dataset name, if not provided by user
        path = path or (self.name + '.json')

        # convert the dataset to an input set json
        inputset = self.to_inputset()

        # save to disk
        print('Saving results to %s' % path)
        #JsonLoader().save(self, path)

    def to_inputset(self) -> dict:
        """Converts a dataset to an input set json."""

        # check that all necessary meta values have been set
        if not (self.name and self.version):
            # name and version are mandatory
            raise Exception('Dataset name and/or version are missing.')

        # jsonify the dataset's metadata
        d = dict()
        if self.name: d['name'] = self.name
        if self.version: d['version'] = self.version
        if self.description: d['description'] = self.description
        if self.readme: d['readme'] = self.readme
        if self.author: d['author'] = self.author
        if self.email: d['email'] = self.email

        # jsonify the projects & versions
        d['inputs'] = []
        for p in self.projects:
            d['inputs'] += p.to_inputset()

        return d
    '''

    '''
    def find_project(self, **kwargs) -> Optional[Project]:
        """Gets the first project with attributes matching all kwargs."""

        # linear search function; potential for being slow...
        for p in self.projects:
            match = True
            for param, val in kwargs.items():
                if getattr(p, param, None) != val:
                    match = False
                    break
            if match:
                return p

        return None

    def find_or_add_project(self, project_cls, **kwargs) -> Project:
        """Finds a matching project or adds a new one of type Project."""
        project = self.find_project(**kwargs)
        if not project:
            project = project_cls(**kwargs)
            self.projects.append(project)

        return project
    '''

    def __repr__(self):
        return 'Dataset(%s)' % ', '.join([
            '%s=%s' % (a, repr(getattr(self, a)))
            for a in dir(self)
            if getattr(self, a)
               and not a.startswith('__')
               and not callable(getattr(self, a))
        ])

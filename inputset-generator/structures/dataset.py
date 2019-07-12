import json
from typing import List, Optional
from types import MethodType
from pathlib import Path
from dill.source import getsource

from structures.projects import Project, DefaultProject, \
    class_map as projects_map
from structures.versions import DefaultVersion, class_map as versions_map


class Dataset(object):
    def __init__(self, registry: str = None, **kwargs):
        from apis import class_map as apis_list
        from structures import Project
        from functions import function_map
        from util import get_user_name, get_user_email

        # validate registry name (if provided) and set
        if registry and registry not in apis_list:
            raise Exception('Invalid registry. Valid types are: %s'
                            % list(apis_list))
        self.registry = registry

        # set up the api
        api_class = apis_list.get(self.registry, None)
        cache_dir = kwargs.get('cache_dir', None)
        cache_timeout = kwargs.get('cache_timeout', None)
        self.api = None if not api_class \
            else api_class(cache_dir=cache_dir, cache_timeout=cache_timeout)

        # register the various transformation functions
        for name, function in function_map.items():
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
        """Uses a file loader to load an initial dataset from file."""
        from loaders.file import class_map

        # check if the path is valid
        if not Path(path).is_file():
            raise Exception('Invalid path; file does not exist.')

        # check if the filetype is valid
        extension = Path(path).suffix
        loader = class_map.get(extension, None)
        if not loader:
            raise Exception("Invalid input file type '%s'. Valid types"
                            "are: %s." % (extension, list(class_map)))

        # load initial data from the file
        print('Loading %s' % path)
        if fileargs:
            loader().load(self, path, fileargs)
        else:
            loader().load(self, path)

    def load_weblist(self, name: str, nocache: bool = False) -> None:
        """Uses a weblist loader to load an initial dataset from a weblist."""
        from loaders.weblist import class_map

        # check if the registry has been set
        if not self.registry:
            raise Exception('Registry has not been set. Valid '
                            'registries are: %s' % str(class_map))

        # check if the name is valid
        loader = class_map.get(self.registry, None)
        if not loader:
            raise Exception('Invalid weblist for %s. Valid weblists'
                            'are: %s' % (self.registry, str(class_map)))

        # load initial data from the weblist
        print("Loading %s %s" % (self.registry, name))
        loader().load(self, name)

    def get_projects_meta(self, nocache: bool = False) -> None:
        """Gets the metadata for all projects."""
        for p in self.projects:
            self.api.get_project(p, nocache=nocache)

    def get_project_versions(self, historical: str = 'all',
                             nocache: bool = False) -> None:
        """Gets the historical versions for all projects."""
        for p in self.projects:
            self.api.get_versions(p, historical=historical, nocache=nocache)

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

    def save(self, filepath: str = None) -> None:
        # file name is dataset name, if not provided by user
        filepath = filepath or (self.name + '.json')

        # convert the dataset to an input set json
        inputset = self.to_inputset()

        # save to disk
        print('Saving results to %s' % filepath)
        with open(filepath, 'w') as file:
            json.dump(inputset, file, indent=4)

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
            d['inputs'].extend(p.to_inputset())

        return d

    def to_json(self) -> dict:
        """Converts a dataset to a json."""

        # grab dataset attributes
        data = {
            attr: val for attr, val in vars(self).items()
            if attr not in ['api', 'projects']
               and not callable(val)
        }

        # add project (& version) attributes
        data['projects'] = [p.to_json() for p in self.projects]

        return data

    def find_project(self, **kwargs) -> Optional[Project]:
        """Gets the first project with attributes matching all kwargs."""

        # build a temporary project containing the kwargs
        this_p = Project(**kwargs)

        # linear search function for now; potentially quite slow...
        for other_p in self.projects:
            # copy over the other project's uuid lambda funcs so the two
            # projects can be compared (need to rebind the lambda func
            # to this_p instead of other_p--hence the __func__ ref)
            for k, func in other_p.uuids_.items():
                this_p.uuids_[k] = MethodType(func.__func__, this_p)

            if this_p == other_p:
                return other_p

        return None

    def head(self, n: int = 5, details: bool = False):
        """Summarizes the key data of the first n projects."""
        for p in self.projects[:n]:
            project_type = str(type(p).__name__)
            attr_indent = len(project_type) + 5
            val_indent = 11

            # print project uuids
            print('%s(%s' % (
                (' ' * 4) + project_type,
                ('\n' + ' ' * attr_indent).join([
                    '%s = %s' % (
                        a.ljust(val_indent - 3),
                        str(func())) for a, func in p.uuids_.items()
                ])
            ))

            # print versions
            print('%s = [%s])' % (
                (' ' * attr_indent) + 'versions',
                ('\n' + ' ' * (attr_indent + val_indent + 1)).join([
                    repr(v) for v in p.versions
                ])
            ))

    def describe(self, scope: str = 'dataset'):
        """Describes the dataset/project/version structures."""
        '''
        https://stackoverflow.com/questions/9989334/create-nice-column-output-in-python        
        table_data = [
            ['a', 'b', 'c'],
            ['aaaaaaaaaa', 'b', 'c'],
            ['a', 'bbbbbbbbmsk', 'c']
        ]
        for row in table_data:
            print("{: <20} {: <20} {: <20}".format(*row))
        '''

        if scope == 'dataset':
            # describe the dataset
            col_width = 13

            # print the attributes in the following order:
            attrs = ['registry', 'name', 'version',
                     'description', 'readme', 'author', 'email']
            for a in attrs:
                val = getattr(self, a, None)
                print('    %s%s' % (a.ljust(col_width), val))

            # print projects summary info
            print('    projects')
            project_type = projects_map.get(self.registry,
                                            DefaultProject).__name__
            print('    %s%s' % ('    type'.ljust(col_width),
                                'list(%s)' % project_type))
            print('    %s%d' % ('    len'.ljust(col_width),
                                len(self.projects)))

        elif scope in ['project', 'version']:
            # describe a project or version
            obj = self.projects[0]
            if scope == 'version':
                obj = self.projects[0].versions[0]

            # calculate the width of the first columne
            col_width = max([len(a) for a in vars(obj)]) + 2

            # print uuids & meta vars
            for key in ['uuids', 'meta']:
                print('    %s' % key)
                key_dict = getattr(obj, key + '_')
                if len(key_dict) == 0:
                    print('    none')
                for a, func in key_dict.items():
                    # convert the lambda function code to a string
                    func_str = getsource(func).split(': ', 1)[1].strip()
                    print('    %s%s' % (
                        ('    ' + a).ljust(col_width),
                        func_str
                    ))

            # print all the attributes
            special_attrs = ['uuids_', 'meta_', 'versions']
            for a in sorted(vars(obj)):
                if a in special_attrs:
                    continue

                print('    %s%s' % (
                    a.ljust(col_width),
                    type(getattr(obj, a)).__name__
                ))

            if scope == 'project':
                # print versions summary info, if applicable
                print('    versions')
                version_type = versions_map.get(self.registry,
                                                DefaultVersion).__name__
                print('    %s%s' % (
                    '    type'.ljust(col_width),
                    'list(%s)' % version_type
                ))
                print('    %s%d' % (
                    '    len'.ljust(col_width),
                    len(obj.versions)
                ))

    def __repr__(self):
        return 'Dataset(%s' % ', '.join([
            '%s=%s' % (a, repr(getattr(self, a)))
            for a in dir(self)
            if getattr(self, a, None)
               and a is not 'projects'             # ignore projects list
               and not a.startswith('__')          # ignore dunders
               and not callable(getattr(self, a))  # ignore functions
        ]) + ', projects=[%s])' % ('...' if self.projects else '')

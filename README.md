# Input Set Generator

Welcome to Return2Corp's input set generator!

## Installation
To install (pre-official release), download the project's requirements.txt into a folder and navigate to that folder in the terminal. Then:
```
pip install virtualenv
virtualenv venv
source venv/bin/activate (or activate.fish, if you’re using fish)
pip install -r requirements.txt
pip install --index-url https://test.pypi.org/simple/ r2c-isg
```

Then, to run:
```
r2c-isg
```

## Quick Start
Try the following command sequences:

1. Load the top 5,000 pypi projects by downloads in the last 365 days, sort by descending number of downloads, trim to the top 100 most downloaded, download project metadata and all versions, and generate an input set json.

	    load pypi top5kyear
    	sort "desc download_count
	    trim 100
	    get -mv all
    	set-meta -n test -v 1.0
	    export inputset.json

2. Load all npm projects, sample 100, download the latest versions, and generate an input set json.
		
        load npm allbydependents
		sample 100
	    get -v latest
    	set-meta -n test -v 1.0
	    export inputset.json

3. Load a csv containing github urls and commit hashes, get project metadata and the latest versions, generate an input set json of type GitRepoCommit, remove all versions, and generate an input set json of type GitRepo.

    	load --columns "url v.commit" github list_of_github_urls_and_commits.csv
	    get -mv latest
    	set-meta -n test -v 1.0
	    export inputset_1.json
    	trim -v 0
	    export inputset_2.json

## Shell Usage

#### Input/Output

- **load** (OPTIONS) [noreg | github | npm | pypi] [WEBLIST_NAME | FILEPATH.csv]<br>
	Generates a dataset from a weblist or a local file. The following weblists are available:
    - Github: top1kstarred, top1kforked; the top 1,000 most starred or forked repos<br>
    - NPM: allbydependents; **all** packages, sorted from most to fewest dependents count (caution: 1M+ projects... handle with care)<br>
    - Pypi: top5kmonth and top5kyear; the top 5,000 most downloaded projects in the last 30/365 days

	**Options:**<br>
    **-c --columns** "string of col names": A space-separated list of column names in a csv. Overrides default columns (name and version), as well as any headers listed in the file (headers in files begin with a '!'). The CSV reader recognizes the following column keywords: name, url, org, v.commit, v.version. All other columns are read in as project or version attributes.<br>
    Example usage: --headers "name url downloads v.commit v.date".

- **backup** (FILEPATH.p)<br>
	Backs up the dataset to a pickle file (defaults to ./dataset_name.p).

- **restore** FILEPATH.p<br>
	Restores a dataset from a pickle file.

- **import** [noreg | github | npm | pypi] FILEPATH.json<br>
	Builds a dataset from an R2C input set.

- **export** (FILEPATH.json)<br>
	Exports a dataset to an R2C input set (defaults to ./dataset_name.json).

#### Data Acquisition

- **get** (OPTIONS)<br>
	Downloads project and version metadata from Github/NPM/Pypi.

	**Options:**<br>
    **-m --metadata**: Gets metadata for all projects.<br>
    **-v --versions** [all | latest]: Gets historical versions for all projects.

#### Transformation

- **trim** (OPTIONS) N<br>
	Trims the dataset to *n* projects or *n* versions per project.
    
    **Options**<br>
    **-v --versions**: Binary flag; trims on versions instead of projects.

- **sample** (OPTIONS) N<br>
	Samples *n* projects or *n* versions per project.
    
    **Options**<br>
    **-v --versions**: Binary flag; sample versions instead of projects.

- **sort** "[asc, desc] attributes [...]"<br>
	Sorts the projects and versions based on a space-separated string of keywords. Valid keywords are:
    - Any project attributes
    - Any version attributes (prepend "v." to the attribute name)
    - Any uuids (prepend "uuids." to the uuid name
    - Any meta values (prepend "meta." to the meta name
    - The words "asc" and "desc"
    
    All values are sorted in ascending order by default. The first keyword in the string is the primary sort key, the next the secondary, and so on.

    Example: The string "uuids.name meta.url downloads desc v.version_str v.date" would sort the dataset by ascending project name, url, and download count; and descending version string and date (assuming those keys exist).


#### Settings

- **set-meta** (OPTIONS)<br>
	Sets the dataset's metadata.

	**Options:**<br>
	**-n --name** NAME: Input set name. Must be set before the dataset can be exported.<br>
    **-v --version** VERSION: Input set version. Must be set before the dataset can be exported.<br>
    **-d --description** DESCRIPTION: Description string.<br>
    **-r --readme** README: Markdown-formatted readme string.<br>
    **-a --author** AUTHOR: Author name; defaults to git user.name.<br>
    **-e --email** EMAIL: Author email; defaults to git user.email.<br>

- **set-api** (OPTIONS)<br>
	**--cache_dir** CACHE_DIR: The path to the requests cache; defaults to ./.requests_cache.<br>
    **--cache_timeout** DAYS: The number of days before a cached request goes stale.<br>
    **--nocache**: Binary flag; disables request caching for this dataset.<br>
    **--github_pat** GITHUB_PAT: A github personal access token, used to increase the max allowed hourly request rate from 60/hr to 5,000/hr. For instructions on how to obtain a token, see: [https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line](https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line). 

#### Visualization

- **show**<br>
	Converts the dataset to a json file and loads it in the system's native json viewer.

## Python Project

You can also import the package into your own project. Just import the Dataset structure, initialize it, and go to town!

```
from r2c_isg.structures import Dataset

ds = Dataset.import_inputset(
    'file.csv' ~or~ 'weblist_name',
    registry='github' ~or~ 'npm' ~or~ 'pypi',
    cache_dir=path/to/cache/dir,               # optional; overrides ./.requests_cache
    cache_timeout=int(days_in_cache),          # optional; overrides 1 week cache timeout
    nocache=True,                              # optional; disables caching
    github_pat=your_github_pat                 # optional; personal access token for github api
)

ds.get_projects_meta()

ds.get_project_versions(historical='all' ~or~ 'latest')

ds.trim(
    n,
    on_versions=True	# optional; defaults to False
)

ds.sample(
    n,
    on_versions=True	# optional; defaults to False
)

ds.sort('string of sort parameters')

ds.update(**{'name': 'you_dataset_name', 'version': 'your_dataset_version'})

ds.export_inputset('your_inputset.json')
```
import requests

from structures import Dataset
from loaders import Loader


class PypiLoader(Loader):
    def __init__(self):
        self.weblists = {
            'top5kmonth': {
                'getter': self._get_top5kmonth,
                'parser': self._parse_hugovk
            },
            'top5kyear': {
                'getter': self._get_top5kyear,
                'parser': self._parse_hugovk
            }
        }

    def load(self, ds: Dataset, name: str, **_) -> None:
        # load the data
        data = self.weblists[name]['getter']()

        # parse the data
        self.weblists[name]['parser'](ds, data)

    @staticmethod
    def _get_top5kyear() -> list:
        url = 'https://hugovk.github.io/top-pypi-packages/' \
              'top-pypi-packages-365-days.json'
        return requests.get(url).json()['rows']

    @staticmethod
    def _get_top5kmonth() -> list:
        url = 'https://hugovk.github.io/top-pypi-packages/' \
              'top-pypi-packages-30-days.json'
        return requests.get(url).json()['rows']

    @staticmethod
    def _parse_hugovk(ds: Dataset, data: list) -> None:
        project_cls = ds.types['project']
        ds.projects = [project_cls(package_name=d['project'],
                                   downloads=d['download_count'])
                       for d in data]

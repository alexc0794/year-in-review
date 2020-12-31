import csv
import json
import os
from abc import ABC
from dataclasses import dataclass
from typing import Dict, Any, Optional, List


class Parser(ABC):
    year: Optional[int]
    data: Dict[str, Any]

    def __init__(self, year: Optional[int] = None) -> None:
        self.year = year


class JsonParser(Parser):
    def __init__(self, relative_path: str, year: Optional[int] = None) -> None:
        super().__init__(year=year)
        filepath = '{0}/{1}'.format(os.getcwd(), relative_path)

        try:
            with open(filepath) as file:
                self.data = json.load(file)
        except:
            print('There was a problem loading {0}'.format(filepath))
            raise


class MultiJsonParser(Parser):
    def __init__(self, relative_path_to_directory: str, filename_prefix: str, year: Optional[int] = None) -> None:
        super().__init__(year=year)
        directory_path = '{0}/{1}'.format(os.getcwd(), relative_path_to_directory)
        data = []
        for filename in os.listdir(directory_path):
            if filename.startswith(filename_prefix) and filename.endswith('.json'):
                filepath = '{0}/{1}'.format(directory_path, filename)
                try:
                    with open(filepath) as file:
                        data += json.load(file)
                except:
                    print('There was a problem loading {0}'.format(filepath))
                    raise
        self.data = data


class CsvParser(Parser):
    columns: List[str]

    def __init__(self, relative_path: str, year: Optional[int] = None) -> None:
        super().__init__(year=year)
        filepath = '{0}/{1}'.format(os.getcwd(), relative_path)

        try:
            with open(filepath) as file:
                data = list(csv.reader(file, delimiter=','))
                self.columns = data[0]
                self.data = data[1:]
        except:
            print('There was a problem loading {0}'.format(filepath))
            raise

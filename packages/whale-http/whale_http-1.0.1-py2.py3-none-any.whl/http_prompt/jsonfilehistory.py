from pathlib import Path
import datetime
import json
import csv
import yaml

from prompt_toolkit.history import History


def get_data(filename):
    data = []
    with open(filename, 'r') as f:
        data.extend(line.replace('\n', '') for line in f if line.replace('\n', '') != '')

    return data


def get_data_csv(filename):
    data = []
    with open(filename, 'r') as f:
        csv_reader = csv.reader(f)
        data.extend(csv_reader)
    return data


def get_data_json(filename):
    data = []
    with open(filename, 'r') as f:
        dict_data = json.loads(f.read())
        data.extend(tuple(item.values()) for item in dict_data)
    return data


def get_data_yaml(filename):
    """加载yaml配置文件

    Args:
        filename (string): name of the file

    Returns:
        list: list of configs
    """
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        data.append(yaml.load(f, Loader=yaml.FullLoader))
    return data


class JsonFileHistory(History):
    """
    :class:`.History` class that stores all json strings in a file.
    """

    def __init__(self, filename):
        self.filename = filename
        super().__init__()

    def load_history_strings(self):
        strings = []
        # lines = []

        # def add():
        #     if lines:
        #         # Join and drop trailing newline.
        #         string = ''.join(lines)[:-1]

        #         strings.append(string)

        if Path(self.filename).exists():
            hisdata = get_data_yaml(self.filename)
            for item in hisdata[0]['steps']:
                strings.extend((item['name'], item['method'], item['apipath']))
                # with open(self.filename, 'rb') as f:
                #     for line in f:
                #         line = line.decode('utf-8')

                #         if line.startswith('+'):
                #             lines.append(line[1:])
                #         else:
                #             add()
                #             lines = []

                #     add()

        # Reverse the order, because newest items have to go first.
        return reversed(strings)

    def store_string(self, string):
        # Save to file.
        with open(self.filename, 'ab') as f:

            def write(t):
                f.write(t.encode('utf-8'))

            write('\n# %s\n' % datetime.datetime.now())
            for line in string.split('\n'):
                write('+%s\n' % line)

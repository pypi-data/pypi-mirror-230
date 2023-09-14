import csv
import os

list_path = os.path.join(os.path.dirname(__file__), "list.csv")


class TelemetryAllowList(object):
    def __init__(self):
        self._data = set()
        with open(list_path, "r") as fd:
            allow_list_reader = csv.DictReader(fd)
            for row in allow_list_reader:
                self._data.add(row["appid"])

    def __contains__(self, value):
        return value in self._data


telemetry_allow_list = TelemetryAllowList()

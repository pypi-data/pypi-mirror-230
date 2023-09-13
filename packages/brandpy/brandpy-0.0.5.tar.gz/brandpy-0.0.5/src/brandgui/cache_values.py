import os.path
import json


class CacheValues:
    def __init__(self, in_cache_file):
        self.file_path = in_cache_file
        self.values = {}
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as cache_file:
                self.values = json.load(cache_file)
        else:
            self.values = {}

    def save(self):
        with open(self.file_path, 'w') as cache_file:
            json.dump(self.values, cache_file)

    def update_values(self, in_values):
        for k in self.values:
            self.set_value(k, in_values[k])

    def set_value(self, in_key, in_value):
        self.values[in_key] = in_value

    def get_value(self, in_key, in_default_value=""):
        return self.values[in_key] if in_key in self.values else in_default_value


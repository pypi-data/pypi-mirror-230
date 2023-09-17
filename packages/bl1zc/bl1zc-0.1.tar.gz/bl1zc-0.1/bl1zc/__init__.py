# BL1ZCreate (bl1zc)
class packages:
    def openfromlist(list):
        import importlib
        for pack in list:
            importlib.import_module(pack)
    def installfromlist(list):
        import os
        for pack in list:
            os.system(f"pip install {pack}")
class config:
    class ConfigFile:
        def __init__(self, filename):
            self.filename = filename
            self.data = {}
            self.load()

        def load(self):
            try:
                with open(self.filename, 'r') as file:
                    for line in file:
                        key, value = line.strip().split(': ', 1)
                        self.data[key] = value
            except FileNotFoundError:
                print(f"File '{self.filename}' not found.")
            except Exception as e:
                print(f"An error occurred while reading '{self.filename}': {str(e)}")
                print("Must be a .bl1c file")

        def getValue(self, key):
            return self.data.get(key, None)

    def readFile(filename):
        return config.ConfigFile(filename)
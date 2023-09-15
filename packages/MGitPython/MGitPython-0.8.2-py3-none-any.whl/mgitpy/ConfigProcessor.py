import yaml
from jinja2 import Environment, BaseLoader
import os


class ConfigProcessor(object):

    def __init__(self, dir: str = '.'):
        self.__dir = dir
        self.__config = {}
        self.__config['repos'] = []
        filename = os.path.join(dir, "mgit.yaml")
        if (os.path.isfile(filename)):
            self.load_config_file(filename)
        else:
            self.generate_config()

    def set_config(self, config):
        self.__config = config

    def get_config(self):
        return self.__config

    def get_dir(self):
        return self.__dir

    def get_repos(self):
        return self.__config['repos']

    def load_raw_config_file(self, filename):
        with open(filename, "r") as stream:
            self.set_config(yaml.safe_load(stream))

    def process_raw_config_file(self):
        if (not self.__config.get('repos')):
            self.__config['repos'] = []
        if (not self.__config.get('baseUrl')):
            self.__config['baseUrl'] = ''
        if (not self.__config.get('dir')):
            self.__config['dir'] = ''
        if (self.__config['dir'] != ''):
            self.__config['dir'] = self.__config['dir'].rstrip('/') + '/'
        for item in self.__config['repos']:
            if (item.get('dir') == None):
                item['dir'] = self.__config['dir']
            if (item.get('url') == None):
                rtemplate = Environment(loader=BaseLoader).from_string(self.__config['baseUrl'])
                item['url'] = rtemplate.render(item)
            if (item.get('tags') == None):
                item['tags'] = []
            if (not 'all' in item['tags']):
                item['tags'].append('all')

    def load_config_file(self, filename):
        self.load_raw_config_file(filename)
        self.process_raw_config_file()

    def generate_config(self):
        self.__config['repos'] = []
        for file in os.listdir(self.__dir):
            current = os.path.join(self.__dir, file)
            current_dot_git = os.path.join(current, '.git')
            if (os.path.isdir(current) and os.path.isdir(current_dot_git)):
                item = {}
                item['name'] = file
                item['dir'] = self.__dir
                item['tags'] = ['all']
                self.__config['repos'].append(item)
        self.__config['repos'] = sorted(self.__config['repos'], key=lambda x: x['name'])
        self.process_raw_config_file()

    def get_config_yaml(self):
        return yaml.dump(self.__config)

    def save_config_as_yaml(self, filename):
        with open(filename, "w") as text_file:
            text_file.write(self.get_config_yaml())

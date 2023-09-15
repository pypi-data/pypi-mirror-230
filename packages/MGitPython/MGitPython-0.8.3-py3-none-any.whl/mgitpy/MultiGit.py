import subprocess
import pprint
import os
import ConfigProcessor


class MultiGit(object):
    """
    MultiGit - processor for multiple git repos
    """

    def __init__(self, dir: str = '.'):
        self.__configProcessor = ConfigProcessor.ConfigProcessor(dir)

    def __run_commands__(self, commands, tag: str = 'all'):
        for item in self.__configProcessor.get_repos():
            if (tag in item['tags']):
                print("========================================")
                print(f"REPO: {item['name']}")
                for command in commands:
                    process = subprocess.run(command, cwd=os.path.join(item['dir'], item['name']), capture_output=True)
                    print(process.stdout.decode())

    def debug(self):
        """
        debug command
        """
        pprint.pprint(self.__configProcessor.get_config())

    def dump_config(self, filename: str = 'mgit.yaml'):
        """
        dump_config command
        """
        tmp_filename = os.path.join(self.__configProcessor.get_dir(), filename)
        self.__configProcessor.save_config_as_yaml(tmp_filename)

    def version(self):
        """
        version command
        """
        print('mgit ver. 0.8.3')

    def status(self, params: str = '-sb', tag: str = 'all'):
        """
        git status command
        :param params: command parameters
        :param tag: tag to filter repos
        """
        self.__run_commands__([
            ["git", "status", params]
        ], tag)

    def describe(self, params: str = '--tags', tag: str = 'all'):
        """
        git describe command
        :param params: command parameters
        :param tag: tag to filter repos
        """
        self.__run_commands__([
            ["git", "describe", params]
        ], tag)

    def checkout(self, params: str = 'master', tag: str = 'all'):
        """
        git checkout command
        :param params: command parameters
        :param tag: tag to filter repos
        """
        self.__run_commands__([
            ["git", "checkout", params]
        ], tag)

    def git(self, params: str = '', tag: str = 'all'):
        """
        generic git command
        :param params: command parameters
        :param tag: tag to filter repos
        """
        parts = params.split(' ')
        parts.insert(0, 'git')
        self.__run_commands__([
            parts
        ], tag)

    def info(self, tag: str = 'all'):
        """
        git status, git describe commands
        :param tag: tag to filter repos
        """
        self.__run_commands__([
            ["git", "status", "-sb"],
            ["git", "rev-parse", "--short=8", "HEAD"],
            ["git", "describe", "--tags"],
        ], tag)

    def update(self, tag: str = 'all'):
        """
        git update command
        :param tag: tag to filter repos
        """
        self.__run_commands__([
            ["git", "fetch"],
            ["git", "reset", "--hard"],
            ["git", "clean", "-df"],
            ["git", "rebase"],
        ], tag)

    def cleanup(self, tag: str = 'all'):
        """
        git cleanup command
        :param tag: tag to filter repos
        """
        self.__run_commands__([
            ["git", "fetch", "--prune"],
            ["git", "reflog", "expire", "--all", "--expire=now"],
            ["git", "prune"],
            ["git", "fsck", "--unreachable"],
            ["git", "gc"],
        ], tag)

    def clone(self, tag: str = 'all'):
        """
        git clone command
        :param tag: tag to filter repos
        """
        for item in self.__config['repos']:
            if (tag in item['tags']):
                print("========================================")
                print(f"REPO: {item['name']}")
                process = subprocess.run(["git", "clone", f"{item['url']}"], cwd=f"{item['dir']}")

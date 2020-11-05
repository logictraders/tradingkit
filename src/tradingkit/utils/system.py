import os
import pathlib
import pkgutil
from pathlib import Path

import dotenv


class System:

    @staticmethod
    def get_data_dir():
        APPNAME = "br"
        import sys
        from os import path, environ
        if sys.platform == 'darwin':
            from AppKit import NSSearchPathForDirectoriesInDomains
            # http://developer.apple.com/DOCUMENTATION/Cocoa/Reference/Foundation/Miscellaneous/Foundation_Functions/Reference/reference.html#//apple_ref/c/func/NSSearchPathForDirectoriesInDomains
            # NSApplicationSupportDirectory = 14
            # NSUserDomainMask = 1
            # True for expanding the tilde into a fully qualified path
            appdata = path.join(NSSearchPathForDirectoriesInDomains(14, 1, True)[0], APPNAME)
        elif sys.platform == 'win32':
            appdata = path.join(environ['APPDATA'], APPNAME)
        else:
            appdata = path.expanduser(path.join("~", "." + APPNAME))
        return appdata

    @staticmethod
    def get_root_pkg():
        return __package__.split('.')[0]

    @staticmethod
    def read_file(path):
        return pkgutil.get_data(System.get_root_pkg(), path)

    @staticmethod
    def get_cache_dir():
        return System.get_subpath(['cache'])

    @staticmethod
    def get_import_dir():
        return System.get_subpath(['data', 'imported'])

    @staticmethod
    def get_subpath(subpath: list):
        full_path = [System.get_data_dir()] + subpath
        path = os.path.sep.join(full_path)
        if not os.path.exists(path):
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def load_env(env_dir='.', environment='dev'):
        os.environ['TK_ENV'] = environment
        env = Path(env_dir) / ('.env')
        env_local = Path(env_dir) / ('.env.local')
        env_env = Path(env_dir) / ('.env.%s' % environment)
        env_env_local = Path(env_dir) / ('.env.%s.local' % environment)
        # **.local has precedence, and .env.<env> over .env
        dotenv.load_dotenv(dotenv_path=env_env_local)
        dotenv.load_dotenv(dotenv_path=env_local)
        dotenv.load_dotenv(dotenv_path=env_env)
        dotenv.load_dotenv(dotenv_path=env)

import importlib
import os
import re

from tradingkit.utils.injector import Injector


class ConfigInjector(Injector):

    var_processors = {
        "int": lambda x: int(x),
        "str": lambda x: str(x),
        "float": lambda x: float(x)
    }

    def __init__(self, config):
        self.config = config
        self.cache = {}

    def inject(self, key, type=None):
        if key in self.cache:
            return self.cache[key]
        elif key in self.config:
            instance = self.inject_config(self.config[key])
            if instance is None:
                raise ValueError("Injection %s not defined, please check configs" % key)
            if type and not isinstance(instance, type):
                raise ValueError("Injection %s(%s) not matching with %s" % (key, instance.__class__, str(type)))
            self.cache[key] = instance
            return instance
        else:
            return None

    def inject_config(self, config):
        if isinstance(config, dict):
            if 'class' in config:
                element_class = ConfigInjector.find_class(config)
                if 'arguments' in config:
                    arguments_config = config['arguments']
                    arguments = self.inject_config(arguments_config)
                    if isinstance(arguments, dict):
                        instance = element_class(**arguments)
                    elif isinstance(arguments, list):
                        instance = element_class(*arguments)
                    else:
                        raise TypeError("Invalid arguments type, it must be list or dict")
                else:
                    instance = element_class()

                if 'calls' in config:
                    calls = config['calls']
                    if not isinstance(calls, dict):
                        raise TypeError("calls must be a dict")
                    for method_name in calls:
                        method = getattr(instance, method_name)
                        arguments_config = calls[method_name]
                        arguments = self.inject_config(arguments_config)
                        if isinstance(arguments, dict):
                            method(**arguments)
                        elif isinstance(arguments, list):
                            method(*arguments)
                        else:
                            raise TypeError("Invalid call arguments type, it must be list or dict")
                return instance

            else:
                return {el: self.inject_config(config[el]) for el in config}
        elif isinstance(config, list):
            return [self.inject_config(el) for el in config]
        elif isinstance(config, str):
            if config[0] == '@':
                return self.inject(config[1:])
            else:
                return ConfigInjector.replace_env(config)
        return config

    @staticmethod
    def find_class(spec: dict):
        spec_split = spec['class'].split(".")
        ref_module_str, ref_class_str = ".".join(spec_split[:-1]), spec_split[-1]
        ref_module = importlib.import_module(ref_module_str)
        return getattr(ref_module, ref_class_str)

    @staticmethod
    def replace_env(env_ref: str):
        matches = re.match("%env\(((int|str|float):)?([A-Za-z_][A-Za-z0-9_]*)(:(.*))?\)%", env_ref)
        if matches:
            if matches.group(2):
                processor = ConfigInjector.var_processors[matches.group(2)]
            else:
                processor = ConfigInjector.var_processors['str']

            var = matches.group(3)
            if var in os.environ:
                return processor(os.environ[var])
            elif matches.group(5):
                return processor(matches.group(5))
            else:
                raise KeyError("Undefined ENV var '%s'" % var)

        return env_ref

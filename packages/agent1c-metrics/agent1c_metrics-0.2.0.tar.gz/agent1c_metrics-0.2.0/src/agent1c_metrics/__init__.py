from importlib import resources
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

__settings_default = load(resources.read_text("agent1c_metrics", "config.yaml"),Loader=Loader)
__settings_filename = "agent1c_metrics_config.yaml"

with open(__settings_filename,"w+") as settings_file:
    settings = load(settings_file.read(),Loader=Loader)
    if not settings:
        settings = __settings_default
        settings_file.write(dump(settings))

# Version of the package
__version__ = "0.2.0"

#settings = {'folders':['c:\\Program Files\\1cv8\\srvinfo\\reg_1541']}

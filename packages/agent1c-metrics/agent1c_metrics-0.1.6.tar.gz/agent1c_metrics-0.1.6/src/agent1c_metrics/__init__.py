from importlib import resources
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

settings = load(resources.read_text("agent1c_metrics", "config.yaml"),Loader=Loader)

# Version of the package
__version__ = "0.1.6"

#settings = {'folders':['c:\\Program Files\\1cv8\\srvinfo\\reg_1541']}

import subprocess, os
import json
import yaml
from yaml import CSafeLoader
from yaml import SafeLoader



API_KEY = "DummyKeyAIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe Detect Me" #NOSONAR

def test_yaml_load():
    ystr = yaml.dump({'a': 1, 'b': 2, 'c': 3})
    y = yaml.load(ystr, Loader=yaml.SafeLoader) #NOSONAR
    yaml.dump(y)
    try:
        y = yaml.load(ystr, Loader=yaml.CSafeLoader)
    except AttributeError:
        # CSafeLoader only exists if you build yaml with LibYAML
        y = yaml.load(ystr, Loader=yaml.SafeLoader)


def test_json_load():
    # no issue should be found
    j = json.loads("{}") #NOSONAR

yaml.load("{}", Loader=yaml.Loader)

# no issue should be found
yaml.load("{}", Loader=SafeLoader)
yaml.load("{}", Loader=yaml.SafeLoader)
yaml.load("{}", Loader=CSafeLoader)
yaml.load("{}", Loader=yaml.CSafeLoader)


print("Hello World")


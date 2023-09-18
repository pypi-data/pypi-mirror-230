# The function yaml format str and return a dict object
import json
import yaml


def load_json(json_str):
    return json.loads(json_str)


def load_yaml(yaml_str):
    return yaml.safe_load(yaml_str)


def as_json(m, indent=None):
    return json.dumps(m, indent=indent)


def as_yaml(m):
    return yaml.dump(m)

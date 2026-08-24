import yaml
from jsonschema import validate
from jsonschema.exceptions import ValidationError


class PluginValidator:

    def validate_yaml_syntax(self):
        pass

    def validate_plugin_format(self):
        pass

    def validate_plugin_values(self):
        pass

schema = {
    "type": "object",
    "required": ["name", "version", "enabled", "servers"],
    "properties": {
        "name": {"type": "string"},
        "version": {"type": "integer"},
        "enabled": {"type": "boolean"},
        "servers": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["host", "port"],
                "properties": {
                    "host": {"type": "string"},
                    "port": {"type": "integer"}
                },
                "additionalProperties": False
            }
        }
    },
    "additionalProperties": False
}


try:
    with open("config.yaml", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    validate(data, schema)

    print("YAML is valid")

except yaml.YAMLError:
    print("Invalid YAML syntax")

except ValidationError as e:
    print(f"Invalid YAML structure: {e.message}")


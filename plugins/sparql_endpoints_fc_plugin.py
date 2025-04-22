from flask import Blueprint

# Create a blueprint instance
plugin_blueprint = Blueprint("plugin_blueprint", __name__)


@plugin_blueprint.route("/plugin-endpoint")
def plugin_function():
    return "This is a plugin response."

import os
import shutil
import tempfile
import unittest

from metrics.FAIRMetricsFactory import FAIRMetricsFactory
from modules.evaluator.metric import Metric
from modules.plugin.loader import PluginLoader
from modules.plugin.validator import PluginValidator

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")
SCHEMA_DIR = os.path.join(ROOT_DIR, "modules", "plugin") + os.sep
DEFAULT_PLUGIN = os.path.join(ROOT_DIR, "plugins", "default.yaml")


class PluginLoaderTestCase(unittest.TestCase):
    def setUp(self):
        self.plugin_dir = tempfile.mkdtemp() + os.sep
        shutil.copy(DEFAULT_PLUGIN, self.plugin_dir)

    def tearDown(self):
        shutil.rmtree(self.plugin_dir)

    def test_skips_directories_and_non_yaml_files(self):
        # Regression: a plugins/__pycache__ directory crashed the loader.
        os.mkdir(os.path.join(self.plugin_dir, "__pycache__"))
        with open(os.path.join(self.plugin_dir, "README.md"), "w") as f:
            f.write("not a plugin")

        validator = PluginValidator(
            plugin_directory=self.plugin_dir, plugin_schema_directory=SCHEMA_DIR
        )
        self.assertEqual(validator.list_plugin_files(), ["default.yaml"])

        plugins = PluginLoader(
            plugin_directory=self.plugin_dir, plugin_schema_directory=SCHEMA_DIR
        ).load()
        self.assertEqual(len(plugins), 1)

    def test_exits_when_no_yaml_plugin_is_present(self):
        os.remove(os.path.join(self.plugin_dir, "default.yaml"))
        os.mkdir(os.path.join(self.plugin_dir, "__pycache__"))

        validator = PluginValidator(
            plugin_directory=self.plugin_dir, plugin_schema_directory=SCHEMA_DIR
        )
        with self.assertRaises(SystemExit):
            validator.verify_plugin_presence()


class PluginRecommendationsTestCase(unittest.TestCase):
    def test_plugin_recommendations_are_set_on_metrics(self):
        # Regression: the factory assigned a misspelled `recommentations`
        # attribute, so metrics never received the plugin recommendations.
        recommendations = {"weak": "plugin weak reco", "strong": "plugin strong reco"}
        plugin_metric = Metric(
            "F1B", "Persistent IDs", "Findability", "desc", recommendations
        )

        fc_metrics = FAIRMetricsFactory.get_FC_metrics([plugin_metric])

        f1b = fc_metrics["Persistent IDs"]
        self.assertEqual(f1b.recommendations, recommendations)
        self.assertFalse(hasattr(f1b, "recommentations"))

    def test_metrics_without_plugin_entry_keep_empty_recommendations(self):
        fc_metrics = FAIRMetricsFactory.get_FC_metrics([])

        for metric in fc_metrics.values():
            self.assertEqual(metric.recommendations, {})

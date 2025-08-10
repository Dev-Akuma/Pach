# core/plugin_manager.py

import importlib
import os
import sys

class PluginManager:
    def __init__(self, command_registry):
        self.command_registry = command_registry
        self.plugins = []

    def load_plugins(self, plugins_dir='plugins'):
        sys.path.insert(0, plugins_dir)
        for folder in os.listdir(plugins_dir):
            folder_path = os.path.join(plugins_dir, folder)
            if os.path.isdir(folder_path):
                try:
                    plugin_module = importlib.import_module(f'{folder}.plugin')
                    plugin = plugin_module.Plugin(self.command_registry)
                    plugin.register()
                    self.plugins.append(plugin)
                    print(f"Loaded plugin: {folder}")
                except Exception as e:
                    print(f"Failed to load plugin {folder}: {e}")
        sys.path.pop(0)

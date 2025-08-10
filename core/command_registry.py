# core/command_registry.py

class CommandRegistry:
    def __init__(self):
        self._commands = {}

    def register_command(self, name, handler):
        self._commands[name.lower()] = handler

    def get_command(self, name):
        return self._commands.get(name.lower())

    def all_commands(self):
        return list(self._commands.keys())

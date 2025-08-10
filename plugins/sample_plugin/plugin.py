# plugins/sample_plugin/plugin.py

class Plugin:
    def __init__(self, command_registry):
        self.command_registry = command_registry

    def register(self):
        self.command_registry.register_command('hello', self.cmd_hello)

    def cmd_hello(self, args):
        print(f"Hello from sample plugin! Args: {args}")

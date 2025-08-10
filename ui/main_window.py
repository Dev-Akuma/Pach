# ui/main_window.py

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton
from ui.editor import ScriptEditor
from ui.terminal import DebugTerminal
from core.parser import Parser

class MainWindow(QMainWindow):
    def __init__(self, executor, plugin_manager):
        super().__init__()
        self.setWindowTitle("Automation Scripting Tool")

        self.executor = executor
        self.plugin_manager = plugin_manager
        self.parser = Parser()

        # Define keywords & apps for highlighting and autocomplete
        keywords = ['open', 'type', 'wait', 'close', 'hello']  # add plugin commands here
        applications = ['notepad', 'calculator']

        self.editor = ScriptEditor(keywords=keywords, applications=applications)
        self.terminal = DebugTerminal()
        self.run_button = QPushButton("Run Script")

        layout = QVBoxLayout()
        layout.addWidget(self.editor)
        layout.addWidget(self.run_button)
        layout.addWidget(self.terminal)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.run_button.clicked.connect(self.run_script)

        # Bind logger for executor
        self.executor.logger = self.terminal

        # Register core commands
        self.register_core_commands()

        self.is_running = False  # Flag to prevent multiple runs

    def register_core_commands(self):
        self.executor.registry.register_command('open', self.executor.cmd_open)
        self.executor.registry.register_command('wait', self.executor.cmd_wait)
        self.executor.registry.register_command('close', self.executor.cmd_close)
        self.executor.registry.register_command('type', self.executor.cmd_type)

    def run_script(self):
        if self.is_running:
            self.terminal.log("Script is already running. Please wait.")
            return

        self.is_running = True
        self.run_button.setEnabled(False)
        self.terminal.log("Starting script execution...\n")

        try:
            script = self.editor.toPlainText()
            commands = self.parser.parse_script(script)
            for cmd, args in commands:
                self.terminal.log(f"> {cmd} {args}")
                try:
                    self.executor.execute(cmd, args)
                except Exception as e:
                    self.terminal.log(f"Error executing command '{cmd}': {e}")
            self.terminal.log("\nScript execution finished.")
        finally:
            self.is_running = False
            self.run_button.setEnabled(True)

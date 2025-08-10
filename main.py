# main.py

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QPlainTextEdit, QCompleter, QWidget, QTextEdit
from core.command_registry import CommandRegistry
from core.executor import Executor
from core.plugin_manager import PluginManager
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    command_registry = CommandRegistry()
    executor = Executor(command_registry, logger=None)  # logger set later
    plugin_manager = PluginManager(command_registry)

    # Load plugins (optional)
    plugin_manager.load_plugins()

    window = MainWindow(executor, plugin_manager)
    window.resize(700, 600)
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

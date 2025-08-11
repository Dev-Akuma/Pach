from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSplitter,
    QTreeView, QFileSystemModel, QAction, QMenuBar, QFileDialog, QMessageBox,
    QShortcut
)
from PyQt5.QtGui import QKeySequence, QCursor
from PyQt5.QtCore import Qt, QDir, QTimer, QSettings, QFileInfo

from ui.editor import ScriptEditor
from ui.terminal import DebugTerminal
from core.parser import Parser


class MainWindow(QMainWindow):
    def __init__(self, executor, plugin_manager):
        super().__init__()

        self.settings = QSettings("YourCompany", "AutomationScriptingTool")
        self.last_opened_folder = self.settings.value("last_opened_folder", QDir.homePath())

        # File Explorer setup
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(self.last_opened_folder)  # Use last opened folder here
        self.file_explorer = QTreeView()
        self.file_explorer.setModel(self.file_model)
        self.file_explorer.setRootIndex(self.file_model.index(self.last_opened_folder))
        self.file_explorer.setColumnWidth(0, 250)
        self.file_explorer.doubleClicked.connect(self.open_file_from_explorer)

        self.setWindowTitle("Automation Scripting Tool")

        self.executor = executor
        self.plugin_manager = plugin_manager
        self.parser = Parser()

        keywords = ['open', 'type', 'wait', 'close', 'hello']  # add plugin commands here
        applications = ['notepad', 'calculator']

        self.editor = ScriptEditor(keywords=keywords, applications=applications)
        self.terminal = DebugTerminal()

        # Left splitter: vertical - terminal + file explorer
        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.addWidget(self.terminal)

        self.terminal.setStyleSheet("""
            background-color: #292929;
            color: white;
            font-family: Consolas, "Courier New", monospace;
            font-size: 9pt;
        """)

        left_splitter.addWidget(self.file_explorer)
        left_splitter.setSizes([300, 200])

        # Main splitter: horizontal - left splitter + editor
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(self.editor)
        main_splitter.setStretchFactor(1, 1)

        container = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(main_splitter)
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Menu bar
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        new_action = QAction("New File", self)
        open_file_action = QAction("Open File", self)
        open_folder_action = QAction("Open Folder", self)
        recents_action = QAction("Recents", self)
        save_action = QAction("Save", self)
        save_as_action = QAction("Save As", self)
        exit_action = QAction("Exit", self)

        file_menu.addActions([
            new_action, open_file_action, open_folder_action,
            recents_action, save_action, save_as_action,
            exit_action
        ])

        new_action.triggered.connect(self.new_file)
        open_file_action.triggered.connect(self.open_file_dialog)
        open_folder_action.triggered.connect(self.open_folder_dialog)
        save_action.triggered.connect(self.save_file)
        save_as_action.triggered.connect(self.save_file_as)
        exit_action.triggered.connect(self.close)

        # Edit menu (empty for now)
        menu_bar.addMenu("Edit")

        # View menu (empty for now)
        menu_bar.addMenu("View")

        # Run menu
        run_menu = menu_bar.addMenu("Run")
        run_action = QAction("Run Pach File", self)
        run_menu.addAction(run_action)
        run_action.triggered.connect(self.run_script)

        # Shortcut Ctrl+Enter to run script
        run_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        run_shortcut.activated.connect(self.run_script)

        # Shortcut Ctrl+S to save file
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_file)

        self.executor.logger = self.terminal

        self.register_core_commands()

        self.is_running = False
        self.abort_requested = False

        # Timer to check for mouse position for failsafe
        self.failsafe_timer = QTimer()
        self.failsafe_timer.setInterval(100)  # Check every 100ms
        self.failsafe_timer.timeout.connect(self.check_mouse_failsafe)

        # Track current open file path for saving
        self.current_file_path = None

    def register_core_commands(self):
        self.executor.registry.register_command('open', self.executor.cmd_open)
        self.executor.registry.register_command('wait', self.executor.cmd_wait)
        self.executor.registry.register_command('close', self.executor.cmd_close)
        self.executor.registry.register_command('type', self.executor.cmd_type)

    def open_file_from_explorer(self, index):
        file_path = self.file_model.filePath(index)
        from PyQt5.QtCore import QDir
        if QDir(file_path).exists():
            # It's a directory, do nothing or expand folder
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.editor.setPlainText(content)
            self.current_file_path = file_path

            # --- FIXED: save folder, not file ---
            file_info = QFileInfo(file_path)
            self.last_opened_folder = file_info.absolutePath()

            self.settings.setValue("last_opened_folder", self.last_opened_folder)
            self.terminal.log(f"Opened file: {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Open File", f"Could not open file:\n{e}")

    def new_file(self):
        self.editor.clear()
        self.current_file_path = None
        self.terminal.log("Created new file.")

    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            self.last_opened_folder,
            "Pach Script Files (*.psc);;All Files (*)"
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.editor.setPlainText(content)
                self.current_file_path = path

                # --- FIXED: save folder, not file ---
                file_info = QFileInfo(path)
                self.last_opened_folder = file_info.absolutePath()

                self.settings.setValue("last_opened_folder", self.last_opened_folder)
                self.terminal.log(f"Opened file: {path}")
            except Exception as e:
                QMessageBox.warning(self, "Open File", f"Could not open file:\n{e}")

    def open_folder_dialog(self):
        path = QFileDialog.getExistingDirectory(self, "Open Folder", self.last_opened_folder)
        if path:
            self.file_explorer.setRootIndex(self.file_model.index(path))
            self.current_file_path = None
            self.last_opened_folder = path
            self.settings.setValue("last_opened_folder", self.last_opened_folder)
            self.terminal.log(f"Opened folder: {path}")

    def save_file(self):
        if self.current_file_path:
            try:
                with open(self.current_file_path, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.terminal.log(f"Saved file: {self.current_file_path}")

                # Also update last_opened_folder here to folder containing current file
                file_info = QFileInfo(self.current_file_path)
                self.last_opened_folder = file_info.absolutePath()

                self.settings.setValue("last_opened_folder", self.last_opened_folder)
            except Exception as e:
                QMessageBox.warning(self, "Save File", f"Could not save file:\n{e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            self.last_opened_folder,
            "Pach Script Files (*.psc);;All Files (*)"
        )
        if path:
            if not path.endswith('.psc'):
                path += '.psc'
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.current_file_path = path

                # Save folder too here
                file_info = QFileInfo(path)
                self.last_opened_folder = file_info.absolutePath()

                self.settings.setValue("last_opened_folder", self.last_opened_folder)
                self.terminal.log(f"Saved file as: {path}")
            except Exception as e:
                QMessageBox.warning(self, "Save File", f"Could not save file:\n{e}")

    def check_mouse_failsafe(self):
        cursor_pos = QCursor.pos()
        screen = self.screen().geometry()

        margin = 10  # pixels from edge to trigger failsafe
        x, y = cursor_pos.x(), cursor_pos.y()
        left, top, right, bottom = screen.left(), screen.top(), screen.right(), screen.bottom()

        in_corner = (
            (x <= left + margin and y <= top + margin) or  # top-left
            (x >= right - margin and y <= top + margin) or  # top-right
            (x <= left + margin and y >= bottom - margin) or  # bottom-left
            (x >= right - margin and y >= bottom - margin)  # bottom-right
        )
        if in_corner:
            self.abort_requested = True
            self.terminal.log("Failsafe triggered: Mouse moved to corner. Aborting script...")
            self.failsafe_timer.stop()

    def run_script(self):
        if self.is_running:
            self.terminal.log("Script is already running. Please wait.")
            return

        self.is_running = True
        self.abort_requested = False
        self.terminal.log("Starting script execution...\n")

        self.failsafe_timer.start()

        try:
            script = self.editor.toPlainText()
            commands = self.parser.parse_script(script)
            for cmd, args in commands:
                if self.abort_requested:
                    self.terminal.log("\nScript aborted by failsafe.")
                    break
                self.terminal.log(f"> {cmd} {args}")
                try:
                    self.executor.execute(cmd, args)
                except Exception as e:
                    self.terminal.log(f"Error executing command '{cmd}': {e}")
            else:
                self.terminal.log("\nScript execution finished.")
        finally:
            self.is_running = False
            self.failsafe_timer.stop()

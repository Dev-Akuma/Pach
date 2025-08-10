# core/executor.py

import pyautogui
import subprocess
import time
from PyQt5.QtWidgets import QApplication
import pygetwindow as gw


class Executor:
    def __init__(self, command_registry, logger):
        self.registry = command_registry
        self.logger = logger
        self.opened_processes = {}

    def execute(self, command_name, args):
        self.logger.log(f"Executing command: {command_name} with args: {args}")
        handler = self.registry.get_command(command_name)
        if handler:
            handler(args)
        else:
            self.logger.log(f"Unknown command: {command_name}")

    def cmd_open(self, app_name):
        app_name = app_name.lower()
        apps = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
        }
        exe = apps.get(app_name)
        if not exe:
            self.logger.log(f"Unknown application '{app_name}'")
            return
        proc = subprocess.Popen(exe)
        self.opened_processes[app_name] = proc
        self.logger.log(f"Opened {app_name}")

        # Wait a moment for app to open
        time.sleep(1)
        
        # Focus window (Windows only)
        try:
            windows = gw.getWindowsWithTitle(app_name.capitalize())
            if windows:
                windows[0].activate()
                self.logger.log(f"Focused {app_name} window")
        except Exception as e:
            self.logger.log(f"Failed to focus {app_name} window: {e}")

    def cmd_wait(self, seconds_str):
        try:
            seconds = float(seconds_str)
            self.logger.log(f"Waiting for {seconds} seconds...")
            QApplication.processEvents()  # keep UI responsive during wait
            time.sleep(seconds)
        except ValueError:
            self.logger.log(f"Invalid wait time: {seconds_str}")

    def cmd_close(self, app_name):
        app_name = app_name.lower()
        proc = self.opened_processes.get(app_name)
        if proc:
            proc.terminate()
            proc.wait()
            self.logger.log(f"Closed {app_name}")
            del self.opened_processes[app_name]
        else:
            self.logger.log(f"No running instance of {app_name} found.")

    def cmd_type(self, text):
        self.logger.log(f"Typing text: {text}")

        # Replace special sequences
        text = text.replace('/e', '\n')
        text = text.replace('/t', '\t')
        text = text.replace('/b', '\b')
        text = text.replace('/s', ' ')
        
        time.sleep(0.5)  # small delay to ensure target window is focused
        pyautogui.typewrite(text, interval=0.05)

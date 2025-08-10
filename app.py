import tkinter as tk
from tkinter import scrolledtext, messagebox
import pyautogui
import time
import threading

pyautogui.FAILSAFE = True

class AutomationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Automation IDE")
        self.geometry("800x600")

        # Script editor
        self.script_editor = scrolledtext.ScrolledText(self, width=80, height=20)
        self.script_editor.pack(padx=10, pady=10)

        # Run button
        self.run_button = tk.Button(self, text="Run Script", command=self.run_script_thread)
        self.run_button.pack(pady=5)

        # Console output
        self.console = scrolledtext.ScrolledText(self, width=80, height=10, bg='black', fg='white', state='disabled')
        self.console.pack(padx=10, pady=10)

        self.running = False

    def log(self, msg):
        self.console.config(state='normal')
        self.console.insert(tk.END, msg + "\n")
        self.console.see(tk.END)
        self.console.config(state='disabled')

    def parse_and_execute_line(self, line):
        line = line.strip()
        if not line or line.startswith("#"):
            return
        parts = line.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd == "wait":
            try:
                seconds = float(arg)
                self.log(f"Waiting for {seconds} seconds...")
                time.sleep(seconds)
            except:
                self.log(f"Invalid wait time: {arg}")
        elif cmd == "type":
            # Simple special key parsing example: replace /t with tab, /e with enter
            arg = arg.replace("/t", "\t").replace("/e", "\n").replace("/s", " ")
            self.log(f"Typing: {arg}")
            pyautogui.write(arg)
        elif cmd == "exit":
            self.log("Exit command received. Stopping script.")
            self.running = False
        else:
            self.log(f"Unknown command: {cmd}")

    def run_script(self):
        self.running = True
        script = self.script_editor.get("1.0", tk.END).strip().splitlines()
        for line in script:
            if not self.running:
                self.log("Script execution stopped.")
                break
            self.parse_and_execute_line(line)
        self.log("Script finished.")

    def run_script_thread(self):
        if self.running:
            messagebox.showwarning("Warning", "Script is already running!")
            return
        threading.Thread(target=self.run_script, daemon=True).start()

if __name__ == "__main__":
    app = AutomationApp()
    app.mainloop()

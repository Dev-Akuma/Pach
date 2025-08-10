# core/parser.py

class Parser:
    def __init__(self):
        pass

    def parse_line(self, line):
        line = line.strip()
        if not line or line.startswith('#'):
            return None, None
        parts = line.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        return cmd, args

    def parse_script(self, script_text):
        commands = []
        for line in script_text.strip().splitlines():
            cmd, args = self.parse_line(line)
            if cmd:
                commands.append((cmd, args))
        return commands

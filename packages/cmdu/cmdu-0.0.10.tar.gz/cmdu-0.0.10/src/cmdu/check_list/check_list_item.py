import re


class CheckListItem:
    def __init__(self, id: str, checked: bool, line: str):
        self.id = id
        self.checked = checked
        self.line = line

    @staticmethod
    def from_line(line):
        if line == "\n":
            return None
        reg = re.compile("^\\[([Xx ])] (\\d{6}) \\|(.*)(\\n)?$")
        matching = reg.search(line)
        if not matching:
            return None
        is_checked = True if matching.group(1).lower() == 'x' else False
        id = matching.group(2)
        line_content = matching.group(3)
        return CheckListItem(id, is_checked, line_content)

    @staticmethod
    def from_dict(self, d):
        return CheckListItem(d["id"], d["checked"], d["line"])

    def to_line(self):
        return f"[{'X' if self.checked else ' '}] {self.id} |{self.line}\n"

    def to_dict(self):
        return {"id": self.id, "checked": self.checked, "line": self.line}

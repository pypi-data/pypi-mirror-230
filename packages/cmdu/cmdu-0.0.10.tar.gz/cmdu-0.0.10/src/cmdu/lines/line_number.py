class LineNumberAppender:
    def __init__(self):
        self.line_number = 1

    @staticmethod
    def formatting(i, v, format_str):
        number_line = format_str.format(i)
        return f"{number_line} |{v}"

    def append(self, line: str, format_str="{:06d}") -> str:
        ln = self.line_number
        self.line_number += 1
        return LineNumberAppender.formatting(ln, line, format_str)


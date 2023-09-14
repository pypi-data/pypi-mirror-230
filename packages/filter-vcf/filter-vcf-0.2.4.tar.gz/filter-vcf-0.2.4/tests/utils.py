from typing import Optional
from unittest.mock import Mock


class FileMock:
    def __init__(
        self,
        file_lines: Optional[list[str]] = None,
        write_mock: Optional[Mock] = None,
        writelines_mock: Optional[Mock] = None,
    ):
        self.data = file_lines
        self.write_mock = write_mock
        self.writelines_mock = writelines_mock

    def __iter__(self):
        return iter(self.data)

    def write(self, line):
        self.write_mock(line)

    def writelines(self, lines):
        self.writelines_mock(lines)

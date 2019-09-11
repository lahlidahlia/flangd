from utils import eprint
import os


class File():
    def __init__(self, path, content, compiler):
        self.path = path
        self.compiler = compiler
        self.content = ""
        self.compilable_content = ""
        self.symbols = {}
        self.diagnostics = []
        _, self.suffix = os.path.splitext(path)
        self.update_content(content)

    def update_content(self, content):
        self.clear_diagnostics()
        self.content = content
        rcode, stdout, _ = self.compiler.compile_content(
            self.content, suffix=self.suffix, extra_flags=['-fflangd-diagnostic'])
        if rcode == 0:
            self.compilable_content = content
            self.update_symbols()
        else:
            for line in stdout.splitlines():
                self.diagnostics.append(self.parse_diagnostics(line))

    def has_diagnostics(self):
        return True if self.diagnostics else False

    def clear_diagnostics(self):
        self.diagnostics = []

    def update_symbols(self):
        self.symbols = {}
        extra_flags = ['-fget-symbols-sources']
        rcode, output, _ = self.compiler.compile_content(
            self.compilable_content,
            extra_flags=extra_flags,
            suffix=self.suffix)
        if rcode == 1:
            return
        lines = output.splitlines()
        for line in lines:
            symbol, *info = self.parse_symbol_def(line)
            self.symbols[symbol] = info

    def get_definition(self, line, column):
        # [path, line, startColumn, endColumn]
        columns = self.get_word_range_at(line, column)
        if columns == None:
            return None
        c1, c2 = columns
        extra_flags = ['-fget-definition', str(line), str(c1), str(c2)]
        rcode, output, _ = self.compiler.compile_content(self.compilable_content,
                                                extra_flags=extra_flags)
        if rcode == 1:
            return None
        _, *output = self.parse_symbol_def(output)
        return output

    def get_symbols(self):
        # {symbol: [path, line, startColumn, endColumn]}
        # line, startColumn and endColumn are int.
        return self.symbols

    def get_word_range_at(self, line, column):
        line -= 1
        column -= 1
        content = self.compilable_content.splitlines(keepends=True)
        if line > len(content) or column > len(content[line]):
            return None
        first = column - 1
        second = column
        while content[line][first].isalnum() \
                or content[line][first] == '_':
            first -= 1
        if first != column:
            first += 1
        while content[line][second].isalnum() \
                or content[line][second] == '_':
            second += 1
        if first == second:
            return None
        return (first + 1, second + 1)

    def parse_symbol_def(self, symbol_str):
        # Parse symbol: path, line, col1-col2 into
        # [symbol, path, int(line), int(col1), int(col2)]
        # Sometimes is [symbol, mod] when the symbol is elsewhere
        symbol, pos = symbol_str.split(':')
        pos = pos.split(', ')
        if len(pos) == 1:
            return [symbol, pos[0].strip()]
        _, line, columns = pos
        columns = columns.split('-')
        return [symbol, self.path, int(line), int(columns[0]), int(columns[1])]

    def parse_diagnostics(self, diagnostics):
        # Parse code:path:startLine,startCol:endLine,endPos:message
        # into [code, path, startLine, startCol, endLine, endPos, message]
        path, start, end, code, *message = diagnostics.split(':')
        message = ':'.join(message)
        start = start.split(',')
        end = end.split(',')
        return [
            path,
            int(start[0]),
            int(start[1]),
            int(end[0]),
            int(end[1]), code, message
        ]

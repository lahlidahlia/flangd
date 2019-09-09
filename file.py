from utils import eprint
import os


class File():
    def __init__(self, path, content, compiler):
        self.path = path
        self.compiler = compiler
        self.content = ""
        self.compilable_content = ""
        self.symbols = {}
        _, self.suffix = os.path.splitext(path)

        self.update_content(content)

    def update_content(self, content):
        self.content = content
        if self.compiler.compile_check_content(content):
            self.compilable_content = content
            self.update_symbols()

    def update_symbols(self):
        extra_flags = ['-fget-symbols-sources']
        rcode, output = self.compiler.compile_content(
            self.compilable_content, extra_flags=extra_flags,
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
            return columns
        c1, c2 = columns
        extra_flags = ['-fget-definition', str(line), str(c1), str(c2)]
        rcode, output = self.compiler.compile(
            self.path, extra_flags=extra_flags)
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
        first = column - 1
        second = column
        content = self.compilable_content.splitlines(keepends=True)
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
        return (first+1, second+1)

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

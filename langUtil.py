import re

ID_REGEX = r"^[a-zA-Z_][a-zA-Z_0-9]*$"


class LangUtil:

    def __init__(self):
        self.tags2str = {
            "<ENTER>": "\n",
            "<IND>": "",
            "<UNIND>": "",
            "<BREAK>": "",
            "<str>": "\"\"",
            "<char>": "''",
            "<float>": "0.0",
            "<int>": "0",
            "<double>": "0.0",
            "<long>": "0",
            "<bool>": "true",
            "<null>": "null",
        }

    def render(self, tokens, start):
        r = ""
        for i in range(start, len(tokens)):
            token = tokens[i]
            if token in self.tags2str:
                token = self.tags2str[token]
            if token != "" and i > 0 and self.hasSpaceBetween(tokens, i):
                r += " "

            r += token
        return r

    def hasSpaceBetween(self, tokens, nextI):
        left = "" if nextI == 0 else tokens[nextI - 1]
        right = tokens[nextI]
        if left == "" or right == "":
            return False
        if right == ",":
            return False
        if left == "." or right == ".":
            return False
        if left == "<ENTER>" or right == "<ENTER>":
            return False
        if left == "(" or right == ")":
            return False
        if left == "[" or right == "]":
            return False
        if left == ",":
            return True
        if left == "for" or left == "while" or right == "is":
            return True
        if right == "(" or right == "[":
            return re.match(ID_REGEX, left) is None
        if left == ")" and right == "{":
            return True
        if right == ";":
            return False
        if right == "{":
            return True
        if re.match(ID_REGEX, left) is None and re.match(ID_REGEX, right) is None:
            return False
        return True

    def datamask(self, s, trivialLiterals):
        return s

    def rescue(self, document, rescues):
        pass

    def should_predict(self, view):
        if "string.quoted" in view.scope_name(view.sel()[0].a):
            return False
        return True
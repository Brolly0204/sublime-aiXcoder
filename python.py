import re
from aiXcoder.langUtil import ID_REGEX, LangUtil


class PythonLangUtil (LangUtil):

    def __init__(self):
        super().__init__()
        self.tags2str["<bool>"] = "True"
        self.tags2str["<null>"] = "None"

    def skipString(self, i, s, trivialLiterals, stringBuilder, char):
        c = s[i]
        pythonDoc = c == s[i + 1] and c == s[i + 2]
        if pythonDoc:
            i += 2
        i += 1
        strStart = i
        while i < len(s):
            if pythonDoc:
                if s.startswith(c + c + c, i):
                    break
            else:
                if s[i] == char:
                    break
                if s[i] == "\\":
                    i += 1
            i += 1
        strContent = s[strStart: i]
        if strContent in trivialLiterals:
            stringBuilder += strContent
        stringBuilder += char
        return i, stringBuilder

    def datamask(self, s, trivialLiterals):
        stringBuilder = ""
        for i in range(len((s))):
            c = s[i]
            stringBuilder += c
            if c == '"' or c == "'":
                i, stringBuilder = self.skipString(
                    i, s, trivialLiterals, stringBuilder, c)
        return stringBuilder

    def hasSpaceBetween(self, tokens, nextI):
        left = "" if nextI == 0 else tokens[nextI - 1]
        right = tokens[nextI]
        if right == ":":
            return False
        return LangUtil.hasSpaceBetween(self, tokens, nextI)

    def should_predict(self, view):
        return LangUtil.should_predict(self, view)

import re
from aiXcoder.langUtil import ID_REGEX, LangUtil


class JavaScriptLangUtil (LangUtil):

    def hasSpaceBetween(self, tokens, nextI):
        left = "" if nextI == 0 else tokens[nextI - 1]
        right = tokens[nextI]
        if left == "" or right == "":
            return False
        if left == "." or right == ".":
            return False
        if left == "<ENTER>" or right == "<ENTER>":
            return False
        if left == "(" or right == ")":
            return False
        if left == "[" or right == "]":
            return False
        if right == "[":
            return False
        if left == "for" or left == "while" or left == "if":
            return True
        if left == ")" and right == "{":
            return True
        if right == ":":
            return False
        if left == ":":
            return True
        if re.match(ID_REGEX, left) is not None and right == "(":
            return False
        if right == ";":
            return False
        if re.match(ID_REGEX, left) is None and re.match(ID_REGEX, right) is None:
            return False
        if left == "++" or right == "++":
            return False
        if left == "--" or right == "--":
            return False

        return True

    def datamask(self, s, trivialLiterals):
        stringBuilder = ""
        i = 0
        while i < len(s):
            c = s[i]
            stringBuilder += c
            if c == '"' or c == "'" or c == "`":
                i += 1
                strStart = i
                while i < len(s):
                    if s[i] == c:
                        break
                    if s[i] == "\\":
                        i += 1
                    i += 1
                strContent = s[strStart, i]
                if strContent in trivialLiterals:
                    stringBuilder += strContent
                stringBuilder += c
            i += 1
        return stringBuilder

    def should_predict(self, view):
        return LangUtil.should_predict(self, view)

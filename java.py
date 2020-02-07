import re
from aiXcoder.langUtil import ID_REGEX, LangUtil


class JavaLangUtil (LangUtil):

    genericTypeRegex = r"^([a-zA-Z0-9_$]+|<|>|,|\[\])$"

    def isGenericTypeBracket(self, tokens, i):
        if tokens[i] == "<":
            level = 1
            while level > 0 and i < len(tokens):
                if len(tokens[i]) == 0:
                    i += 1
                    continue
                if tokens[i] == ">":
                    level -= 1
                elif not re.match(JavaLangUtil.genericTypeRegex, tokens[i]):
                    break
                i += 1
            return level == 0
        elif tokens[i] == ">":
            level = 1
            while level > 0 and i >= 0:
                if len(tokens[i]) == 0:
                    i -= 1
                    continue
                if tokens[i] == "<":
                    level -= 1
                elif not re.match(JavaLangUtil.genericTypeRegex, tokens[i]):
                    break
                i -= 1
            return level == 0
        else:
            return False

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
        if not re.match(ID_REGEX, left) and right == "{":
            return True
        if re.match(ID_REGEX, left) and right == "(":
            return False
        if right == ";":
            return False
        if not re.match(ID_REGEX, left) and not re.match(ID_REGEX, right):
            return False
        if left == "++" or right == "++":
            return False
        if left == "--" or right == "--":
            return False
        if right == "<" or right == ">":
            return not self.isGenericTypeBracket(tokens, nextI)
        if left == "<" or left == ">":
            return not self.isGenericTypeBracket(tokens, nextI - 1)

        return True

    def datamask(self, s, trivialLiterals):
        stringBuilder = ""
        i = 0
        while i < len(s):
            c = s[i]
            stringBuilder += c
            if c == '"' or c == "'":
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

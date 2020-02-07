import re
from aiXcoder.langUtil import ID_REGEX, LangUtil


class PhpLangUtil (LangUtil):

    def hasSpaceBetween(self, tokens, nextI):
        left = "" if nextI == 0 else tokens[nextI - 1]
        right = tokens[nextI]
        if left == "" or right == "":
            return False
        if right == "->":
            return False
        if right == ":" or left == "$" or left == "!":
            return False
        return LangUtil.hasSpaceBetween(self, tokens, nextI)

    def datamask(self, s, trivialLiterals):
        return s

    def should_predict(self, view):
        return LangUtil.should_predict(self, view)

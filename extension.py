import sublime
import sublime_plugin

import urllib
import json
import threading
import functools
import re
import uuid
import hashlib
import webbrowser

from aiXcoder.typescript import TypeScriptLangUtil
from aiXcoder.javascript import JavaScriptLangUtil
from aiXcoder.java import JavaLangUtil
from aiXcoder.php import PhpLangUtil
from aiXcoder.python import PythonLangUtil
from aiXcoder.cpp import CppLangUtil
from aiXcoder.codestore import CodeStore

__DEBUG__ = False

endpoint = "https://api.aixcoder.com/predict"


def get_ext(syntax):
    if 'JavaScript' in syntax:
        return "javascript(Javascript)"
    elif 'TypeScript' in syntax:
        return "typescript(Typescript)"
    elif 'Java' in syntax:
        return "java(Java)"
    elif 'Php' in syntax:
        return "php(Php)"
    elif 'Python' in syntax:
        return "python(Python)"
    elif 'C++' in syntax:
        return "cpp(Cpp)"
    else:
        return None


def get_lang_util(syntax):
    if 'JavaScript' in syntax:
        return JavaScriptLangUtil()
    elif 'TypeScript' in syntax:
        return TypeScriptLangUtil()
    elif 'Java' in syntax:
        return JavaLangUtil()
    elif 'Php' in syntax:
        return PhpLangUtil()
    elif 'Python' in syntax:
        return PythonLangUtil()
    elif 'C++' in syntax:
        return CppLangUtil()
    else:
        return None


def get_uuid():
    s = sublime.load_settings("Preferences.sublime-settings")
    if s.get("aixcoder.uuid", None) is None:
        s.set("aixcoder.uuid", "sublime-" + str(uuid.uuid4()))
        sublime.save_settings("Preferences.sublime-settings")
    return s.get("aixcoder.uuid", None)


def md5Hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def log(*args, **kwargs):
    if __DEBUG__:
        print(*args, **kwargs)


def on_nav(view, href):
    # p = view.selection[0].a
    pattern = re.compile('https://www.aixcoder.com/#/Guide')
    match = pattern.match(href)
    if match:
        jump_to_web()
    else:
        view.run_command("insert", {"characters": href[5:]})
        view.hide_popup()


def on_hide(view):
    popup_open = False
    view.settings().set('aiXcoder.internal_list_shown', False)


popup_open = False
r = None
results = []
long_results = []
r_map = []
last_text = ""
current_selected = 0
current_filter = ""


def render_up_down(index):
    if index < current_selected:
        return "↑"
    elif index > current_selected:
        return "↓"
    else:
        return "enter"


def render_item_long(_, r):
    style = ""
    if r == current_selected:
        style += "background-color:grey"
    return "<a style='text-decoration: none;display: block;line-height: 18px;" + style + "' href='long:" + \
        _[1]+"'>"+_[0]+"<i style='padding-left:10px;font-size: 12px;color: #FFF;position: relative;margin-left: 220%;display: block;top: -20px;margin-bottom: -18px;'>" + \
        render_up_down(r) + "</i></a>"


def render_item_short(_, r):
    style = ""
    if r == current_selected:
        style += "background-color:grey;"
    return "<a style='text-decoration: none;display: block;line-height: 18px;" + style + "' href='sort:"+_[1][len(current_filter):]+"'>" + _[1] + "<i style='padding-left:10px;font-size: 12px;color: #FFF;display: block;position: relative;margin-left: 220%;top: -20px;margin-bottom: -18px;'>" + render_up_down(r) + "</i></a>"


def render_to_html(lang_util, r, filter_text="", selected=0, move_only=False, current=''):
    # log(">>>render_html")
    # log(r)
    # log("filter_text=" + repr(filter_text))
    # log("<<<render_html")
    global r_map, current_filter, current_selected, results, long_results
    if not move_only and (r is None or len(r) == 0):
        return ""
    if not move_only:
        results = []
        long_results = []
        displayed = set()
        r_map = []
        if filter_text != "-":
            current_filter = filter_text
        elif 'current' in r[0]:
            current_filter = r[0]['current']
            # if r[0]['current'] == "":
            #   return ''
        else:
            current_filter = ""
        # log("current_filter=" + repr(current_filter))
        for single_r in r:
            # log("single_r =" + repr(single_r))
            if len(single_r['tokens']) > 0:
                display = lang_util.render(single_r['tokens'], 0)
                if 'r_completion' in single_r:
                    r_completion = lang_util.render(
                        single_r['r_completion'], 0)
                else:
                    r_completion = ''
                # log("long display" + display)
                if len(current_filter) == 0 or (single_r['current'] + display).replace(" ", "").startswith(current_filter):
                    actual_display = single_r['current'] + display
                    if len(r_completion) > 0:
                        actual_display += r_completion
                    long_results.append((actual_display, display))
                    displayed.add(actual_display)
                    r_map.append(
                        ((single_r['current'] + display)[len(current_filter):], r_completion))
            if 'sort' in single_r:
                if filter_text == "-":
                    current_filter = current
                for single_sort in single_r['sort']:
                    single_sort_prob, single_sort_word = single_sort[:2]
                    if len(results) < 10 and (single_sort_word not in displayed) and (len(current_filter) == 0 or single_sort_word.startswith(current_filter)) and len(current_filter) < len(single_sort_word):
                        results.append(
                            (single_sort_word + '\taixcoder' + str(single_sort_prob), single_sort_word))
                        displayed.add(single_sort_word)
                        r_map.append(
                            (single_sort_word[len(current_filter):], ''))
    lis = ""
    btmText = "<div style='font-size: 12px;line-height: 18px;margin-top: 4px;margin-left: 150%;'><span style='padding-left: 8px;position: relative;top: -2px;color: #81837C;'><a href='https://www.aixcoder.com/#/Guide' style='color: #81837C;text-direction: none;'>aiXcoder智能编程助手</a></span></div>"
    r = 0
    if selected < 0:
        selected = 0
    if selected >= len(long_results) + len(results):
        selected = len(long_results) + len(results) - 1
    current_selected = selected
    # log("$$$$")
    # log(long_results)
    # log(results)
    for _ in long_results:
        lis += render_item_long(_, r)
        r += 1
    for _ in results:
        lis += render_item_short(_, r)
        r += 1
    if len(lis) > 0:
        lis += btmText
        return "<html><body>" + lis + "</body></html>"
    else:
        return ""


def show(html, view):
    global popup_open
    if len(html) > 0:
        view.settings().set('aiXcoder.internal_list_shown', True)
        if popup_open:
            view.update_popup(html)
        else:
            view.show_popup(html, sublime.COOPERATE_WITH_AUTO_COMPLETE, -1, 1000,
                            1000, functools.partial(on_nav, view), functools.partial(on_hide, view))
        popup_open = True
    else:
        view.settings().set('aiXcoder.internal_list_shown', False)
        popup_open = False
        view.hide_popup()


def jump_to_web():
    webbrowser.open("https://www.aixcoder.com/#/Guide")


class AiXPredictThread(threading.Thread):
    def __init__(self, lang_util, view, values, headers, current, *args, **kwargs):
        self.lang_util = lang_util
        self.view = view
        self.values = values
        self.headers = headers
        self.current = current
        super().__init__(*args, **kwargs)

    def run(self, retry=True):
        # log("send request...")
        view = self.view
        values = self.values
        headers = self.headers
        # log(repr(values))
        data = urllib.parse.urlencode(values).encode("utf-8")
        req = urllib.request.Request(endpoint, data, headers)
        global r
        with urllib.request.urlopen(req) as response:
            r = response.read()
            r = r.decode('utf-8')
        projName = values['project']
        fileID = values['fileid']
        # log("r=" + repr(r))
        if retry and r == 'Conflict':
            CodeStore.getInstance().invalidateFile(projName, fileID)
            return self.run(retry=False)
        else:
            maskedText = values['text']
            CodeStore.getInstance().saveLastSent(projName, fileID, maskedText)
            r = json.loads(r)
            if 'current' in r[0] and r[0]['current'] == "":
                return
            # log(r)
            html = render_to_html(
                self.lang_util, r, filter_text="-", current=self.current)
            show(html, view)


class AiXCoderAutocomplete(sublime_plugin.EventListener):
    def on_modified_async(self, view):
        syntax = view.settings().get("syntax")
        lang_util = get_lang_util(syntax)
        if lang_util is None:
            return
        if not lang_util.should_predict(view):
            return
        # log("syntax=" + syntax)

        # log("====================================")
        global r, popup_open, last_text
        popup_open = view.is_popup_visible()
        prefix = view.substr(sublime.Region(0, view.selection[0].a))
        # log("prefix=" + repr(prefix))
        i = len(prefix) - 1
        has_non_digit = False
        while i >= 0 and (prefix[i].isalpha() or prefix[i].isdigit() or prefix[i] in ["_", "$"]):
            has_non_digit = has_non_digit or not prefix[i].isdigit()
            i -= 1
        current = prefix[i + 1:]
        if popup_open:
            # log("current=" + repr(current))
            if len(current) == 0 and last_text != prefix:
                show("", view)
            else:
                # log("cached r=" + repr(r))
                html = render_to_html(lang_util, r, current)
                # log(html)
                show(html, view)
        if not popup_open:
            prefix = view.substr(sublime.Region(0, view.selection[0].a))
            line_end = view.line(view.selection[0].a).b
            remaining_text = view.substr(
                sublime.Region(view.selection[0].a, line_end))
            last_text = prefix
            ext = get_ext(syntax)
            # log("ext = " + ext)
            fileID = view.file_name() or ("_untitled_" + str(view.buffer_id()))
            maskedText = prefix
            offset = CodeStore.getInstance().getDiffPosition(fileID, maskedText)
            md5 = md5Hash(maskedText)
            values = {
                "text": maskedText[offset:],
                "remaining_text": remaining_text,
                "ext": ext,
                "uuid": get_uuid(),
                "project": "_scratch",
                "fileid": fileID,
                "sort": 1,
                "offset": offset
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "uuid": get_uuid(),
                "ext": ext,
            }
            AiXPredictThread(lang_util, view, values, headers, current=current,
                             name="aix-predict-thread").start()


class AixConfirmCommand(sublime_plugin.TextCommand):

    def run(self, edit, index):
        view = self.view
        # log("tabbed ! " + str(current_selected))
        # log("r_map=" + repr(r_map))
        if len(r_map) > current_selected:
            view.run_command(
                "insert", {"characters": r_map[current_selected][0] + r_map[current_selected][1]})
            if len(r_map[current_selected][1]) > 0:
                view.run_command(
                    "move", {"by": "characters", "forward": False, "amount": len(r_map[current_selected][1])})
        show("", view)


class AixMoveCommand(sublime_plugin.TextCommand):

    def run(self, edit, direction):
        view = self.view
        # log("moved ! " + direction)
        if direction == "up":
            show(render_to_html(None, None,
                                selected=current_selected - 1, move_only=True), view)
        else:
            show(render_to_html(None, None,
                                selected=current_selected + 1, move_only=True), view)

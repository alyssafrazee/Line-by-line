import sublime
import sublime_plugin
import os
import subprocess
import re

settingsfile = 'line-by-line.sublime-settings'

# escape double quote
def escape_dq(string):
    string = string.replace('\\', '\\\\')
    string = string.replace('"', '\\"')
    return string

# clean command before sending to Terminal
def clean(cmd):
    plat = sublime.platform()
    if plat == "osx":
        cmd = escape_dq(cmd)
    cmd = cmd.rstrip('\n')
    if len(re.findall("\n", cmd)) == 0:
        cmd = cmd.lstrip()
    return cmd

# get platform specific key
def get(plat, key, default=None):
    settings = sublime.load_settings(settingsfile)
    plat_settings = settings.get(plat)
    if key in plat_settings:
        return plat_settings[key]
    else:
        return default

# the main function
def runcmd(cmd):
    cmd = clean(cmd)
    plat = sublime.platform()
    if plat == 'osx':
        App = get("osx", "App", "Terminal")
        if App == 'Terminal':
            args = ['osascript']
            args.extend(['-e', 'tell app "Terminal" to do script "' + cmd + '" in front window\n'])
            subprocess.Popen(args)
        elif re.match('iTerm', App):
                args = ['osascript']
                apple_script = ('tell application "' + App + '"\n'
                                    'tell the first terminal\n'
                                        'tell current session\n'
                                            'write text "' + cmd + '"\n'
                                        'end tell\n'
                                    'end tell\n'
                                'end tell\n')
                args.extend(['-e', apple_script])
                subprocess.Popen(args)

    else:
        sublime.error_message("Only OSX is supported - sorry!")

class SendSelectCommand(sublime_plugin.TextCommand):

    # expand selection to {...} when being triggered
    def expand_sel(self, sel):
        esel = self.view.find(r"""^.*(\{(?:(["\'])(?:[^\\\\]|\\\\.|\n)*?\\2|#.*$|[^\{\}]|\n|(?1))*\})"""
            , self.view.line(sel).begin())
        if self.view.line(sel).begin() == esel.begin():
            return esel

    def run(self, edit):
        cmd = ''
        for sel in self.view.sel():
            if sel.empty():
                thiscmd = self.view.substr(self.view.line(sel))
                # if the line ends with {, expand to {...}
                if re.match(r".*\{\s*$", thiscmd):
                    esel = self.expand_sel(sel)
                    if esel:
                        thiscmd = self.view.substr(esel)
            else:
                thiscmd = self.view.substr(sel)
                # if selection is function meta definition (R), expand to {...}
                if self.view.score_selector(sel.end()-1, "meta.function.r") and \
                    not self.view.score_selector(sel.end(), "meta.function.r"):
                    esel = self.expand_sel(sel)
                    if esel:
                        thiscmd = self.view.substr(esel)
            cmd += thiscmd +'\n'
        runcmd(cmd)


class AppSwitcher(sublime_plugin.WindowCommand):

    def show_quick_panel(self, options, done):
        sublime.set_timeout(lambda: self.window.show_quick_panel(options, done), 10)

    def run(self):
        plat = sublime.platform()
        if plat == 'osx':
            self.app_list = ["Terminal", "iTerm"]
            pop_string = ["Terminal", "iTerm 2"]
        else:
            sublime.error_message("Only OSX is supported - sorry!")

        self.show_quick_panel([list(z) for z in zip(self.app_list, pop_string)], self.on_done)

    def on_done(self, action):
        if action==-1: return
        settings = sublime.load_settings(settingsfile)
        plat = sublime.platform()
        if plat == 'osx':
            plat_settings = settings.get('osx')
            plat_settings['App'] = self.app_list[action]
            settings.set('osx', plat_settings)
        else:
            sublime.error_message("Only OSX is supported - sorry!")

        sublime.save_settings(settingsfile)
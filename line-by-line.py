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
                self.advanceCursor(sel) ### (AF) Snagged from Rtools.py I think this is approximate the same place that Rtools.py uses the advanceCursor function. In that file they loop over "region" instead of "sel".                        
                        
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

    ### (AF) function below is snagged from Rtools.py
    def advanceCursor(self, region):
        (row, col) = self.view.rowcol(region.begin())

        # Make sure not to go past end of next line
        nextline = self.view.line(self.view.text_point(row + 1, 0))
        if nextline.size() < col:
            loc = self.view.text_point(row + 1, nextline.size())
        else:
            loc = self.view.text_point(row + 1, col)

        # Remove the old region and add the new one
        self.view.sel().subtract(region)
        self.view.sel().add(sublime.Region(loc, loc))
    ### (AF) End of snag         

class RDocsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sel = self.view.sel()[0]
        # Taking out spaces and such
        params_reg = self.view.find('(?<=\().*(?=\)|$)', sel.begin())
        # self.view.insert(edit, sel.begin(), params_reg)
        params_txt = self.view.substr(params_reg)
        params_txt=re.sub("^\s+","",params_txt)
        params_txt=re.sub("\s+\Z","",params_txt)
        params_txt=re.sub(',\s+', ",", params_txt)
        params_txt=re.sub('\s+=', "=", params_txt)
        params_txt=re.sub('=\s+', "=", params_txt)
        params_txt=re.sub('"', "", params_txt)
        params_txt=re.sub(',$', "", params_txt)

        #### adding trailing , so they are the same
        params_txt = params_txt + ","

        ### take out anything like ifelse() or c()
        params_txt=re.sub('=[^=]+?\(\S+?\),', ",", params_txt)
        params_txt=re.sub('=[^=]+?\{\S+?\},', ",", params_txt)
        params_txt=re.sub(',$', "", params_txt)



        # Splitting on commas
        params = params_txt.split(',')
        snippet = "#'<brief desc>\n#'\n#'<full description>\n"

        for p in params:
            # self.view.insert(edit, sel.begin(), p + "\n")

            # Added if statement if not empty
            if p != '':
                p = re.sub('(.*)=(.*)', "\\1", p)
                snippet += "#' @param %s <what param does>\n" % p

        snippet += "#' @export\n#' @keywords\n#' @seealso\n#' @return\n#' @alias\n#' @examples \dontrun{\n#'\n#'}\n"

        self.view.insert(edit, sel.begin(), snippet)


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

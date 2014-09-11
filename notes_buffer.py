import sublime, sublime_plugin
import os, fnmatch, re
import yaml

TAB_SIZE = 2
COL_WIDTH = 30

def settings():
    return sublime.load_settings('Notes.sublime-settings')

class NotesBufferCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.new_file()
        view.set_scratch(True)
        view.set_name("✎ Notes Index")
        view.set_syntax_file('Packages/PlainNotes/Notes Index.hidden-tmLanguage')
        view.settings().set('color_scheme', 'Packages/PlainNotes/Color Schemes/Notes-Index.hidden-tmTheme')
        self.window.focus_view(view)
        view.run_command('notes_buffer_refresh')

class NotesBufferRefreshCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        v = self.view
        v.set_read_only(False)
        v.erase(edit, sublime.Region(0, self.view.size()))
        root = os.path.normpath(os.path.expanduser(settings().get("root")))
        lines = self.list_files(root)

        v.settings().set('notes_buffer_files', lines)

        v.insert(edit, 0, "\n".join([f[0] for f in lines]))
        v.set_read_only(True)

    def list_files(self, path):
        lines = []
        for root, dirs, files in os.walk(path, topdown=False):
            level = root.replace(path, '').count(os.sep) - 1
            indent = ' ' * TAB_SIZE * (level)
            relpath = os.path.relpath(root, path)
            if  not (relpath.startswith(".")):
                line_str = '{0}▣ {1}'.format(indent, os.path.relpath(root, path))
                lines.append( (line_str, root) )
            if  (not relpath.startswith(".brain")):
                subindent = ' ' * TAB_SIZE * (level + 1)
                for f in files:
                    for ext in settings().get("note_file_extensions"): # display only files with given extension
                        if fnmatch.fnmatch(f, "*." + ext):
                            line_str = '{0}≡ {1}'.format(subindent, re.sub('\.note$', '', f))
                            line_path = os.path.normpath(os.path.join(root, f))
                            yaml_read = self.parseYAML(line_path)
                            line_str = line_str + ' -- created: ' + yaml_read['date'].strftime("%Y-%m-%d %H:%M")
                            #line_str = line_str + '-- modified: ' + str(os.path.getmtime(line_path))
                            lines.append( (line_str, line_path)  )

        return lines

    def parseYAML(self,path):
     stream = open(path, "r")
     s = 0
     e = 0
     yaml_read = '';
     for line in stream:
      if s == 1 and re.match('---',line):
        e = 1
      if s == 0 and re.match('---',line):
        s = 1
      if e == 1:
        break
      if not re.match('---',line):
       yaml_read = yaml_read + line +'\n' 
     stream.close()
     yaml_read = yaml_read + ''

     doc = yaml.load(yaml_read)

     yaml_read = '';
     for k in doc:
      yaml_read = yaml_read + k + ':' 
     return doc

class NotesBufferOpenCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        v = self.view
        for sel in v.sel():
            file_index = v.rowcol(sel.a)[0]
            files = v.settings().get('notes_buffer_files')
            file_path = files[file_index][1]
            sublime.run_command("notes_open", {"file_path": file_path})

import sublime, sublime_plugin, re, sys, os

reg_file = r"""Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\$protocol_name$]
@="URL:Sublime Protocol"
"URL Protocol"=""

[HKEY_CLASSES_ROOT\$protocol_name$\DefaultIcon]
@="\"$sublime_text_file$\",0"

[HKEY_CLASSES_ROOT\$protocol_name$\shell]

[HKEY_CLASSES_ROOT\$protocol_name$\shell\open]

[HKEY_CLASSES_ROOT\$protocol_name$\shell\open\command]
@="\"$sublime_text_file$\" --command \"open_file_from_url {\\\"url\\\": \\\"%1\\\"}\""
"""

WINDOWS = sublime.platform() == 'windows'
protocol_name = 'subl';
sublime_text_file = os.path.dirname(sublime.__file__) + r'\sublime_text.exe'
reg_val = r'"$EXE" --command "open_file_from_url {\"url\": \"%1\"}"'.replace('$EXE', sublime_text_file)

if WINDOWS:
	from winreg import (OpenKey, QueryValueEx, CreateKey, SetValueEx, SetValue,
						KEY_ALL_ACCESS, HKEY_CLASSES_ROOT, REG_SZ)
	try:
		with OpenKey( HKEY_CLASSES_ROOT,
					 r'%s\shell\open\command' % protocol_name) as key:
			val, _ = QueryValueEx(key, None)
			if reg_val != val:
				raise WindowsError

	except WindowsError:
		with open('subl.reg', 'w+') as subl_reg_file:
			reg_file = reg_file.replace('$sublime_text_file$',sublime_text_file.replace('\\','\\\\'))
			reg_file = reg_file.replace('$protocol_name$',protocol_name)
			subl_reg_file.write(reg_file)
			subl_reg_file.close()
		os.system('regedit /s "' +os.getcwd()+ '\\subl.reg"')


class OpenFileFromUrlCommand(sublime_plugin.WindowCommand):
	def run(self,url):
		replaced = re.sub('^subl://', '', url)
		self.window.open_file(replaced,1)



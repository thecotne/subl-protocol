import sublime, sublime_plugin, os, tempfile, re
from os.path import dirname, realpath

protocol_name = 'subl'
platform = sublime.platform()

class OpenFileFromUrlCommand(sublime_plugin.WindowCommand):
	def run(self, url):
		if platform == 'linux':
			# 'subl://file.txt' => subl://file.txt
			url = url[1:][:-1]

		# subl://file.txt => file.txt
		url = re.sub(r"^" + protocol_name + ":(\/\/)?", "", url)

		self.window.open_file(url, 1)

def plugin_loaded():
	if platform == 'windows':
		win_plugin_loaded()
	elif platform == 'linux':
		linux_plugin_loaded()

def plugin_unloaded():
	if platform == 'windows':
		win_plugin_unloaded()
	elif platform == 'linux':
		linux_plugin_unloaded()

def linux_plugin_loaded():
	cmd = 'cp "{}/subl-protocol.desktop" ~/.local/share/applications/subl-protocol.desktop &&\
			xdg-mime default subl-protocol.desktop x-scheme-handler/subl'

	packagePath = dirname(realpath(__file__))

	os.system(cmd.format(packagePath))



def linux_plugin_unloaded():
	os.system('rm ~/.local/share/applications/subl-protocol.desktop')

def win_plugin_loaded():
	sublime_text_file = os.path.dirname(sublime.__file__) + r'\sublime_text.exe'
	reg_val = r'"$EXE" --command "open_file_from_url {\"url\": \"%1\"}"'
	reg_val = reg_val.replace('$EXE', sublime_text_file)

	from winreg import (OpenKey, QueryValueEx, CreateKey, SetValueEx, SetValue,
						KEY_ALL_ACCESS, HKEY_CLASSES_ROOT, REG_SZ)
	try:
		with OpenKey( HKEY_CLASSES_ROOT,
					 r'%s\shell\open\command' % protocol_name) as key:
			val = QueryValueEx(key, None)
			if reg_val != val[0]:
				raise WindowsError
	except WindowsError:
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
		reg_file = reg_file.replace('$sublime_text_file$',sublime_text_file.replace('\\','\\\\'))
		reg_file = reg_file.replace('$protocol_name$',protocol_name)
		subl_reg_file = tempfile.NamedTemporaryFile(mode='w+',delete=False)
		subl_reg_file.write(reg_file)
		subl_reg_file.close()
		# os.system('regedit /s "' +subl_reg_file.name+ '" && echo "plugin_loaded" && pause')
		os.system('regedit /s "' +subl_reg_file.name+ '" ')


def win_plugin_unloaded():
	cleen_reg_file = r"""Windows Registry Editor Version 5.00
	[-HKEY_CLASSES_ROOT\$protocol_name$]
	"""
	cleen_reg_file = cleen_reg_file.replace('$protocol_name$',protocol_name)
	subl_reg_file = tempfile.NamedTemporaryFile(mode='w+',delete=False)
	subl_reg_file.write(cleen_reg_file)
	subl_reg_file.close()
	# os.system('regedit /s "' +subl_reg_file.name+ '" && echo "plugin_unloaded" && pause')
	os.system('regedit /s "' +subl_reg_file.name+ '" ')


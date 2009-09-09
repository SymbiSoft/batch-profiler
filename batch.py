import e32
import time
import appuifw
import sys
import os
import codecs
import globalui
import key_codes
import msys # Extra module

KStart = time.time()
__title__ = "Batch Profile"
__version__ = "0.2"
__author__ = "madhacker"
__email__ = "madhacker.na@gmail.com"
__shell__ = 1

class _Main:
	def __init__(self):
		self.canvas = appuifw.Canvas(event_callback = None, redraw_callback = None, resize_callback = None)
		self.lock = e32.Ao_lock()
		appuifw.app.screen = 'normal'
		appuifw.app.title = unicode("%s %s" % (__title__, __version__))
		self.runprofilemenu = (u"Run", ((u"Profile 1", lambda:self.run_profile('profile1')), (u"Profile 2", lambda:self.run_profile('profile2')), (u"Profile 3", lambda:self.run_profile('profile3'))))
		self.profile1menu = (u"Profile 1", ((u"Add apps", lambda:self.add_prog('profile1')), (u"Add apps from task", lambda:self.add_prog_task('profile1')), (u"Remove App", lambda:self.edit_profile('profile1')), (u"Show Profile", lambda:self.show_profile('profile1'))))
		self.profile2menu = (u"Profile 2", ((u"Add apps", lambda:self.add_prog('profile2')), (u"Add apps from task", lambda:self.add_prog_task('profile2')), (u"Remove App", lambda:self.edit_profile('profile2')), (u"Show Profile", lambda:self.show_profile('profile2'))))
		self.profile3menu = (u"Profile 3", ((u"Add apps", lambda:self.add_prog('profile3')), (u"Add apps from task", lambda:self.add_prog_task('profile3')), (u"Remove App", lambda:self.edit_profile('profile3')), (u"Show Profile", lambda:self.show_profile('profile3'))))
		self.aboutmenu = (u"About", self.about)
		self.exitmenu = (u"Exit", self.quit)
		appuifw.app.menu = [self.runprofilemenu, self.profile1menu, self.profile2menu, self.profile3menu, self.aboutmenu, self.exitmenu]
		appuifw.app.body = self.canvas
		appuifw.app.exit_key_handler = self.quit

	def add_prog(self, profile):
		apps.show_list(profile)

	def add_prog_task(self, profile):
		apps.show_list(profile, task = 1)

	def edit_profile(self, profile):
		apps.show_programs(profile)

	def show_profile(self, profile):
		apps.show_only(profile)

	def about(self):
		appuifw.note(u"Author: %s\neMail: %s" % (__author__, __email__))

	def quit(self):
		self.lock.signal()
		if not __shell__: sys.exit()

	def run_profile(self, profile):
		try:
			self.settings = _Settings()
			self.progs = self.settings.read().get(profile, '').get('applications', '')
			self.settings = None
		except Exception, err:
			appuifw.note(unicode(err), "error")
			return
		if not len(self.progs) > 0: 
			appuifw.note(u"No applications in %s" % profile, "error")
			return
		print u"Starting %s" % profile
		for uid in self.progs:
			id = apps.find_in_list(uid)
			e32.start_exe(apps.lista_applicazioni[id][2], '')
			print u"Running '%s'" % apps.lista_applicazioni[id][0]
			e32.ao_sleep(0.1)

	def run(self):
		self.lock.wait()

class _Core:
	def __init__(self):
		try:
			self.lista_applicazioni = msys.listapp()
		except Exception, err:
			appuifw.note(unicode(err), 'error')
			self.lista_applicazioni = []
		try:
			self.lista_task = msys.listtask()
		except Exception, err:
			appuifw.note(unicode(err), 'error')
			self.lista_task = []
		self.task = 0
		self.programmi = []
		self.saving = {}

	def exit(self, query = 1):
		if query:
			if globalui.global_query(u"Save changes?"):	
				try:
					self.settings = _Settings()
					self.globalsettings = self.settings.read()
					self.settings = None
				except: self.globalsettings = {}
				self.settings = _Settings()
				self.saving["applications"] = self.programmi
				self.globalsettings[self.profile] = self.saving
				self.settings.save(self.globalsettings)
				self.settings = None
				print u"Saved"
		self.programmi = []
		appuifw.app.body = self.old_body
		appuifw.app.menu = self.old_menu
		appuifw.app.title = self.old_title
		appuifw.app.exit_key_handler = self.old_quit
		msys.option_text(self.old_option_text)
		msys.exit_text(self.old_exit_text)

	def check(self, name):
		if name.lower() in self.programmi:
			index = self.find_in_list(name.lower())
			if index == None: return 1
			appuifw.note(u"'%s' already exist in %s" % (self.lista_applicazioni[index][0], self.profile), "error")
			return 1
		return 0

	def delete_program(self):
		if not self.programmi: return
		appdelete = self.programmi[self.list_box.current()].lower()
		index = self.find_in_list(appdelete.lower())
		if index == None: return
		if globalui.global_query(u"Delete '%s'?" % self.lista_applicazioni[index][0]):
			self.programmi.remove(appdelete)
			appuifw.note(u"Deleted from %s" % self.profile, "conf")
			self._update_lb_profile()

	def find_in_list(self, name):
		i = 0
		for x in map(lambda x:x[1], self.lista_applicazioni):
			if x.lower() == name.lower():
				return i
			i += 1
		return None

	def add_program(self):
		if self.task:
			app = self.lista_task[self.list_box.current()][1].lower()
		else:
			app = self.lista_applicazioni[self.list_box.current()][1].lower()
		if self.check(app): return
		self.programmi.append( app )
		if self.task: name = self.lista_task[self.list_box.current()][0]
		else: name = self.lista_applicazioni[self.list_box.current()][0]
		appuifw.note(u"'%s' added in %s" % (name, self.profile), "conf")

	def _update_lb_profile(self, bind = 1):
		self.programmiscelti = []
		for a in map(lambda x:x, self.programmi):
			index = self.find_in_list(a.lower())
			if index == None: continue
			self.programmiscelti.append(self.lista_applicazioni[index])
		if self.programmiscelti == []:
			self.programmiscelti.append(u"< Empty >")
			self.list_box = appuifw.Listbox(map(lambda x:x, self.programmiscelti))
		else:
			self.list_box = appuifw.Listbox(map(lambda x:x[0], self.programmiscelti))
			# if bind: self.list_box.bind(key_codes.EKeySelect, self.delete_program)
			if bind: self.list_box.bind(key_codes.EKeyBackspace, self.delete_program)
		appuifw.app.body = self.list_box

	def _update_lb_list(self):
		if self.task: self.list_box = appuifw.Listbox(map(lambda x:x[0], self.lista_task))
		else: self.list_box = appuifw.Listbox(map(lambda x:x[0], self.lista_applicazioni))
		self.list_box.bind(key_codes.EKeySelect, self.add_program)
		appuifw.app.body = self.list_box

	def _preprare_(self):
		try:
			self.settings = _Settings()
			self.programmi = self.settings.read().get(self.profile, '').get('applications', '')
			self.settings = None
		except: pass
		self.old_quit = appuifw.app.exit_key_handler
		self.old_body = appuifw.app.body
		self.old_title = appuifw.app.title
		self.old_menu = appuifw.app.menu
		self.old_option_text = msys.option_text(u"Menu")
		self.old_exit_text = msys.exit_text(u"Back")

	def show_programs(self, profile):
		self.profile = profile
		self._preprare_()
		appuifw.app.menu = [(u"Delete", self.delete_program), (u"Back", self.exit)]
		appuifw.app.title = unicode("Edit %s" % profile)
		appuifw.app.exit_key_handler = self.exit
		self._update_lb_profile()

	def show_only(self, profile):
		self.profile = profile
		self._preprare_()
		appuifw.app.menu = [(u"Back", lambda:self.exit(query = 0))]
		appuifw.app.title = unicode("Show %s" % self.profile)
		appuifw.app.exit_key_handler = lambda:self.exit(query = 0)
		self._update_lb_profile(bind = 0)

	def show_list(self, profile, task = 0):
		self.profile = profile
		self.task = task
		self._preprare_()
		appuifw.app.menu = [(u"Add", self.add_program), (u"Back", self.exit)]
		appuifw.app.title = unicode("App List %s" % self.profile)
		appuifw.app.exit_key_handler = self.exit
		self._update_lb_list()

class _Settings:
	def __init__(self):
		self.KFileSettings = "%s\\settings.dat" % os.getcwd()

	def save(self, tuple):
		f = codecs.open(self.KFileSettings, 'wt')
		f.write(repr(tuple))
		f.close()

	def read(self):
		f = codecs.open(self.KFileSettings, 'rt')
		content = f.read()
		config = eval(content)
		f.close()
		return config

KNow = time.time()
KTimeForStart = KNow - KStart # In seconds
print u"%s sec to start" % int(KTimeForStart)
batch = _Main()
apps = _Core()
batch.run()
KEnd = time.time()
KTimeLogged = KEnd - KNow
print u"%s sec logged in %s %s" % (int(KTimeLogged), __title__, __version__)
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
__version__ = "0.3"
__author__ = "madhacker"
__email__ = "madhacker.na@gmail.com"
__shell__ = 1 # Define if it's a script or an application

class _UI:
	def __init__(self):
		self._first_run_()
		self.default_list_for_listbox = [(u"Profile 1 (DEF)", 'profile1')]
		self.lock = e32.Ao_lock()
		appuifw.app.screen = 'normal'
		self.set_profile(manual = 'profile1')
		appuifw.app.title = unicode("%s %s" % (__title__, __version__))
		self.operationmenu = (u"Operation", ((u"Add apps", self.add_prog), (u"Add apps from task", self.add_prog_task), (u"Remove App", self.edit_profile)))
		self.profilemenu = (u"Profile", ((u"Run", self.run_profile), (u"Show Profile", self.show_profile), (u"New Profile", self.new_profile), (u"Delete Profile", self.delete_profile)))
		self.aboutmenu = (u"About", self.about)
		self.exitmenu = (u"Exit", self.quit)
		self._prepare_main()

	def _first_run_(self):
		if not settings.check_file():
			globalui.global_msg_query(u"This is first run! Please ignore next error warning. Create a new profile to start.",u"1st run")

	def _prepare_main(self):
		self.list_for_listbox = []
		try:
			self.profili = settings.read()
			a = 1
			for y in self.profili.keys():
				self.list_for_listbox.append((u"Profile %s" % a, 'profile%s' % a))
				a += 1
			if not len(self.list_for_listbox) > 0: self.list_for_listbox = self.default_list_for_listbox
		except Exception, err:
			appuifw.note(unicode(err), "error")
			self.list_for_listbox = self.default_list_for_listbox
		appuifw.app.menu = [self.profilemenu, self.operationmenu, self.aboutmenu, self.exitmenu]
		self.list_box = appuifw.Listbox(map(lambda x:x[0], self.list_for_listbox))
		self.list_box.bind(key_codes.EKeySelect, self.set_profile)
		self.list_box.bind(key_codes.EKeyBackspace, self.delete_profile)
		appuifw.app.body = self.list_box
		appuifw.app.exit_key_handler = self.quit

	def new_profile(self):
		try:
			self.globalsettings = settings.read()
			self.newsettings = {}
		except: self.globalsettings = self.newsettings = {}
		a = 1
		for x in self.globalsettings.keys():
			self.newsettings['profile%s' % a] = self.globalsettings[x]
			a += 1
		if len(self.globalsettings.keys()) > 0:	id = a + 1
		else: id = 1
		self.newsettings['profile%s' % id] = {'applications': []}
		settings.save(self.newsettings)
		self._prepare_main()
		self.set_profile(manual = 'profile1')

	def delete_profile(self):
		if globalui.global_query(u"Delete '%s'?" % self.profile):
			try: self.progs = settings.read()
			except Exception, err:
				appuifw.note(unicode(err), "error")
				return
			if not len(self.progs.keys()) > 0: 
				appuifw.note(u"You cannot delete default profile", "error")
				return
			try:
				self.globalsettings = settings.read()
				self.newsettings = {}
			except: self.globalsettings = self.newsettings = {}
			a = 1
			for x in self.progs.keys():
				if not x == self.profile: 
					self.newsettings['profile%s' % a] = self.globalsettings[x]
					a += 1
			settings.save(self.newsettings)
			self._prepare_main()
			self.set_profile(manual = 'profile1')

	def run_profile(self):
		apps.show_list(self.profile)

	def add_prog(self):
		apps.show_list(self.profile)

	def add_prog_task(self):
		apps.show_list(self.profile, task = 1)

	def edit_profile(self):
		apps.show_programs(self.profile)

	def show_profile(self):
		apps.show_only(self.profile)

	def set_profile(self, manual = None):
		if manual != None: self.profile = manual
		else:
			self.profile = map(lambda x:x[1], self.list_for_listbox)[self.list_box.current()]
			appuifw.note(unicode("'%s' is set" % self.profile), "conf")
		msys.navitext(u"'%s' is active" % self.profile)

	def about(self):
		appuifw.note(u"Author: %s\neMail: %s" % (__author__, __email__))

	def quit(self):
		msys.navitext(u"")
		self.lock.signal()
		if not __shell__: sys.exit()

	def run_profile(self):
		try: self.progs = settings.read().get(self.profile, '').get('applications', '')
		except Exception, err:
			appuifw.note(unicode(err), "error")
			return
		if not len(self.progs) > 0: 
			appuifw.note(u"No applications in %s" % self.profile, "error")
			return
		print u"Starting %s" % self.profile
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
				try: self.globalsettings = settings.read()
				except: self.globalsettings = {}
				self.saving["applications"] = self.programmi
				self.globalsettings[self.profile] = self.saving
				settings.save(self.globalsettings)
				print u"Saved"
		self.programmi = []
		appuifw.app.body = self.old_body
		appuifw.app.menu = self.old_menu
		appuifw.app.title = self.old_title
		appuifw.app.exit_key_handler = self.old_quit
		msys.option_text(self.old_option_text)
		msys.exit_text(self.old_exit_text)
		batch._prepare_main()

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
			if bind: self.list_box.bind(key_codes.EKeyBackspace, self.delete_program)
		appuifw.app.body = self.list_box

	def _update_lb_list(self):
		if self.task: self.list_box = appuifw.Listbox(map(lambda x:x[0], self.lista_task))
		else: self.list_box = appuifw.Listbox(map(lambda x:x[0], self.lista_applicazioni))
		self.list_box.bind(key_codes.EKeySelect, self.add_program)
		appuifw.app.body = self.list_box

	def _preprare_(self):
		try: self.programmi = settings.read().get(self.profile, '').get('applications', '')
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

	def check_file(self):
		return os.path.exists(self.KFileSettings)

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
print u"%.2f sec to start" % KTimeForStart
settings = _Settings()
batch = _UI()
apps = _Core()
batch.run()
KEnd = time.time()
KTimeLogged = KEnd - KNow
print u"%.2f sec logged in %s %s" % (KTimeLogged, __title__, __version__)
"""Run the BEE2 application."""
from multiprocessing import freeze_support, set_start_method
import os
import sys
import builtins
from types import TracebackType
from typing import Type
import tkinter as tk

import wx
import srctools.logger

import utils

builtins._ = lambda t: str(t)  # this makes so that if _ is not defined we at least have a fallback

# We need to add dummy files if these are None - MultiProcessing tries to flush them.
if sys.stdout is None:
	sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
	sys.stderr = open(os.devnull, 'w')
if sys.stdin is None:
	sys.stdin = open(os.devnull, 'r')


if not sys.platform.startswith('win'):
	set_start_method('spawn')
freeze_support()


class App(wx.App):

	appName: str = 'bee2'
	TK_ROOT = tk.Tk()

	def OnPreInit(self):
		if len(sys.argv) > 1:
			logName = self.appName = sys.argv[1].lower()
			if self.appName not in ('backup', 'compilepane'):
				logName = 'bee2'
		else:
			logName = self.appName = 'bee2'

		# We need to initialise logging as early as possible - that way
		# it can record any errors in the initialisation of modules.
		utils.fix_cur_directory()
		LOGGER = srctools.logger.init_logging(
			str( utils.install_path( f'logs/{logName}.log' ) ),
			__name__,
			on_error=self.onError,
		)
		utils.setup_localisations( LOGGER )

		LOGGER.info( 'Arguments: {}', sys.argv )
		LOGGER.info( 'Running "{}", version {}:', self.appName, utils.BEE_VERSION )

	def OnInit(self):
		if self.appName == 'bee2':
			from app import BEE2
		elif self.appName == 'backup':
			from app import backup
			backup.init_application()
		elif self.appName == 'compilepane':
			from app import CompilerPane
			CompilerPane.init_application()
		elif self.appName.startswith('test_'):
			import importlib
			mod = importlib.import_module('app.' + sys.argv[1][5:])
			mod.test()
		else:
			wx.MessageDialog(
				parent=None,
				message=f'Invalid component name "{self.appName}", valid names are:\n - bee2\n - backup\n - compilepane',
				caption='Invalid component name'
			).Show()

	def onError(self, exc_type: Type[BaseException], exc_value: BaseException, exc_tb: TracebackType, ) -> None:
		"""Run when the application crashes. Display to the user, log it, and quit."""
		# We don't want this to fail, so import everything here, and wrap in
		# except Exception.
		import traceback

		err = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))

		# Grab and release the grab so nothing else can block the error message.
		try:
			TK_ROOT.grab_set_global()
			TK_ROOT.grab_release()

			# Append traceback to the clipboard.
			TK_ROOT.clipboard_append(err)
		except Exception:
			pass

		if not issubclass(exc_type, Exception):
			# It's subclassing BaseException (KeyboardInterrupt, SystemExit),
			# so ignore the error.
			return

		# Put it onscreen.
		try:
			from tkinter import messagebox
			messagebox.showinfo(
				title=f'BEEMOD {utils.BEE_VERSION} Error!',
				message='An error occurred: \n{err}\n\nThis has been copied to the clipboard.',
				icon=messagebox.ERROR,
			)
		except Exception:
			pass

		try:
			from BEE2_config import GEN_OPTS
			# Try to turn on the logging window for next time..
			GEN_OPTS.load()
			GEN_OPTS['Debug']['show_log_win'] = '1'
			GEN_OPTS['Debug']['window_log_level'] = 'DEBUG'
			GEN_OPTS.save()
		except Exception:
			# Ignore failures...
			pass

if __name__ == '__main__':
	app = App()
	app.MainLoop()


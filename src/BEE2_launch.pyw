"""Run the BEE2 application."""
from multiprocessing import freeze_support, set_start_method
import os
import sys

import wx
import srctools.logger

from app import on_error, TK_ROOT
import utils

# We need to add dummy files if these are None - MultiProccessing tries to flush
# them.
if sys.stdout is None:
	sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
	sys.stderr = open(os.devnull, 'w')
if sys.stdin is None:
	sys.stdin = open(os.devnull, 'r')

if sys.platform == "darwin":
	# Disable here, can't get this to work.
	sys.modules['pyglet'] = None

if not sys.platform.startswith('win'):
	set_start_method('spawn')
freeze_support()


class App(wx.App):

	app_name: str
	instanceChecker = wx.SingleInstanceChecker('BEEmod')
	ShouldExit: bool = False

	def OnPreInit(self):
		if self.instanceChecker.IsAnotherRunning():
			self.ShouldExit = True
			return
		if not utils.FROZEN:
			os.environ['SRCTOOLS_DEBUG'] = '1'
		if len( sys.argv ) > 1:
			log_name = self.app_name = sys.argv[ 1 ].lower()
			if self.app_name not in ('backup', 'compilepane'):
				log_name = 'bee2'
		else:
			log_name = self.app_name = 'bee2'

		# We need to initialise logging as early as possible - that way
		# it can record any errors in the initialisation of modules.
		utils.fix_cur_directory()
		LOGGER = srctools.logger.init_logging(
			str( utils.install_path( f'logs/{log_name}.log' if getattr(sys, 'frozen', False) else f'run/logs/{log_name}.log' ) ),
			__name__,
			on_error=on_error,
		)
		utils.setup_localisations( LOGGER )

		LOGGER.info( 'Arguments: {}', sys.argv )
		LOGGER.info( 'Running "{}", version {}:', self.app_name, utils.BEE_VERSION )

	def OnInit(self):
		if self.ShouldExit:
			print('Another instance of BEEmod is running, aborting.')
			return False
		from app.UIwx import Root
		window = Root()
		self.SetTopWindow( window )
		if self.app_name == 'bee2':
			from app import BEE2
			BEE2.BEEmod()
		elif self.app_name == 'backup':
			from app import backup
			backup.init_application()
		elif self.app_name == 'compilepane':
			from app import CompilerPane
			CompilerPane.init_application()
		else:
			raise ValueError( f'Invalid component name "{self.app_name}"!' )
		return True


if __name__ == '__main__':
	app = App()
	app.MainLoop()

from typing import Union, Callable

import wx
import srctools.logger

import utils

if __name__ == '__main__':
	LOGGER = srctools.logger.init_logging(
		str( utils.install_path( 'run/logs/bee2.log' ) ),
		__name__
	)
	utils.setup_localisations( LOGGER )

import BEE2_config
from BEE2_config import GEN_OPTS
from app import sound, gameMan, backup, packageMan, optionWindow
from loadScreen import main_loader

if __name__ == '':
	from gettext import gettext as _


LOGGER = srctools.logger.get_logger(__name__)

item_opts = BEE2_config.ConfigFile( 'item_configs.cfg' )
idindex: int = -1


class Root(wx.Frame):

	selectedPalette: int = 0
	# Holds the WX Toplevels, frames, widgets and menus
	# TODO: actually remove this, idk if those are used for something, but until i find out, just include them
	windows = {}
	frames = {}
	UI = {}
	menus = {}

	def __init__(self):
		super(Root, self).__init__(
			parent=None,
			title='BEE2.4'
		)
		# sound.load_snd()
		# main_loader.step('UI') not done

		# here the menu bar is made
		bar = wx.MenuBar()
		# all the menus
		file_menu = self.menus['file'] = wx.Menu()
		create_item( file_menu, 'Export', lambda: print(), utils.KEY_ACCEL[ "KEY_EXPORT" ] )
		create_item( file_menu, 'Add Game', gameMan.add_game )
		create_item( file_menu, 'Uninstall from Selected Game', gameMan.remove_game )
		create_item( file_menu, 'Backup/Restore Puzzles...', backup.show_window )
		create_item( file_menu, 'Manage Packages...', packageMan.show)
		file_menu.AppendSeparator()
		create_item( file_menu, 'Options', optionWindow.show)
		if not utils.MAC:
			create_item( file_menu, 'Quit', self.QuitApplication)

		bar.Append(menu=file_menu, title=_('File') )
		self.SetMenuBar(bar)

		self.Bind(wx.EVT_CLOSE, self.QuitApplication)
		self.Show()

	def QuitApplication( self, evt: Union[wx.CloseEvent, wx.MenuEvent] = None ):
		""" Do a last-minute save of our config files, and quit the app. """
		import logging
		GEN_OPTS[ 'win_state' ][ 'main_window_x' ] = str( self.GetPosition().Get()[0] )
		GEN_OPTS[ 'win_state' ][ 'main_window_y' ] = str( self.GetPosition().Get()[0] )

		BEE2_config.write_settings()
		GEN_OPTS.save_check()
		item_opts.save_check()
		# TODO: reenable this
		# CompilerPane.COMPILE_CFG.save_check()
		gameMan.save()
		logging.shutdown()
		self.Destroy()

	def LoadSettings( self ):
		""" Load options from the general config file. """
		try:
			self.selectedPalette = GEN_OPTS.get_int('Last_Selected', 'palette')
		except (KeyError, ValueError):
			pass  # It'll be set to the first palette by default, and then saved
		# selectedPalette_radio
		GEN_OPTS.has_changed = False

		# optionWindow.load()


gameMan.quit_application = lambda: wx.GetTopLevelWindows()[0].QuitApplication()


def create_item( menu: wx.Menu, label: str, command: Callable[ [ wx.MenuEvent ], None ], accelerator: str = None ) -> wx.MenuItem:
	global idindex
	idindex += 1
	accelerator = f'\t{accelerator}' if accelerator is not None else ''
	item: wx.MenuItem = menu.Append( id=idindex, item=_(label) + accelerator )
	menu.Bind(wx.EVT_MENU, command)
	return item


if __name__ == '__main__':
	app = wx.App()
	frm = Root()
	app.SetTopWindow(frm)
	frm.Show()
	app.MainLoop()

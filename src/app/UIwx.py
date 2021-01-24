from typing import Union, Callable, Dict
import webbrowser as wb

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
from app import sound, gameMan, backup, packageMan, optionWindow, helpMenu
from loadScreen import main_loader

if __name__ == '':
	from gettext import gettext as _


LOGGER = srctools.logger.get_logger(__name__)

item_opts = BEE2_config.ConfigFile( 'item_configs.cfg' )
_menuIndex: int = 0


def newMenuIndex() -> int:
	global _menuIndex
	_menuIndex += 1
	return _menuIndex - 1


class Root(wx.Frame):

	selectedPalette: int = 0
	# Holds the WX Toplevels, frames, widgets and menus
	# TODO: actually remove this, idk if those are used for something, but until i find out, just include them
	windows = {}
	frames = {}
	UI = {}
	menus: Dict[str, wx.Menu] = {}
	menu_items: Dict[str, wx.MenuItem] = {}

	def __init__(self):
		super(Root, self).__init__(
			parent=None,
			title='BEE2.4'
		)
		# sound.load_snd()
		# main_loader.step('UI') not done

		# here the menu bar is made
		bar = wx.MenuBar()
		# construct the menu bar
		# file menu
		self.menus['file'] = file_menu = wx.Menu()
		self.menu_items['Export'] = file_menu.Append(newMenuIndex(), f'{_("Export")}\t{utils.KEY_ACCEL[ "KEY_EXPORT" ]}' )
		self.menu_items['Add Game'] = file_menu.Append(newMenuIndex(), _('Add Game') )
		self.menu_items['Uninstall from Selected Game'] = file_menu.Append(newMenuIndex(), _('Uninstall from Selected Game') )
		self.menu_items['Backup/Restore Puzzles...'] = file_menu.Append(newMenuIndex(), _('Backup/Restore Puzzles...') )
		self.menu_items['Manage Packages...'] = file_menu.Append(newMenuIndex(), _('Manage Packages...') )
		file_menu.AppendSeparator()
		self.menu_items['Options'] = file_menu.Append(newMenuIndex(), _('Options') )
		self.menu_items['Quit'] = file_menu.Append( newMenuIndex(), _('Quit') )
		file_menu.AppendSeparator()
		for game in gameMan.all_games:
			self.menu_items[game.name] = file_menu.AppendRadioItem(newMenuIndex(), game.name)
			self.Bind(wx.EVT_MENU, self.SetGame, self.menu_items[game.name])
		bar.Append(menu=file_menu, title=_('File') )

		# palette menu
		self.menus['pal'] = pal_menu = wx.Menu()
		self.menu_items['Clear'] = pal_menu.Append( newMenuIndex(), _('Clear') )
		self.menu_items['Delete Palette'] = pal_menu.Append( newMenuIndex(), _('Delete Palette') )
		self.menu_items['Fill Palette'] = pal_menu.Append( newMenuIndex(), _('Fill Palette') )
		pal_menu.AppendSeparator()
		self.menu_items['Save Settings in Palettes'] = pal_menu.AppendCheckItem( newMenuIndex(), _('Save Settings in Palettes') )
		pal_menu.AppendSeparator()
		self.menu_items['Save Palette'] = pal_menu.Append( newMenuIndex(), f'{_("Save Palette")}\t{utils.KEY_ACCEL["KEY_SAVE"]}' )
		self.menu_items['Save Palette As...'] = pal_menu.Append( newMenuIndex(), f'{_("Save Palette As...")}\t{utils.KEY_ACCEL["KEY_SAVE_AS"]}' )
		pal_menu.AppendSeparator()
		bar.Append(menu=pal_menu, title=_('Palette') )

		# help menu
		self.menus['Help'] = help_menu = wx.Menu()
		for res in helpMenu.WEB_RESOURCES:
			if res is helpMenu.SEPERATOR:
				help_menu.AppendSeparator()
			else:
				self.menu_items[] help_menu.Append()

		bar.Append( menu=help_menu, title=_( 'Help' ) )

		# set the bar
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

	# menu items events
	def SetGame( self, evt: wx.MenuEvent ):
		# gameMan.selected_game =
		pass


gameMan.quit_application = lambda: wx.GetTopLevelWindows()[0].QuitApplication()


def openUrl(url: str):
	"""
	opens an url with the default browser
	:param url: the url to open
	"""
	LOGGER.info(f'opening "{url}" with default browser')
	wb.open(url)


if __name__ == '__main__':
	app = wx.App()
	frm = Root()
	app.SetTopWindow(frm)
	frm.Show()
	app.MainLoop()

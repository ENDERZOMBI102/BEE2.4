"""
This module provides a wrapper around Pyglet, in order to play sounds easily.
To use, call sound.fx() with one of the dict keys.
If PyGame fails to load, all fx() calls will fail silently.
(Sounds are not critical to the app, so they just won't play.)
"""
import os
from io import BytesIO
from tkinter import Event
from typing import IO, Optional, Callable, Union, Dict
import wx.adv, wx.media
from pydub import AudioSegment

import utils

from app import TK_ROOT
from srctools.filesys import FileSystemChain, FileSystem, RawFileSystem
import srctools.logger

__all__ = [
	'SOUNDS', 'SamplePlayer',

	'pyglet_version', 'initiallised',
	'load_snd', 'play_sound', 'fx',
	'fx_blockable', 'block_fx',
]

LOGGER = srctools.logger.get_logger(__name__)

play_sound = True

# This starts holding the filenames, but then caches the actual sound object.
SOUNDS: Dict[str, Union[str, wx.adv.Sound]] = {
	'select': 'rollover',
	'add': 'increment',
	'config': 'reconfig',
	'subtract': 'decrement',
	'connect': 'connection_made',
	'disconnect': 'connection_destroyed',
	'expand': 'extrude',
	'delete': 'collapse',
	'error': 'error',
	'contract': 'carve',
	'raise_1': 'panel_raise_01',
	'raise_2': 'panel_raise_02',
	'raise_3': 'panel_raise_03',
	'lower_1': 'panel_lower_01',
	'lower_2': 'panel_lower_02',
	'lower_3': 'panel_lower_03',
	'move': 'reconfig',
	'swap': 'extrude',
}

# for name in SOUNDS.keys():
# 	SOUNDS[name] += '.ogg'


initiallised = True
_play_repeat_sfx = True


def load_snd() -> None:
	"""Load all the sounds."""
	for name, fname in SOUNDS.items():
		LOGGER.info( f'Loading sound "{name}" -> sounds/{fname}' )
		buf = BytesIO()
		AudioSegment.from_ogg( utils.install_path( f'sounds/{fname}' ) ).export( buf, format='WAV' )
		SOUNDS[ name ] = wx.adv.Sound()
		SOUNDS[ name ].CreateFromData( buf.read() )


def fx( name, e=None ):
	"""Play a sound effect stored in the sounds{} dict."""
	if not play_sound:
		return
	# Defer loading these until we actually need them, speeds up
	# startup a little.
	try:
		SOUNDS[ name ].Play()
	except KeyError:
		raise ValueError( f'Not a valid sound? "{name}"' )
	except AttributeError:
		LOGGER.warning( f'load_snd() not called when playing "{name}"?' )


def _reset_fx_blockable() -> None:
	"""Reset the fx_norep() call after a delay."""
	global _play_repeat_sfx
	_play_repeat_sfx = True

def fx_blockable(sound: str) -> None:
	"""Play a sound effect.

	This waits for a certain amount of time between retriggering sounds
	so they don't overlap.
	"""
	global _play_repeat_sfx
	if play_sound and _play_repeat_sfx:
		fx(sound)
		_play_repeat_sfx = False
		TK_ROOT.after(75, _reset_fx_blockable)

def block_fx():
	"""Block fx_blockable() for a short time."""
	global _play_repeat_sfx
	_play_repeat_sfx = False
	TK_ROOT.after(50, _reset_fx_blockable)

class SamplePlayer:
	"""Handles playing a single audio file, and allows toggling it on/off."""
	def __init__(
			self,
			start_callback:  Callable[[], None],
			stop_callback:  Callable[[], None],
			system: FileSystemChain,
	) -> None:
		"""Initialise the sample-playing manager.
		"""
		self.sample: Optional[Source] = None
		self.start_time: float = 0   # If set, the time to start the track at.
		self.after: Optional[str] = None
		self.start_callback: Callable[[], None] = start_callback
		self.stop_callback: Callable[[], None] = stop_callback
		self.cur_file: Optional[str] = None
		# The system we need to cleanup.
		self._handle: Optional[IO[bytes]] = None
		self._cur_sys: Optional[FileSystem] = None
		self.system: FileSystemChain = system

	@property
	def is_playing(self):
		"""Is the player currently playing sounds?"""
		return self.sample is not None

	def _close_handles(self) -> None:
		"""Close down previous sounds."""
		if self._handle is not None:
			self._handle.close()
		if self._cur_sys is not None:
			self._cur_sys.close_ref()
		self._handle = self._cur_sys = None

	def play_sample(self, e: Event=None) -> None:
		pass
		"""Play a sample of music.

		If music is being played it will be stopped instead.
		"""
		if self.cur_file is None:
			return

		if self.sample is not None:
			self.stop()
			return

		self._close_handles()

		with self.system:
			try:
				file = self.system[self.cur_file]
			except (KeyError, FileNotFoundError):
				self.stop_callback()
				LOGGER.error(f'Sound sample not found: "{self.cur_file}"')
				return  # Abort if music isn't found..

			child_sys = self.system.get_system(file)
			# Special case raw filesystems - Pyglet is more efficient
			# if it can just open the file itself.
			if isinstance(child_sys, RawFileSystem):
				load_path = os.path.join(child_sys.path, file.path)
				self._cur_sys = self._handle = None
				LOGGER.debug(f'Loading music directly from {load_path}')
			else:
				# Use the file objects directly.
				self._cur_sys = child_sys
				self._cur_sys.open_ref()
				self._handle = file.open_bin()
				LOGGER.debug(f'Loading music via {self._handle}')
				self.sample = wx.adv.Sound()
				try:
					if file.path.endswith('.wav'):
						self.sample.CreateFromData(self._handle)
					else:
						buf = BytesIO()
						AudioSegment.from_file( self._handle ).export( buf, format='WAV' )
						self.sample.CreateFromData( buf )
				except ():
					self.stop_callback()
					LOGGER.exception(f'Sound sample not valid: "{self.cur_file}"')
					return  # Abort if music isn't found..

		# if self.start_time:
		# 	try:
		# 		sound.seek(self.start_time)
		# 	except CannotSeekException:
		# 		LOGGER.exception(f'Cannot seek in "{self.cur_file}"!')

		self.sample.Play()
		self.after = TK_ROOT.after(
			int(200 * 1000),
			self._finished,
		)
		self.start_callback()

	def stop(self) -> None:
		"""Cancel the music, if it's playing."""
		if self.sample is None:
			return

		self.sample.Stop()
		self.sample = None
		self._close_handles()
		self.stop_callback()

		if self.after is not None:
			TK_ROOT.after_cancel(self.after)
			self.after = None

	def _finished(self) -> None:
		"""Reset values after the sound has finished."""
		print('finished')
		self.sample = None
		self.after = None
		self._close_handles()
		self.stop_callback()


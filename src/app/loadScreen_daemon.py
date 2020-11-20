from typing import Tuple, Union

import wx

from app.canvas import Canvas, CanvasRectangle
import app.img as img


class SplashScreen:

	def __init__(self):
		self.lrg = SplashScreenLarge(self)
		self.lrg.OnClose = self.OnClose
		self.sml = SplashScreenSmall(self)
		self.sml.OnClose = self.OnClose
		self.sml.SetPosition( self.lrg.GetPosition() )

	def Toggle( self ):
		if self.lrg.IsShown():
			self.lrg.Show( False )
			self.sml.SetPosition( self.lrg.GetPosition() )
			self.sml.Show( True )
		else:
			self.sml.Show( False )
			self.lrg.SetPosition( self.sml.GetPosition() )
			self.lrg.Show( True )

	def OnClose( self ):
		"""
		overwrite to get the event
		"""
		self.Destroy()

	def Destroy( self ):
		self.sml.Destroy()
		self.lrg.Destroy()


class SplashScreenSmall(wx.Frame):

	screenSize: wx.Size
	splashScreen: SplashScreen
	initDrag: Union[Tuple[int, int], None] = None

	def __init__(self, ss: SplashScreen):
		self.screenSize = wx.ScreenDC().GetSize().Get()
		super(SplashScreenSmall, self).__init__(
			parent=None,
			size=wx.Size(
				int( min( self.screenSize[ 0 ] * 0.5, 400 ) ),
				int( min( self.screenSize[ 1 ] * 0.5, 175 ) )
			),
			style=wx.BORDER_NONE | wx.FRAME_NO_WINDOW_MENU
		)
		self.splashScreen = ss
		self.canvas = Canvas( parent=self )

		# close button
		self.close_btn = self.canvas.CreateRectangle(
			pos=wx.Point2D( self.GetSize()[ 0 ] - 20, 0 ),
			width=20,
			height=20,
			fillColor=wx.ColourDatabase().Find( 'DARK GREEN' ),
			lineColor=wx.ColourDatabase().Find( 'DARK GREEN' ),
			layer=1
		)
		self.canvas.CreateLine(
			wx.Point( self.GetSize()[ 0 ] - 16, 4 ),
			wx.Point( self.GetSize()[ 0 ] - 4, 16 ),
			width=2,
			layer=1
		)
		self.canvas.CreateLine(
			wx.Point( self.GetSize()[ 0 ] - 4, 4 ),
			wx.Point( self.GetSize()[ 0 ] - 16, 16 ),
			width=2,
			layer=1
		)

		# resize button
		self.resize_btn = self.canvas.CreateRectangle(
			pos=wx.Point2D( self.GetSize()[ 0 ] - 40, 0 ),
			width=20,
			height=20,
			fillColor=wx.ColourDatabase().Find( 'DARK GREEN' ),
			lineColor=wx.ColourDatabase().Find( 'DARK GREEN' ),
			layer=1
		)
		self.canvas.CreateLine(
			wx.Point( self.GetSize()[ 0 ] - 20 - 4, 4 ),
			wx.Point( self.GetSize()[ 0 ] - 20 - 16, 4 ),
			width=2,
			layer=1
		)
		self.canvas.CreateLine(
			wx.Point( self.GetSize()[ 0 ] - 20 - 4, 4 ),
			wx.Point( self.GetSize()[ 0 ] - 20 - 4, 16 ),
			width=2,
			layer=1
		)
		self.canvas.CreateLine(
			wx.Point( self.GetSize()[ 0 ] - 24, 4 ),
			wx.Point( self.GetSize()[ 0 ] - 36, 16 ),
			width=2,
			layer=1
		)

		# bind events
		self.canvas.Bind( wx.EVT_LEFT_DOWN, self.OnMouseClick )
		self.canvas.Bind( wx.EVT_LEFT_UP, self.OnMouseClick )
		self.canvas.Bind( wx.EVT_MOTION, self.OnMouseMove )

	def OnMouseClick( self, evt: wx.MouseEvent ):
		if self.close_btn.GetBoundingBox().IsInside( evt.GetPosition() ) and evt.LeftIsDown():
			self.splashScreen.Destroy()
		elif self.resize_btn.GetBoundingBox().IsInside( evt.GetPosition() ) and evt.LeftIsDown():
			self.splashScreen.Toggle()
		elif evt.LeftIsDown():
			self.initDrag = evt.GetPosition().Get()
		else:
			self.initDrag = None
		if evt.LeftIsDown():
			print( 'mouse position: ' + str( evt.GetPosition().Get() ) )

	def OnMouseMove( self, evt: wx.MouseEvent ):
		if evt.Dragging() and (self.initDrag is not None):
			self.SetPosition(
				wx.Point(
					self.GetPosition().Get()[ 0 ] + (evt.GetX() - self.initDrag[ 0 ]),
					self.GetPosition().Get()[ 1 ] + (evt.GetY() - self.initDrag[ 1 ])
				)
			)


class SplashScreenLarge(wx.Frame):

	compact: bool = False
	initDrag: Union[Tuple[int, int], None] = None
	screenSize: Tuple[int, int]

	frameLargeSize: wx.Size
	frameCompactSize: wx.Size

	close_btn: CanvasRectangle
	resize_btn: CanvasRectangle

	splashScreen: SplashScreen

	def __init__(self, ss: SplashScreen):
		self.screenSize = wx.ScreenDC().GetSize().Get()

		super(SplashScreenLarge, self).__init__(
			parent=None,
			size=wx.Size(
				int( max( self.screenSize[ 0 ] * 0.6, 500 ) ),
				int( max( self.screenSize[ 1 ] * 0.6, 400 ) )
			),
			style=wx.BORDER_NONE | wx.FRAME_NO_WINDOW_MENU
		)
		self.CenterOnScreen()

		self.splashScreen = ss
		# <app.canvas.Canvas object at 0x0000020ECC4938B8>
		self.canvas = Canvas( parent=self )

		# close button
		self.close_btn = self.canvas.CreateRectangle(
			pos=wx.Point2D( self.GetSize()[ 0 ] - 20, 0 ),
			width=20,
			height=20,
			fillColor=wx.ColourDatabase().Find( 'DARK GREEN' ),
			lineColor=wx.ColourDatabase().Find( 'DARK GREEN' ),
			layer=1
		)
		self.canvas.CreateLine(
			wx.Point( self.GetSize()[ 0 ] - 16, 4 ),
			wx.Point( self.GetSize()[ 0 ] - 4, 16 ),
			width=2,
			layer=1
		)
		self.canvas.CreateLine(
			wx.Point( self.GetSize()[ 0 ] - 4, 4 ),
			wx.Point( self.GetSize()[ 0 ] - 16, 16 ),
			width=2,
			layer=1
		)

		# resize button
		self.resize_btn = self.canvas.CreateRectangle(
			pos=wx.Point2D( self.GetSize()[ 0 ] - 40, 0 ),
			width=20,
			height=20,
			fillColor=wx.ColourDatabase().Find( 'DARK GREEN' ),
			lineColor=wx.ColourDatabase().Find( 'DARK GREEN' ),
			layer=1
		)
		self.canvas.CreateLine(
			wx.Point( self.GetSize()[ 0 ] - 36, 16 ),
			wx.Point( self.GetSize()[ 0 ] - 24, 16 ),
			width=2,
			layer=1
		)
		self.canvas.CreateLine(
			wx.Point( self.GetSize()[ 0 ] - 36, 16 ),
			wx.Point( self.GetSize()[ 0 ] - 36, 4 ),
			width=2,
			layer=1
		)
		self.canvas.CreateLine(
			wx.Point( self.GetSize()[ 0 ] - 24, 4 ),
			wx.Point( self.GetSize()[ 0 ] - 36, 16 ),
			width=2,
			layer=1
		)

		# BEE logo
		self.canvas.CreateImage(
			img.png( './../images/BEE2/splash_logo.png', wxImg=True ),
			wx.Point( 10, 10 ),
			layer=1
		)

		# texts
		text = self.canvas.CreateText(
			text='Better Extended Editor for Portal 2',
			pos=wx.Point( 10, 125 ),
			color=wx.ColourDatabase().Find( 'WHITE' ),
			font=wx.Font( wx.FontInfo( 14 ).FaceName( 'DIN' ).Bold( True ) ),
			layer=1
		)
		versionText = self.canvas.CreateText(
			text='Version: (dev)',
			pos=wx.Point( 10, 145 ),
			color=wx.ColourDatabase().Find( 'WHITE' ),
			font=wx.Font( wx.FontInfo( 14 ).FaceName( 'DIN' ).Bold( True ) ),
			layer=1
		)

		text1_bbox: Tuple[int, int, int, int] = (
			text.GetBoundingBox().GetTopLeft().Get()[ 0 ],
			text.GetBoundingBox().GetTopLeft().Get()[ 1 ],
			text.GetBoundingBox().GetBottomRight().Get()[ 0 ],
			text.GetBoundingBox().GetBottomRight().Get()[ 1 ]
		)
		text2_bbox: Tuple[int, int, int, int] = (
			versionText.GetBoundingBox().GetTopLeft().Get()[ 0 ],
			versionText.GetBoundingBox().GetTopLeft().Get()[ 1 ],
			versionText.GetBoundingBox().GetBottomRight().Get()[ 0 ],
			versionText.GetBoundingBox().GetBottomRight().Get()[ 1 ]
		)

		# background image + shadows + gradient
		self.canvas.CreateImage(
			image=img.make_splash_screen(
				max_width=self.GetSize().Get()[ 0 ],
				max_height=self.GetSize().Get()[ 1 ],
				base_height=80,
				text1_bbox=text1_bbox,
				text2_bbox=text2_bbox,
				wxImg=True
			),
			pos=wx.Point( 0, 0 )
		)
		self.canvas.Bind( wx.EVT_LEFT_DOWN, self.OnMouseClick )
		self.canvas.Bind( wx.EVT_LEFT_UP, self.OnMouseClick )
		self.canvas.Bind( wx.EVT_MOTION, self.OnMouseMove )
		self.Show()

	# to move the window + react to buttons
	def OnMouseClick(self, evt: wx.MouseEvent):
		if self.close_btn.GetBoundingBox().IsInside( evt.GetPosition() ) and evt.LeftDown():
			self.splashScreen.Destroy()
		elif self.resize_btn.GetBoundingBox().IsInside( evt.GetPosition() ) and evt.LeftDown():
			self.splashScreen.Toggle()
		elif evt.LeftDown():
			self.initDrag = evt.GetPosition().Get()
		else:
			self.initDrag = None
		if evt.LeftDown():
			print( 'mouse position: '+str(evt.GetPosition().Get()) )

	def OnMouseMove(self, evt: wx.MouseEvent):
		if evt.Dragging() and ( self.initDrag is not None ):
			self.SetPosition(
				wx.Point(
					self.GetPosition().Get()[0] + ( evt.GetX() - self.initDrag[0] ),
					self.GetPosition().Get()[1] + ( evt.GetY() - self.initDrag[1] )
				)
			)


if __name__ == '__main__':
	app = wx.App()
	splashScreen = SplashScreen()
	app.MainLoop()

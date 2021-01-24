from typing import Tuple, Union

import wx

from app.canvas import Canvas, CanvasRectangle
import app.img as img


class SplashScreen(wx.Frame):

	compact: bool = False
	initDrag: Union[Tuple[int, int], None] = None
	screenSize: Tuple[int, int]

	frameLargeSize: wx.Size
	frameCompactSize: wx.Size

	largeCanvas: Canvas
	compactCanvas: Canvas

	close_btn: CanvasRectangle
	resize_btn: CanvasRectangle

	def __init__(self):
		self.screenSize = wx.ScreenDC().GetSize().Get()

		# sizes
		self.frameLargeSize = wx.Size(
			int( max( self.screenSize[ 0 ] * 0.6, 500 ) ),
			int( max( self.screenSize[ 1 ] * 0.6, 400 ) )
		)
		self.frameCompactSize = wx.Size(
			int( min( self.screenSize[ 0 ] * 0.5, 400 ) ),
			int( min( self.screenSize[ 1 ] * 0.5, 175 ) )
		)

		super(SplashScreen, self).__init__(
			parent=None,
			size=self.frameLargeSize,
			style=wx.BORDER_NONE | wx.FRAME_NO_WINDOW_MENU
		)
		self.CenterOnScreen()

		self.largeCanvas = Canvas( parent=self )
		self.compactCanvas = Canvas( parent=self )
		self.compactCanvas.Show( False )
		self.compactCanvas.Enable( False )
		buttonColor: wx.Colour = wx.Colour( '#00785A' )

		# LARGE CANVAS

		# close button
		self.close_btn = self.largeCanvas.CreateRectangle(
			pos=wx.Point( self.frameLargeSize[ 0 ] - 20, 0 ),
			width=20,
			height=20,
			fillColor=buttonColor,
			lineColor=buttonColor,
			layer=1
		)
		self.largeCanvas.CreateLine(
			wx.Point( self.frameLargeSize[ 0 ] - 16, 4 ),
			wx.Point( self.frameLargeSize[ 0 ] - 4, 16 ),
			width=2,
			layer=1
		)
		self.largeCanvas.CreateLine(
			wx.Point( self.frameLargeSize[ 0 ] - 4, 4 ),
			wx.Point( self.frameLargeSize[ 0 ] - 16, 16 ),
			width=2,
			layer=1
		)

		# resize button
		self.resize_btn = self.largeCanvas.CreateRectangle(
			pos=wx.Point( self.frameLargeSize[ 0 ] - 40, 0 ),
			width=20,
			height=20,
			fillColor=buttonColor,
			lineColor=buttonColor,
			layer=1
		)
		self.largeCanvas.CreateLine(
			wx.Point( self.frameLargeSize[ 0 ] - 36, 16 ),
			wx.Point( self.frameLargeSize[ 0 ] - 24, 16 ),
			width=2,
			layer=1
		)
		self.largeCanvas.CreateLine(
			wx.Point( self.frameLargeSize[ 0 ] - 36, 16 ),
			wx.Point( self.frameLargeSize[ 0 ] - 36, 4 ),
			width=2,
			layer=1
		)
		self.largeCanvas.CreateLine(
			wx.Point( self.frameLargeSize[ 0 ] - 24, 4 ),
			wx.Point( self.frameLargeSize[ 0 ] - 36, 16 ),
			width=2,
			layer=1
		)

		# BEE logo
		self.largeCanvas.CreateImage(
			img.png( './../images/BEE2/splash_logo.png', wxImg=True ),
			wx.Point( 10, 10 ),
			layer=1
		)

		# texts
		text = self.largeCanvas.CreateText(
			text='Better Extended Editor for Portal 2',
			pos=wx.Point( 10, 125 ),
			color=wx.ColourDatabase().Find( 'WHITE' ),
			font=wx.Font( wx.FontInfo( 14 ).FaceName( 'DIN' ).Bold( True ) ),
			layer=1
		)
		versionText = self.largeCanvas.CreateText(
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
		self.largeCanvas.CreateImage(
			image=img.make_splash_screen(
				max_width=self.frameLargeSize.Get()[ 0 ],
				max_height=self.frameLargeSize.Get()[ 1 ],
				base_height=80,
				text1_bbox=text1_bbox,
				text2_bbox=text2_bbox,
				wxImg=True
			),
			pos=wx.Point( 0, 0 )
		)

		# COMPACT CANVAS

		# background
		# self.compactCanvas.SetBackgroundColour( wx.Colour( '#009678' ) )

		# close button
		self.cclose_btn = self.compactCanvas.CreateRectangle(
			pos=wx.Point( self.frameCompactSize[ 0 ] - 20, 0 ),
			width=20,
			height=20,
			fillColor=buttonColor,
			lineColor=buttonColor,
			layer=0
		)
		self.compactCanvas.CreateLine(
			wx.Point( self.frameCompactSize[ 0 ] - 16, 4 ),
			wx.Point( self.frameCompactSize[ 0 ] - 4, 16 ),
			width=2,
			layer=0
		)
		self.compactCanvas.CreateLine(
			wx.Point( self.frameCompactSize[ 0 ] - 4, 4 ),
			wx.Point( self.frameCompactSize[ 0 ] - 16, 16 ),
			width=2,
			layer=0
		)

		# resize button
		self.cresize_btn = self.compactCanvas.CreateRectangle(
			pos=wx.Point( self.frameCompactSize[ 0 ] - 40, 0 ),
			width=20,
			height=20,
			fillColor=buttonColor,
			lineColor=buttonColor,
			layer=0
		)
		self.compactCanvas.CreateLine(
			wx.Point( self.frameCompactSize[ 0 ] - 20 - 4, 4 ),
			wx.Point( self.frameCompactSize[ 0 ] - 20 - 16, 4 ),
			width=2,
			layer=0
		)
		self.compactCanvas.CreateLine(
			wx.Point( self.frameCompactSize[ 0 ] - 20 - 4, 4 ),
			wx.Point( self.frameCompactSize[ 0 ] - 20 - 4, 16 ),
			width=2,
			layer=0
		)
		self.compactCanvas.CreateLine(
			wx.Point( self.frameCompactSize[ 0 ] - 24, 4 ),
			wx.Point( self.frameCompactSize[ 0 ] - 36, 16 ),
			width=2,
			layer=0
		)

		# bind events
		self.largeCanvas.Bind( wx.EVT_LEFT_DOWN, self.OnMouseClick )
		self.largeCanvas.Bind( wx.EVT_LEFT_UP, self.OnMouseClick )
		self.largeCanvas.Bind( wx.EVT_MOTION, self.OnMouseMove )
		self.compactCanvas.Bind( wx.EVT_LEFT_DOWN, self.OnMouseClick )
		self.compactCanvas.Bind( wx.EVT_LEFT_UP, self.OnMouseClick )
		self.compactCanvas.Bind( wx.EVT_MOTION, self.OnMouseMove )
		self.Show()

	def Toggle( self ):
		if self.compact:
			self.compactCanvas.Show( False )
			self.compactCanvas.Enable( False )
			self.largeCanvas.Show()
			self.SetSize( self.frameLargeSize )
			self.compact = False
		else:
			self.largeCanvas.Show( False )
			self.compactCanvas.Enable()
			self.compactCanvas.Show()
			self.SetSize( self.frameCompactSize )
			self.compact = True

		# to move the window + react to buttons
	def OnMouseClick(self, evt: wx.MouseEvent):
		if self.close_btn.GetBoundingBox().IsInside( evt.GetPosition() ) and evt.LeftDown() and not self.compact:
			self.Destroy()
		elif self.resize_btn.GetBoundingBox().IsInside( evt.GetPosition() ) and evt.LeftDown() and not self.compact:
			self.Toggle()
		elif self.cclose_btn.GetBoundingBox().IsInside( evt.GetPosition() ) and evt.LeftDown():
			self.Destroy()
		elif self.cresize_btn.GetBoundingBox().IsInside( evt.GetPosition() ) and evt.LeftDown():
			self.Toggle()
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


run_screen = lambda: print('')


if __name__ == '__main__':
	app = wx.App()
	frame = SplashScreen()
	app.MainLoop()

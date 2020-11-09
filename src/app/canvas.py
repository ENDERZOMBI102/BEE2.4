from abc import ABCMeta, abstractmethod
from typing import Tuple, Union, List, Dict

import wx


class Canvas(wx.Panel):
	"""
		a small wrapper around the wx.ClientDC class, to draw on a window
		possible arguments:
		background: background color
		parent: a wx.Panel or wx.frame
		this class inherits all wx.Panel arguments
	"""
	_LayerCount: int
	_layers: Dict[int, List['CanvasItem'] ] = {}

	def __init__(self, parent: wx.Window):
		super(Canvas, self).__init__( parent=parent, size=parent.GetSize() )
		self.Bind(wx.EVT_PAINT, self._OnPaint, self)

	def AppendItem( self, layer: int, item: 'CanvasItem' ):
		if layer not in self._layers.keys():
			self._layers[ layer ] = []
		self._layers[ layer ].append( item )

	def CreateImage( self, image: wx.Image, pos: Union[wx.Point, wx.Point2D], layer: int = 0 ) -> 'CanvasImage':
		dc = wx.ClientDC( self )
		dc.DrawBitmap( image.ConvertToBitmap(), wx.Point( pos.Get() ) )
		return CanvasImage(self, image, pos, layer)

	def CreateText(
			self,
			text: str,
			pos: Union[wx.Point, wx.Point2D],
			color: Union[str, wx.Colour] = None,
			font: wx.Font = None,
			layer: int = 0
	):
		if color is None:
			color = wx.ColourDatabase().Find('BLACK')
		else:
			color = _CheckColor(color)
		if font is None:
			font = wx.Font( wx.FontInfo().Family(wx.FONTFAMILY_DEFAULT) )
		dc = wx.ClientDC( self )
		dc.SetTextForeground(color)
		dc.SetFont(font)
		dc.DrawText( text, wx.Point( pos.Get() ) )
		return CanvasText( self, text, font, color, pos, layer )

	def CreateRectangle(
			self,
			pos: Union[wx.Point, wx.Point2D],
			width: int,
			height: int,
			fillColor: Union[str, wx.Colour],
			lineColor: Union[str, wx.Colour] = None,
			alpha: int = 0,
			layer: int = 0
	):
		fillColor, lineColor = _CheckColor(fillColor), _CheckColor(lineColor)
		dc = wx.ClientDC( self )
		if lineColor is not None:
			dc.SetPen( wx.Pen(lineColor) )
		dc.SetBrush( wx.Brush(fillColor) )
		dc.DrawRectangle( wx.Rect( wx.Point( pos.Get() ), wx.Size(width, height) ) )
		return CanvasRectangle(self, pos, width, height, fillColor, lineColor, layer)

	def CreateGradient(
			self,
			pos: Union[wx.Point, wx.Point2D],
			width: int,
			height: int,
			color: wx.Colour,
			direction: int = wx.UP,
			color2: wx.Colour = None,
			layer: int = 0
	) -> 'CanvasGradient':
		color, color2 = _CheckColor( color ), _CheckColor( color2 )
		dc = wx.ClientDC(self)
		dc.GradientFillLinear( wx.Rect(pos.Get()[0], pos.Get()[1], width, height), color, color2, direction )
		return CanvasGradient(self, pos, width, height, color, direction, color2, layer)

	def CreateLine(
			self,
			pos0: Union[wx.Point, wx.Point2D],
			pos1: Union[wx.Point, wx.Point2D],
			color: wx.Colour = None,
			width: int = 1,
			layer: int = 0
	) -> 'CanvasLine':
		pos0, pos1 = wx.Point(pos0.Get()), wx.Point(pos1.Get())
		dc = wx.ClientDC( self )
		if color is None:
			dc.SetPen( wx.Pen( color ) )
		pen = dc.GetPen()
		pen.SetWidth( width )
		dc.SetPen( pen )
		dc.DrawLine( pos0, pos1 )
		return CanvasLine( self, pos0, pos1, color, width, layer)

	def CreatePoint( self, pos: Union[wx.Point, wx.Point2D], pen: wx.Pen = None, layer: int = 0):
		dc = wx.ClientDC( self )
		if pen is not None:
			dc.SetPen( pen )
		dc.DrawPoint( pos.Get() )
		return CanvasPoint(self, pos, pen, layer)

	def _OnPaint( self, evt: wx.PaintEvent ):
		for layer in range( len( self._layers ) ):
			for obj in self._layers[layer]:
				obj.Draw()


class CanvasItem(metaclass=ABCMeta):

	_parent: Canvas
	_bbox: 'BBox'
	_pos: Union[wx.Point, wx.Point2D]

	def __init__(self, parent: Canvas, pos: Union[wx.Point, wx.Point2D], layer: int = 0):
		self._parent = parent
		self._pos = pos
		parent.AppendItem(layer, self)

	@abstractmethod
	def GetBoundingBox( self ):
		return self._bbox

	@abstractmethod
	def Draw( self ):
		pass

	@abstractmethod
	def _UpdateBBox( self ):
		pass

	def GetParent( self ) -> wx.Window:
		return self._parent


class CanvasLine(CanvasItem):

	_bbox: 'BBox'
	_pos1: wx.Point
	_color: wx.Colour
	_width: int

	def __init__(self, parent: Canvas, pos0: wx.Point, pos1: wx.Point, color: wx.Colour = None, width: int = 1, layer: int = 0 ):
		super(CanvasLine, self).__init__(parent, pos0, layer)
		self._pos1 = pos1
		self._color = color
		self._width = width

	def Draw( self ):
		dc = wx.PaintDC( self._parent )
		if self._color is None:
			dc.SetPen( wx.Pen( self._color ) )
		pen = dc.GetPen()
		pen.SetWidth(self._width)
		dc.SetPen(pen)
		dc.DrawLine( self._pos, self._pos1 )

	def GetBoundingBox( self ):
		pass

	def _UpdateBBox( self ):
		pass


class CanvasRectangle(CanvasItem):

	_bbox: 'RectBBox'
	_rect: wx.Rect
	_fillColor: wx.Colour
	_lineColor: wx.Colour
	
	def __init__( self, parent: Canvas, pos: wx.Point2D, width: int, height: int, fillColor: wx.Colour, lineColor: wx.Colour, layer: int = 0 ):
		super(CanvasRectangle, self).__init__(parent, pos, layer)
		self._fillColor = fillColor
		self._lineColor = lineColor
		self._rect = wx.Rect(wx.Point( pos.Get() ), wx.Size(width, height) )
		self._UpdateBBox()

	def SetWidth( self, width: int ):
		self._rect.SetWidth(width)
		self._UpdateBBox()

	def SetHeight( self, height: int ):
		self._rect.SetWidth(height)
		self._UpdateBBox()

	def SetColor( self, color: Union[str, wx.Colour] ):
		self._color = _CheckColor(color)

	def GetBoundingBox( self ) -> 'RectBBox':
		return self._bbox

	def _UpdateBBox( self ):
		width, height = self._rect.GetSize()
		self._bbox = RectBBox.FromPoints(
			topLeft=self._pos,
			topRight=wx.Point2D( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] ),
			centerTop=wx.Point2D( self._pos.Get()[ 0 ] + (width / 2), self._pos.Get()[ 1 ] ),
			bottomLeft=wx.Point2D( self._pos.Get()[ 0 ], self._pos.Get()[ 1 ] + height ),
			bottomRight=wx.Point2D( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] + height ),
			centerBottom=wx.Point2D( self._pos.Get()[ 0 ] + (width / 2), self._pos.Get()[ 1 ] + height ),
			centerLeft=wx.Point2D( self._pos.Get()[ 0 ], self._pos.Get()[ 1 ] + (height / 2) ),
			centerRight=wx.Point2D( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] + (height / 2) )
		)

	def Draw( self ):
		dc = wx.PaintDC(self._parent)
		if self._lineColor is not None:
			dc.SetPen( wx.Pen( self._lineColor ) )
		dc.SetBrush( wx.Brush( self._fillColor ) )
		dc.DrawRectangle(self._rect)


class CanvasText(CanvasItem):

	_bbox: 'RectBBox'
	_font: wx.Font
	_color: wx.Colour
	_text: str

	def __init__(self, parent: Canvas, text: str, font: wx.Font, color: wx.Colour, pos: wx.Point2D, layer: int = 0 ):
		super(CanvasText, self).__init__(parent, pos, layer)
		self._text = text
		self._font = font
		self._color = color
		self._UpdateBBox()

	def _UpdateBBox( self ):
		dc = wx.ClientDC(self._parent)
		dc.SetFont(self._font)
		width, height = dc.GetTextExtent(self._text)
		x, y = self._pos.Get()
		print(x, y)
		self._bbox = RectBBox.FromPoints(
			topLeft=self._pos,
			topRight=wx.Point2D( x + width, y ),
			centerTop=wx.Point2D( x + (width / 2), y ),
			bottomLeft=wx.Point2D( x, y + height ),
			bottomRight=wx.Point2D( x + width, y + height ),
			centerBottom=wx.Point2D( x + (width / 2), y + height ),
			centerLeft=wx.Point2D( x, y + (height / 2) ),
			centerRight=wx.Point2D( x + width, y + (height / 2) )
		)
		print(
			[ i.Get() for i in self._bbox.GetVerticies() ]
		)

	def SetText( self, text: str ):
		self._text = text
		self._UpdateBBox()

	def GetText( self ):
		return self._text

	def GetBoundingBox( self ) -> 'RectBBox':
		return self._bbox

	def Draw( self ):
		dc = wx.PaintDC( self._parent )
		dc.SetTextForeground(self._color)
		dc.SetFont( self._font )
		dc.DrawText( self._text, wx.Point( self._pos.Get() ) )


class CanvasGradient( CanvasItem ):

	_bbox: 'RectBBox'
	_rect: wx.Rect
	_color: wx.Colour
	_color2: wx.Colour
	_direction: int

	def __init__(
			self,
			parent: Canvas,
			pos: Union[wx.Point, wx.Point2D],
			width: int,
			height: int,
			color: wx.Colour,
			direction: int = wx.UP,
			color2: wx.Colour = None,
			layer: int = 0
	):
		super( CanvasGradient, self ).__init__( parent, pos, layer )
		self._color = color
		self._direction = direction
		self._color2 = color2
		self._rect = wx.Rect( wx.Point( pos.Get() ), wx.Size( width, height ) )
		self._UpdateBBox()

	def SetWidth( self, width: int ):
		self._rect.SetWidth( width )
		self._UpdateBBox()

	def SetHeight( self, height: int ):
		self._rect.SetWidth( height )
		self._UpdateBBox()

	def SetColor( self, color: Union[ str, wx.Colour ] ):
		self._color = _CheckColor( color )

	def GetBoundingBox( self ) -> 'RectBBox':
		return self._bbox

	def _UpdateBBox( self ):
		width, height = self._rect.GetSize()
		self._bbox = RectBBox.FromPoints(
			topLeft=self._pos,
			topRight=wx.Point2D( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] ),
			centerTop=wx.Point2D( self._pos.Get()[ 0 ] + (width / 2), self._pos.Get()[ 1 ] ),
			bottomLeft=wx.Point2D( self._pos.Get()[ 0 ], self._pos.Get()[ 1 ] + height ),
			bottomRight=wx.Point2D( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] + height ),
			centerBottom=wx.Point2D( self._pos.Get()[ 0 ] + (width / 2), self._pos.Get()[ 1 ] + height ),
			centerLeft=wx.Point2D( self._pos.Get()[ 0 ], self._pos.Get()[ 1 ] + (height / 2) ),
			centerRight=wx.Point2D( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] + (height / 2) )
		)

	def Draw( self ):
		dc = wx.PaintDC( self._parent )
		dc.GradientFillLinear(self._rect, self._color, self._color2, self._direction)


class CanvasPoint(CanvasItem):

	_pen: wx.Pen

	def __init__( self, parent: Canvas, pos: Union[wx.Point, wx.Point2D], pen: wx.Pen = None, layer: int = 0 ):
		super().__init__( parent, pos, layer )
		self._pen = pen

	def Draw( self ):
		dc = wx.PaintDC( self._parent )
		if self._pen is not None:
			dc.SetPen( self._pen )
		dc.DrawPoint( self._pos.Get() )

	def GetBoundingBox( self ):
		pass

	def _UpdateBBox( self ):
		pass


class CanvasImage(CanvasItem):

	_image: wx.Image
	_bbox: 'RectBBox'

	def __init__(self, parent: Canvas, img: wx.Image, pos: Union[wx.Point, wx.Point2D], layer: int = 0):
		super(CanvasImage, self).__init__(parent, pos, layer)
		self._image = img
		self._UpdateBBox()

	def GetBoundingBox( self ) -> 'RectBBox':
		return self._bbox

	def _UpdateBBox( self ):
		width, height = self._image.GetSize().Get()
		self._bbox = RectBBox.FromPoints(
			topLeft=self._pos,
			topRight=wx.Point2D( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] ),
			centerTop=wx.Point2D( self._pos.Get()[ 0 ] + (width / 2), self._pos.Get()[ 1 ] ),
			bottomLeft=wx.Point2D( self._pos.Get()[ 0 ], self._pos.Get()[ 1 ] + height ),
			bottomRight=wx.Point2D( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] + height ),
			centerBottom=wx.Point2D( self._pos.Get()[ 0 ] + (width / 2), self._pos.Get()[ 1 ] + height ),
			centerLeft=wx.Point2D( self._pos.Get()[ 0 ], self._pos.Get()[ 1 ] + (height / 2) ),
			centerRight=wx.Point2D( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] + (height / 2) )
		)

	def SetImage( self, img: wx.Image ):
		self._image = img
		self._UpdateBBox()

	def GetImage( self ) -> wx.Image:
		return self._image

	def Draw( self ):
		dc = wx.PaintDC( self._parent )
		dc.DrawBitmap( self._image.ConvertToBitmap(), wx.Point( self._pos.Get() ) )


class BBox(metaclass=ABCMeta):

	@abstractmethod
	def IsInside( self, pos: Union[wx.Point, wx.Point2D] ) -> bool:
		pass


class RectBBox(BBox):

	_topRight: wx.Point2D
	_topLeft: wx.Point2D
	_bottomRight: wx.Point2D
	_bottomLeft: wx.Point2D
	_top: wx.Point2D
	_bottom: wx.Point2D
	_right: wx.Point2D
	_left: wx.Point2D

	def __init__(self, points: Tuple[wx.Point2D]):
		self._topRight = points[ 0 ]
		self._topLeft = points[ 1 ]
		self._bottomRight = points[ 2 ]
		self._bottomLeft = points[ 3 ]
		self._top = points[ 4 ]
		self._bottom = points[ 5 ]
		self._right = points[ 6 ]
		self._left = points[ 7 ]

	@staticmethod
	def FromPoints(
		topRight: wx.Point2D,
		topLeft: wx.Point2D,
		bottomRight: wx.Point2D,
		bottomLeft: wx.Point2D,
		centerTop: wx.Point2D,
		centerBottom: wx.Point2D,
		centerRight: wx.Point2D,
		centerLeft: wx.Point2D
	):
		return RectBBox(
			tuple(
				[topRight, topLeft, bottomRight, bottomLeft, centerTop, centerBottom, centerRight, centerLeft]
			)
		)

	def GetTopRight( self ):
		return self._topRight

	def GetTopLeft( self ):
		return self._topLeft

	def GetBottomRight( self ):
		return self._bottomRight

	def GetBottomLeft( self ):
		return self._bottomLeft

	def GetTop( self ):
		return self._top

	def GetBottom( self ):
		return self._bottom

	def GetRight( self ):
		return self._right

	def GetLeft( self ):
		return self._left

	def GetCenter( self ):
		return wx.Point2D(self._left.Get()[1], self._top.Get()[0])

	def GetVerticies( self ) -> Tuple[ wx.Point2D, wx.Point2D, wx.Point2D, wx.Point2D ]:
		return self._topLeft, self._topRight, self._bottomLeft, self._bottomRight

	def IsInside( self, pos: Union[wx.Point, wx.Point2D] ) -> bool:
		inside = True
		# too much left
		if pos.Get()[0] < self._left.Get()[0]:
			inside = False
		# too much right
		elif pos.Get()[0] > self._right.Get()[0]:
			inside = False
		# too much top
		elif pos.Get()[1] < self._top.Get()[1]:
			inside = False
		# too much bottom
		elif pos.Get()[1] > self._bottom.Get()[1]:
			inside = False
		return inside


def _CheckColor(color: Union[str, wx.Colour]) -> Union[None, wx.Colour]:
	if color is None:
		return None
	elif isinstance( color, wx.Colour ):
		return color
	else:
		kolor: wx.Colour = wx.ColourDatabase().Find( color )
		if kolor.IsOk():
			return kolor
		else:
			wx.ColourDatabase().AddColour( color, wx.Colour( color ) )
			return wx.ColourDatabase().Find( color )

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
	_layers: Dict[int, List['CanvasItem'] ]

	def __init__(self, **kwargs):
		if 'parent' not in kwargs:
			raise TypeError('Missing required keyword argument "parent"')
		super(Canvas, self).__init__( size=kwargs.get('parent').GetSize(), **kwargs )
		self._LayerCount = 0
		self._layers = {}
		self.Bind(wx.EVT_PAINT, self._OnPaint, self)

	def AppendItem( self, layer: int, item: 'CanvasItem' ):
		"""
		Adds an item to the drawing list
		:param layer: the layer this item will be drawn to
		:param item: the item to append
		"""
		if layer not in self._layers.keys():
			self._layers[ layer ] = []
		self._layers[ layer ].append( item )
		self._LayerCount = len(self._layers)

	def CreateImage( self, image: wx.Image, pos: Union[wx.Point, wx.Point2D], layer: int = 0 ) -> 'CanvasImage':
		"""
		Creates an image on the canvas

		:ret-type: layer: int
		"""
		return CanvasImage(self, image, wx.Point( pos.Get() ), layer)

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
		return CanvasText( self, text, font, color, wx.Point( pos.Get() ), layer )

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
		return CanvasRectangle(self, wx.Point( pos.Get() ), width, height, fillColor, lineColor, layer)

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
		return CanvasGradient(
			self,
			wx.Point( pos.Get() ),
			width,
			height,
			color,
			direction,
			color2,
			layer
		)

	def CreateLine(
			self,
			pos0: Union[wx.Point, wx.Point2D],
			pos1: Union[wx.Point, wx.Point2D],
			color: wx.Colour = None,
			width: int = 1,
			layer: int = 0
	) -> 'CanvasLine':
		pos0, pos1 = wx.Point( pos0.Get() ), wx.Point( pos1.Get() )
		return CanvasLine( self, pos0, pos1, color, width, layer)

	def CreatePoint( self, pos: Union[wx.Point, wx.Point2D], pen: wx.Pen = None, layer: int = 0):
		return CanvasPoint(self, wx.Point( pos.Get() ), pen, layer)

	def _OnPaint( self, evt: wx.PaintEvent ):
		dc = wx.PaintDC( self )
		for layer in range( len( self._layers ) ):
			# range gives 0 too, we might not have a layer 0
			if layer in self._layers.keys():
				for obj in self._layers[layer]:
					obj.Draw(dc)
		dc.Destroy()


class CanvasItem(metaclass=ABCMeta):

	_parent: Canvas
	_bbox: 'BBox'
	_pos: wx.Point

	def __init__(self, parent: Canvas, pos: wx.Point, layer: int = 0):
		self._parent = parent
		self._pos = pos
		parent.AppendItem(layer, self)

	@abstractmethod
	def GetBoundingBox( self ):
		return self._bbox

	@abstractmethod
	def Draw( self, dc: wx.PaintDC ):
		pass

	@abstractmethod
	def _UpdateBBox( self ):
		pass

	def GetParent( self ) -> Canvas:
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

	def Draw( self, dc: wx.PaintDC ):
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
	
	def __init__( self, parent: Canvas, pos: wx.Point, width: int, height: int, fillColor: wx.Colour, lineColor: wx.Colour, layer: int = 0 ):
		super(CanvasRectangle, self).__init__(parent, pos, layer)
		self._fillColor = fillColor
		self._lineColor = lineColor
		self._rect = wx.Rect(pos, wx.Size(width, height) )
		self._UpdateBBox()

	def SetWidth( self, width: int ):
		self._rect.SetWidth(width)
		self._UpdateBBox()

	def SetHeight( self, height: int ):
		self._rect.SetWidth(height)
		self._UpdateBBox()

	def SetColor( self, color: Union[str, wx.Colour] ):
		self._fillColor = _CheckColor(color)

	def GetBoundingBox( self ) -> 'RectBBox':
		return self._bbox

	def _UpdateBBox( self ):
		width, height = self._rect.GetSize()
		self._bbox = RectBBox.FromPoints(
			topLeft=self._pos,
			topRight=wx.Point( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] ),
			centerTop=wx.Point( self._pos.Get()[ 0 ] + (width / 2), self._pos.Get()[ 1 ] ),
			bottomLeft=wx.Point( self._pos.Get()[ 0 ], self._pos.Get()[ 1 ] + height ),
			bottomRight=wx.Point( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] + height ),
			centerBottom=wx.Point( self._pos.Get()[ 0 ] + (width / 2), self._pos.Get()[ 1 ] + height ),
			centerLeft=wx.Point( self._pos.Get()[ 0 ], self._pos.Get()[ 1 ] + (height / 2) ),
			centerRight=wx.Point( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] + (height / 2) )
		)
		self._bbox.SetOwner( self )

	def Draw( self, dc: wx.PaintDC ):
		if self._lineColor is not None:
			dc.SetPen( wx.Pen( self._lineColor ) )
		dc.SetBrush( wx.Brush( self._fillColor ) )
		dc.DrawRectangle(self._rect)


class CanvasText(CanvasItem):

	_bbox: 'RectBBox'
	_font: wx.Font
	_color: wx.Colour
	_text: str

	def __init__(self, parent: Canvas, text: str, font: wx.Font, color: wx.Colour, pos: wx.Point, layer: int = 0 ):
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
		self._bbox = RectBBox.FromPoints(
			topLeft=self._pos,
			topRight=wx.Point( x + width, y ),
			centerTop=wx.Point( x + (width / 2), y ),
			bottomLeft=wx.Point( x, y + height ),
			bottomRight=wx.Point( x + width, y + height ),
			centerBottom=wx.Point( x + (width / 2), y + height ),
			centerLeft=wx.Point( x, y + (height / 2) ),
			centerRight=wx.Point( x + width, y + (height / 2) )
		)
		self._bbox.SetOwner( self )

	def SetText( self, text: str ):
		self._text = text
		self._UpdateBBox()

	def GetText( self ):
		return self._text

	def GetBoundingBox( self ) -> 'RectBBox':
		return self._bbox

	def Draw( self, dc: wx.PaintDC ):
		dc.SetTextForeground(self._color)
		dc.SetFont( self._font )
		dc.DrawText( self._text, self._pos )


class CanvasGradient( CanvasItem ):

	_bbox: 'RectBBox'
	_rect: wx.Rect
	_color: wx.Colour
	_color2: wx.Colour
	_direction: int

	def __init__(
			self,
			parent: Canvas,
			pos: wx.Point,
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
			topRight=wx.Point( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] ),
			centerTop=wx.Point( self._pos.Get()[ 0 ] + (width / 2), self._pos.Get()[ 1 ] ),
			bottomLeft=wx.Point( self._pos.Get()[ 0 ], self._pos.Get()[ 1 ] + height ),
			bottomRight=wx.Point( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] + height ),
			centerBottom=wx.Point( self._pos.Get()[ 0 ] + (width / 2), self._pos.Get()[ 1 ] + height ),
			centerLeft=wx.Point( self._pos.Get()[ 0 ], self._pos.Get()[ 1 ] + (height / 2) ),
			centerRight=wx.Point( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] + (height / 2) )
		)
		self._bbox.SetOwner( self )

	def Draw( self, dc: wx.PaintDC ):
		dc.GradientFillLinear(self._rect, self._color, self._color2, self._direction)


class CanvasPoint(CanvasItem):

	_pen: wx.Pen

	def __init__( self, parent: Canvas, pos: wx.Point, pen: wx.Pen = None, layer: int = 0 ):
		super().__init__( parent, pos, layer )
		self._pen = pen

	def Draw( self, dc: wx.PaintDC ):
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

	def __init__(self, parent: Canvas, img: wx.Image, pos: wx.Point, layer: int = 0):
		super(CanvasImage, self).__init__(parent, pos, layer)
		self._image = img
		self._UpdateBBox()

	def GetBoundingBox( self ) -> 'RectBBox':
		return self._bbox

	def _UpdateBBox( self ):
		width, height = self._image.GetSize().Get()
		self._bbox = RectBBox.FromPoints(
			topLeft=self._pos,
			topRight=wx.Point( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] ),
			centerTop=wx.Point( self._pos.Get()[ 0 ] + (width / 2), self._pos.Get()[ 1 ] ),
			bottomLeft=wx.Point( self._pos.Get()[ 0 ], self._pos.Get()[ 1 ] + height ),
			bottomRight=wx.Point( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] + height ),
			centerBottom=wx.Point( self._pos.Get()[ 0 ] + (width / 2), self._pos.Get()[ 1 ] + height ),
			centerLeft=wx.Point( self._pos.Get()[ 0 ], self._pos.Get()[ 1 ] + (height / 2) ),
			centerRight=wx.Point( self._pos.Get()[ 0 ] + width, self._pos.Get()[ 1 ] + (height / 2) )
		)
		self._bbox.SetOwner(self)

	def SetImage( self, img: wx.Image ):
		self._image = img
		self._UpdateBBox()

	def GetImage( self ) -> wx.Image:
		return self._image

	def Draw( self, dc: wx.PaintDC ):
		dc.DrawBitmap( self._image.ConvertToBitmap(), wx.Point( self._pos.Get() ) )


class BBox(metaclass=ABCMeta):

	@abstractmethod
	def IsInside( self, pos: Union[wx.Point, wx.Point2D] ) -> bool:
		pass

	@abstractmethod
	def SetOwner( self, owner: CanvasItem ) -> None:
		pass


class RectBBox(BBox):

	_topRight: wx.Point
	_topLeft: wx.Point
	_bottomRight: wx.Point
	_bottomLeft: wx.Point
	_top: wx.Point
	_bottom: wx.Point
	_right: wx.Point
	_left: wx.Point
	_owner: CanvasItem

	def __init__(self, owner: CanvasItem, points: Tuple[wx.Point]):
		self._topRight = points[ 0 ]
		self._topLeft = points[ 1 ]
		self._bottomRight = points[ 2 ]
		self._bottomLeft = points[ 3 ]
		self._top = points[ 4 ]
		self._bottom = points[ 5 ]
		self._right = points[ 6 ]
		self._left = points[ 7 ]
		self._owner = owner

	@staticmethod
	def FromPoints(
		topRight: wx.Point,
		topLeft: wx.Point,
		bottomRight: wx.Point,
		bottomLeft: wx.Point,
		centerTop: wx.Point,
		centerBottom: wx.Point,
		centerRight: wx.Point,
		centerLeft: wx.Point
	):
		return RectBBox(
			None,
			tuple(
				[topRight, topLeft, bottomRight, bottomLeft, centerTop, centerBottom, centerRight, centerLeft]
			)
		)

	def SetOwner( self, owner: CanvasItem ) -> None:
		self._owner = owner

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
		return wx.Point(self._left.Get()[1], self._top.Get()[0])

	def GetVerticies( self ) -> Tuple[ wx.Point, wx.Point, wx.Point, wx.Point ]:
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

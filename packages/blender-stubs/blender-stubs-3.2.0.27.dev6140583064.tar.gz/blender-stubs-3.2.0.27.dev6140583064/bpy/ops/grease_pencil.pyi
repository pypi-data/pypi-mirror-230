"""


Grease Pencil Operators
***********************

:func:`brush_stroke`

:func:`dissolve`

:func:`draw_mode_toggle`

:func:`insert_blank_frame`

:func:`layer_add`

:func:`layer_group_add`

:func:`layer_remove`

:func:`layer_reorder`

:func:`select_all`

:func:`select_alternate`

:func:`select_ends`

:func:`select_less`

:func:`select_linked`

:func:`select_more`

:func:`select_random`

:func:`set_selection_mode`

:func:`stroke_simplify`

:func:`stroke_smooth`

"""

import typing

def brush_stroke(stroke: typing.Union[typing.Sequence[OperatorStrokeElement], typing.Mapping[str, OperatorStrokeElement], bpy.types.bpy_prop_collection] = None, mode: str = 'NORMAL') -> None:

  """

  Draw a new stroke in the active Grease Pencil object

  """

  ...

def dissolve(type: str = 'POINTS') -> None:

  """

  Delete selected points without splitting strokes

  """

  ...

def draw_mode_toggle() -> None:

  """

  Enter/Exit draw mode for grease pencil

  """

  ...

def insert_blank_frame(all_layers: bool = False, duration: int = 1) -> None:

  """

  Insert a blank frame on the current scene frame

  """

  ...

def layer_add(new_layer_name: str = 'GP_Layer') -> None:

  """

  Add a new Grease Pencil layer in the active object

  """

  ...

def layer_group_add(new_layer_group_name: str = 'GP_Group') -> None:

  """

  Add a new Grease Pencil layer group in the active object

  """

  ...

def layer_remove() -> None:

  """

  Remove the active Grease Pencil layer

  """

  ...

def layer_reorder(target_layer_name: str = 'GP_Layer', location: str = 'ABOVE') -> None:

  """

  Reorder the active Grease Pencil layer

  """

  ...

def select_all(action: str = 'TOGGLE') -> None:

  """

  (De)select all visible strokes

  """

  ...

def select_alternate(deselect_ends: bool = False) -> None:

  """

  Select alternated points in strokes with already selected points

  """

  ...

def select_ends(amount_start: int = 0, amount_end: int = 1) -> None:

  """

  Select end points of strokes

  """

  ...

def select_less() -> None:

  """

  Shrink the selection by one point

  """

  ...

def select_linked() -> None:

  """

  Select all points in curves with any point selection

  """

  ...

def select_more() -> None:

  """

  Grow the selection by one point

  """

  ...

def select_random(ratio: float = 0.5, seed: int = 0, action: str = 'SELECT') -> None:

  """

  Selects random points from the current strokes selection

  """

  ...

def set_selection_mode(mode: str = 'POINT') -> None:

  """

  Change the selection mode for Grease Pencil strokes

  """

  ...

def stroke_simplify(factor: float = 0.001) -> None:

  """

  Simplify selected strokes

  """

  ...

def stroke_smooth(iterations: int = 10, factor: float = 1.0, smooth_ends: bool = False, keep_shape: bool = False, smooth_position: bool = True, smooth_radius: bool = True, smooth_opacity: bool = False) -> None:

  """

  Smooth selected strokes

  """

  ...

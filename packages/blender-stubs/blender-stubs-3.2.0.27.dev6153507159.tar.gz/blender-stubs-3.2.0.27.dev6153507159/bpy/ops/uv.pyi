"""


Uv Operators
************

:func:`align`

:func:`align_rotation`

:func:`average_islands_scale`

:func:`copy`

:func:`cube_project`

:func:`cursor_set`

:func:`cylinder_project`

:func:`follow_active_quads`

:func:`hide`

:func:`lightmap_pack`

:func:`mark_seam`

:func:`minimize_stretch`

:func:`pack_islands`

:func:`paste`

:func:`pin`

:func:`project_from_view`

:func:`randomize_uv_transform`

:func:`remove_doubles`

:func:`reset`

:func:`reveal`

:func:`rip`

:func:`rip_move`

:func:`seams_from_islands`

:func:`select`

:func:`select_all`

:func:`select_box`

:func:`select_circle`

:func:`select_edge_ring`

:func:`select_lasso`

:func:`select_less`

:func:`select_linked`

:func:`select_linked_pick`

:func:`select_loop`

:func:`select_mode`

:func:`select_more`

:func:`select_overlap`

:func:`select_pinned`

:func:`select_similar`

:func:`select_split`

:func:`shortest_path_pick`

:func:`shortest_path_select`

:func:`smart_project`

:func:`snap_cursor`

:func:`snap_selected`

:func:`sphere_project`

:func:`stitch`

:func:`unwrap`

:func:`weld`

"""

import typing

import mathutils

def align(axis: str = 'ALIGN_AUTO') -> None:

  """

  Align selected UV vertices to an axis

  """

  ...

def align_rotation(method: str = 'AUTO', axis: str = 'X', correct_aspect: bool = False) -> None:

  """

  Align the UV island's rotation

  """

  ...

def average_islands_scale(scale_uv: bool = False, shear: bool = False) -> None:

  """

  Average the size of separate UV islands, based on their area in 3D space

  """

  ...

def copy() -> None:

  """

  Copy selected UV vertices

  """

  ...

def cube_project(cube_size: float = 1.0, correct_aspect: bool = True, clip_to_bounds: bool = False, scale_to_bounds: bool = False) -> None:

  """

  Project the UV vertices of the mesh over the six faces of a cube

  """

  ...

def cursor_set(location: mathutils.Vector = (0.0, 0.0)) -> None:

  """

  Set 2D cursor location

  """

  ...

def cylinder_project(direction: str = 'VIEW_ON_EQUATOR', align: str = 'POLAR_ZX', pole: str = 'PINCH', seam: bool = False, radius: float = 1.0, correct_aspect: bool = True, clip_to_bounds: bool = False, scale_to_bounds: bool = False) -> None:

  """

  Project the UV vertices of the mesh over the curved wall of a cylinder

  """

  ...

def follow_active_quads(mode: str = 'LENGTH_AVERAGE') -> None:

  """

  Follow UVs from active quads along continuous face loops

  """

  ...

def hide(unselected: bool = False) -> None:

  """

  Hide (un)selected UV vertices

  """

  ...

def lightmap_pack(PREF_CONTEXT: str = 'SEL_FACES', PREF_PACK_IN_ONE: bool = True, PREF_NEW_UVLAYER: bool = False, PREF_BOX_DIV: int = 12, PREF_MARGIN_DIV: float = 0.1) -> None:

  """

  Pack each face's UVs into the UV bounds

  """

  ...

def mark_seam(clear: bool = False) -> None:

  """

  Mark selected UV edges as seams

  """

  ...

def minimize_stretch(fill_holes: bool = True, blend: float = 0.0, iterations: int = 0) -> None:

  """

  Reduce UV stretching by relaxing angles

  """

  ...

def pack_islands(udim_source: str = 'CLOSEST_UDIM', rotate: bool = True, rotate_method: str = 'ANY', scale: bool = True, merge_overlap: bool = False, margin_method: str = 'SCALED', margin: float = 0.001, pin: bool = False, pin_method: str = 'LOCKED', shape_method: str = 'CONCAVE') -> None:

  """

  Transform all islands so that they fill up the UV/UDIM space as much as possible

  """

  ...

def paste() -> None:

  """

  Paste selected UV vertices

  """

  ...

def pin(clear: bool = False, invert: bool = False) -> None:

  """

  Set/clear selected UV vertices as anchored between multiple unwrap operations

  """

  ...

def project_from_view(orthographic: bool = False, camera_bounds: bool = True, correct_aspect: bool = True, clip_to_bounds: bool = False, scale_to_bounds: bool = False) -> None:

  """

  Project the UV vertices of the mesh as seen in current 3D view

  """

  ...

def randomize_uv_transform(random_seed: int = 0, use_loc: bool = True, loc: mathutils.Vector = (0.0, 0.0), use_rot: bool = True, rot: float = 0.0, use_scale: bool = True, scale_even: bool = False, scale: typing.Tuple[float, float] = (1.0, 1.0)) -> None:

  """

  Randomize the UV island's location, rotation, and scale

  """

  ...

def remove_doubles(threshold: float = 0.02, use_unselected: bool = False) -> None:

  """

  Selected UV vertices that are within a radius of each other are welded together

  """

  ...

def reset() -> None:

  """

  Reset UV projection

  """

  ...

def reveal(select: bool = True) -> None:

  """

  Reveal all hidden UV vertices

  """

  ...

def rip(mirror: bool = False, release_confirm: bool = False, use_accurate: bool = False, location: mathutils.Vector = (0.0, 0.0)) -> None:

  """

  Rip selected vertices or a selected region

  """

  ...

def rip_move(UV_OT_rip: UV_OT_rip = None, TRANSFORM_OT_translate: TRANSFORM_OT_translate = None) -> None:

  """

  Unstitch UVs and move the result

  """

  ...

def seams_from_islands(mark_seams: bool = True, mark_sharp: bool = False) -> None:

  """

  Set mesh seams according to island setup in the UV editor

  """

  ...

def select(extend: bool = False, deselect: bool = False, toggle: bool = False, deselect_all: bool = False, select_passthrough: bool = False, location: mathutils.Vector = (0.0, 0.0)) -> None:

  """

  Select UV vertices

  """

  ...

def select_all(action: str = 'TOGGLE') -> None:

  """

  Change selection of all UV vertices

  """

  ...

def select_box(pinned: bool = False, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True, mode: str = 'SET') -> None:

  """

  Select UV vertices using box selection

  """

  ...

def select_circle(x: int = 0, y: int = 0, radius: int = 25, wait_for_input: bool = True, mode: str = 'SET') -> None:

  """

  Select UV vertices using circle selection

  """

  ...

def select_edge_ring(extend: bool = False, location: mathutils.Vector = (0.0, 0.0)) -> None:

  """

  Select an edge ring of connected UV vertices

  """

  ...

def select_lasso(path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, mode: str = 'SET') -> None:

  """

  Select UVs using lasso selection

  """

  ...

def select_less() -> None:

  """

  Deselect UV vertices at the boundary of each selection region

  """

  ...

def select_linked() -> None:

  """

  Select all UV vertices linked to the active UV map

  """

  ...

def select_linked_pick(extend: bool = False, deselect: bool = False, location: mathutils.Vector = (0.0, 0.0)) -> None:

  """

  Select all UV vertices linked under the mouse

  """

  ...

def select_loop(extend: bool = False, location: mathutils.Vector = (0.0, 0.0)) -> None:

  """

  Select a loop of connected UV vertices

  """

  ...

def select_mode(type: str = 'VERTEX') -> None:

  """

  Change UV selection mode

  """

  ...

def select_more() -> None:

  """

  Select more UV vertices connected to initial selection

  """

  ...

def select_overlap(extend: bool = False) -> None:

  """

  Select all UV faces which overlap each other

  """

  ...

def select_pinned() -> None:

  """

  Select all pinned UV vertices

  """

  ...

def select_similar(type: str = 'PIN', compare: str = 'EQUAL', threshold: float = 0.0) -> None:

  """

  Select similar UVs by property types

  """

  ...

def select_split() -> None:

  """

  Select only entirely selected faces

  """

  ...

def shortest_path_pick(use_face_step: bool = False, use_topology_distance: bool = False, use_fill: bool = False, skip: int = 0, nth: int = 1, offset: int = 0, object_index: int = -1, index: int = -1) -> None:

  """

  Select shortest path between two selections

  """

  ...

def shortest_path_select(use_face_step: bool = False, use_topology_distance: bool = False, use_fill: bool = False, skip: int = 0, nth: int = 1, offset: int = 0) -> None:

  """

  Selected shortest path between two vertices/edges/faces

  """

  ...

def smart_project(angle_limit: float = 1.15192, margin_method: str = 'SCALED', island_margin: float = 0.0, area_weight: float = 0.0, correct_aspect: bool = True, scale_to_bounds: bool = False) -> None:

  """

  Projection unwraps the selected faces of mesh objects

  """

  ...

def snap_cursor(target: str = 'PIXELS') -> None:

  """

  Snap cursor to target type

  """

  ...

def snap_selected(target: str = 'PIXELS') -> None:

  """

  Snap selected UV vertices to target type

  """

  ...

def sphere_project(direction: str = 'VIEW_ON_EQUATOR', align: str = 'POLAR_ZX', pole: str = 'PINCH', seam: bool = False, correct_aspect: bool = True, clip_to_bounds: bool = False, scale_to_bounds: bool = False) -> None:

  """

  Project the UV vertices of the mesh over the curved surface of a sphere

  """

  ...

def stitch(use_limit: bool = False, snap_islands: bool = True, limit: float = 0.01, static_island: int = 0, active_object_index: int = 0, midpoint_snap: bool = False, clear_seams: bool = True, mode: str = 'VERTEX', stored_mode: str = 'VERTEX', selection: typing.Union[typing.Sequence[SelectedUvElement], typing.Mapping[str, SelectedUvElement], bpy.types.bpy_prop_collection] = None, objects_selection_count: typing.Tuple[int, ...] = (0, 0, 0, 0, 0, 0)) -> None:

  """

  Stitch selected UV vertices by proximity

  """

  ...

def unwrap(method: str = 'ANGLE_BASED', fill_holes: bool = True, correct_aspect: bool = True, use_subsurf_data: bool = False, margin_method: str = 'SCALED', margin: float = 0.001) -> None:

  """

  Unwrap the mesh of the object being edited

  """

  ...

def weld() -> None:

  """

  Weld selected UV vertices together

  """

  ...

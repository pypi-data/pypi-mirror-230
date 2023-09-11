"""


Node Operators
**************

:func:`add_collection`

:func:`add_file`

:func:`add_group`

:func:`add_group_asset`

:func:`add_mask`

:func:`add_material`

:func:`add_node`

:func:`add_object`

:func:`add_repeat_zone`

:func:`add_reroute`

:func:`add_search`

:func:`add_simulation_zone`

:func:`attach`

:func:`backimage_fit`

:func:`backimage_move`

:func:`backimage_sample`

:func:`backimage_zoom`

:func:`clear_viewer_border`

:func:`clipboard_copy`

:func:`clipboard_paste`

:func:`collapse_hide_unused_toggle`

:func:`cryptomatte_layer_add`

:func:`cryptomatte_layer_remove`

:func:`deactivate_viewer`

:func:`delete`

:func:`delete_reconnect`

:func:`detach`

:func:`detach_translate_attach`

:func:`duplicate`

:func:`duplicate_move`

:func:`duplicate_move_keep_inputs`

:func:`duplicate_move_linked`

:func:`find_node`

:func:`group_edit`

:func:`group_insert`

:func:`group_make`

:func:`group_separate`

:func:`group_ungroup`

:func:`hide_socket_toggle`

:func:`hide_toggle`

:func:`insert_offset`

:func:`interface_item_duplicate`

:func:`interface_item_new`

:func:`interface_item_remove`

:func:`join`

:func:`link`

:func:`link_make`

:func:`link_viewer`

:func:`links_cut`

:func:`links_detach`

:func:`links_mute`

:func:`move_detach_links`

:func:`move_detach_links_release`

:func:`mute_toggle`

:func:`new_geometry_node_group_assign`

:func:`new_geometry_node_group_tool`

:func:`new_geometry_nodes_modifier`

:func:`new_node_tree`

:func:`node_color_preset_add`

:func:`node_copy_color`

:func:`options_toggle`

:func:`output_file_add_socket`

:func:`output_file_move_active_socket`

:func:`output_file_remove_active_socket`

:func:`parent_set`

:func:`preview_toggle`

:func:`read_viewlayers`

:func:`render_changed`

:func:`repeat_zone_item_add`

:func:`repeat_zone_item_move`

:func:`repeat_zone_item_remove`

:func:`resize`

:func:`select`

:func:`select_all`

:func:`select_box`

:func:`select_circle`

:func:`select_grouped`

:func:`select_lasso`

:func:`select_link_viewer`

:func:`select_linked_from`

:func:`select_linked_to`

:func:`select_same_type_step`

:func:`shader_script_update`

:func:`simulation_zone_item_add`

:func:`simulation_zone_item_move`

:func:`simulation_zone_item_remove`

:func:`switch_view_update`

:func:`translate_attach`

:func:`translate_attach_remove_on_cancel`

:func:`tree_path_parent`

:func:`view_all`

:func:`view_selected`

:func:`viewer_border`

"""

import typing

def add_collection(name: str = '', session_uuid: int = 0) -> None:

  """

  Add a collection info node to the current node editor

  """

  ...

def add_file(filepath: str = '', hide_props_region: bool = True, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = True, filter_movie: bool = True, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_collada: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 9, relative_path: bool = True, show_multiview: bool = False, use_multiview: bool = False, display_type: str = 'DEFAULT', sort_method: str = '', name: str = '', session_uuid: int = 0) -> None:

  """

  Add a file node to the current node editor

  """

  ...

def add_group(name: str = '', session_uuid: int = 0, show_datablock_in_node: bool = True) -> None:

  """

  Add an existing node group to the current node editor

  """

  ...

def add_group_asset() -> None:

  """

  Add a node group asset to the active node tree

  """

  ...

def add_mask(name: str = '', session_uuid: int = 0) -> None:

  """

  Add a mask node to the current node editor

  """

  ...

def add_material(name: str = '', session_uuid: int = 0) -> None:

  """

  Add a material node to the current node editor

  """

  ...

def add_node(use_transform: bool = False, settings: typing.Union[typing.Sequence[NodeSetting], typing.Mapping[str, NodeSetting], bpy.types.bpy_prop_collection] = None, type: str = '') -> None:

  """

  Add a node to the active tree

  """

  ...

def add_object(name: str = '', session_uuid: int = 0) -> None:

  """

  Add an object info node to the current node editor

  """

  ...

def add_repeat_zone(use_transform: bool = False, settings: typing.Union[typing.Sequence[NodeSetting], typing.Mapping[str, NodeSetting], bpy.types.bpy_prop_collection] = None, offset: typing.Tuple[float, float] = (150.0, 0.0)) -> None:

  """

  Add a repeat zone that allows executing nodes a dynamic number of times

  """

  ...

def add_reroute(path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, cursor: int = 8) -> None:

  """

  Add a reroute node

  """

  ...

def add_search(use_transform: bool = True) -> None:

  """

  Search for nodes and add one to the active tree

  """

  ...

def add_simulation_zone(use_transform: bool = False, settings: typing.Union[typing.Sequence[NodeSetting], typing.Mapping[str, NodeSetting], bpy.types.bpy_prop_collection] = None, offset: typing.Tuple[float, float] = (150.0, 0.0)) -> None:

  """

  Add simulation zone input and output nodes to the active tree

  """

  ...

def attach() -> None:

  """

  Attach active node to a frame

  """

  ...

def backimage_fit() -> None:

  """

  Fit the background image to the view

  """

  ...

def backimage_move() -> None:

  """

  Move node backdrop

  """

  ...

def backimage_sample() -> None:

  """

  Use mouse to sample background image

  """

  ...

def backimage_zoom(factor: float = 1.2) -> None:

  """

  Zoom in/out the background image

  """

  ...

def clear_viewer_border() -> None:

  """

  Clear the boundaries for viewer operations

  """

  ...

def clipboard_copy() -> None:

  """

  Copy the selected nodes to the internal clipboard

  """

  ...

def clipboard_paste(offset: typing.Tuple[float, float] = (0.0, 0.0)) -> None:

  """

  Paste nodes from the internal clipboard to the active node tree

  """

  ...

def collapse_hide_unused_toggle() -> None:

  """

  Toggle collapsed nodes and hide unused sockets

  """

  ...

def cryptomatte_layer_add() -> None:

  """

  Add a new input layer to a Cryptomatte node

  """

  ...

def cryptomatte_layer_remove() -> None:

  """

  Remove layer from a Cryptomatte node

  """

  ...

def deactivate_viewer() -> None:

  """

  Deactivate selected viewer node in geometry nodes

  """

  ...

def delete() -> None:

  """

  Remove selected nodes

  """

  ...

def delete_reconnect() -> None:

  """

  Remove nodes and reconnect nodes as if deletion was muted

  """

  ...

def detach() -> None:

  """

  Detach selected nodes from parents

  """

  ...

def detach_translate_attach(NODE_OT_detach: NODE_OT_detach = None, TRANSFORM_OT_translate: TRANSFORM_OT_translate = None, NODE_OT_attach: NODE_OT_attach = None) -> None:

  """

  Detach nodes, move and attach to frame

  """

  ...

def duplicate(keep_inputs: bool = False, linked: bool = True) -> None:

  """

  Duplicate selected nodes

  """

  ...

def duplicate_move(NODE_OT_duplicate: NODE_OT_duplicate = None, NODE_OT_translate_attach: NODE_OT_translate_attach = None) -> None:

  """

  Duplicate selected nodes and move them

  """

  ...

def duplicate_move_keep_inputs(NODE_OT_duplicate: NODE_OT_duplicate = None, NODE_OT_translate_attach: NODE_OT_translate_attach = None) -> None:

  """

  Duplicate selected nodes keeping input links and move them

  """

  ...

def duplicate_move_linked(NODE_OT_duplicate: NODE_OT_duplicate = None, NODE_OT_translate_attach: NODE_OT_translate_attach = None) -> None:

  """

  Duplicate selected nodes, but not their node trees, and move them

  """

  ...

def find_node() -> None:

  """

  Search for a node by name and focus and select it

  """

  ...

def group_edit(exit: bool = False) -> None:

  """

  Edit node group

  """

  ...

def group_insert() -> None:

  """

  Insert selected nodes into a node group

  """

  ...

def group_make() -> None:

  """

  Make group from selected nodes

  """

  ...

def group_separate(type: str = 'COPY') -> None:

  """

  Separate selected nodes from the node group

  """

  ...

def group_ungroup() -> None:

  """

  Ungroup selected nodes

  """

  ...

def hide_socket_toggle() -> None:

  """

  Toggle unused node socket display

  """

  ...

def hide_toggle() -> None:

  """

  Toggle hiding of selected nodes

  """

  ...

def insert_offset() -> None:

  """

  Automatically offset nodes on insertion

  """

  ...

def interface_item_duplicate() -> None:

  """

  Add a copy of the active item to the interface

  """

  ...

def interface_item_new(item_type: str = 'INPUT') -> None:

  """

  Add a new item to the interface

  """

  ...

def interface_item_remove() -> None:

  """

  Remove active item from the interface

  """

  ...

def join() -> None:

  """

  Attach selected nodes to a new common frame

  """

  ...

def link(detach: bool = False, drag_start: typing.Tuple[float, float] = (0.0, 0.0), inside_padding: float = 2.0, outside_padding: float = 0.0, speed_ramp: float = 1.0, max_speed: float = 26.0, delay: float = 0.5, zoom_influence: float = 0.5) -> None:

  """

  Use the mouse to create a link between two nodes

  """

  ...

def link_make(replace: bool = False) -> None:

  """

  Makes a link between selected output in input sockets

  """

  ...

def link_viewer() -> None:

  """

  Link to viewer node

  """

  ...

def links_cut(path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, cursor: int = 12) -> None:

  """

  Use the mouse to cut (remove) some links

  """

  ...

def links_detach() -> None:

  """

  Remove all links to selected nodes, and try to connect neighbor nodes together

  """

  ...

def links_mute(path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, cursor: int = 35) -> None:

  """

  Use the mouse to mute links

  """

  ...

def move_detach_links(NODE_OT_links_detach: NODE_OT_links_detach = None, TRANSFORM_OT_translate: TRANSFORM_OT_translate = None) -> None:

  """

  Move a node to detach links

  """

  ...

def move_detach_links_release(NODE_OT_links_detach: NODE_OT_links_detach = None, NODE_OT_translate_attach: NODE_OT_translate_attach = None) -> None:

  """

  Move a node to detach links

  """

  ...

def mute_toggle() -> None:

  """

  Toggle muting of selected nodes

  """

  ...

def new_geometry_node_group_assign() -> None:

  """

  Create a new geometry node group and assign it to the active modifier

  """

  ...

def new_geometry_node_group_tool() -> None:

  """

  Create a new geometry node group for an tool

  """

  ...

def new_geometry_nodes_modifier() -> None:

  """

  Create a new modifier with a new geometry node group

  """

  ...

def new_node_tree(type: str = '', name: str = 'NodeTree') -> None:

  """

  Create a new node tree

  """

  ...

def node_color_preset_add(name: str = '', remove_name: bool = False, remove_active: bool = False) -> None:

  """

  Add or remove a Node Color Preset

  """

  ...

def node_copy_color() -> None:

  """

  Copy color to all selected nodes

  """

  ...

def options_toggle() -> None:

  """

  Toggle option buttons display for selected nodes

  """

  ...

def output_file_add_socket(file_path: str = 'Image') -> None:

  """

  Add a new input to a file output node

  """

  ...

def output_file_move_active_socket(direction: str = 'DOWN') -> None:

  """

  Move the active input of a file output node up or down the list

  """

  ...

def output_file_remove_active_socket() -> None:

  """

  Remove the active input from a file output node

  """

  ...

def parent_set() -> None:

  """

  Attach selected nodes

  """

  ...

def preview_toggle() -> None:

  """

  Toggle preview display for selected nodes

  """

  ...

def read_viewlayers() -> None:

  """

  Read all render layers of all used scenes

  """

  ...

def render_changed() -> None:

  """

  Render current scene, when input node's layer has been changed

  """

  ...

def repeat_zone_item_add() -> None:

  """

  Add a repeat item to the repeat zone

  """

  ...

def repeat_zone_item_move(direction: str = 'UP') -> None:

  """

  Move a repeat item up or down in the list

  """

  ...

def repeat_zone_item_remove() -> None:

  """

  Remove a repeat item from the repeat zone

  """

  ...

def resize() -> None:

  """

  Resize a node

  """

  ...

def select(extend: bool = False, deselect: bool = False, toggle: bool = False, deselect_all: bool = False, select_passthrough: bool = False, location: typing.Tuple[int, int] = (0, 0), socket_select: bool = False, clear_viewer: bool = False) -> None:

  """

  Select the node under the cursor

  """

  ...

def select_all(action: str = 'TOGGLE') -> None:

  """

  (De)select all nodes

  """

  ...

def select_box(tweak: bool = False, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True, mode: str = 'SET') -> None:

  """

  Use box selection to select nodes

  """

  ...

def select_circle(x: int = 0, y: int = 0, radius: int = 25, wait_for_input: bool = True, mode: str = 'SET') -> None:

  """

  Use circle selection to select nodes

  """

  ...

def select_grouped(extend: bool = False, type: str = 'TYPE') -> None:

  """

  Select nodes with similar properties

  """

  ...

def select_lasso(tweak: bool = False, path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, mode: str = 'SET') -> None:

  """

  Select nodes using lasso selection

  """

  ...

def select_link_viewer(NODE_OT_select: NODE_OT_select = None, NODE_OT_link_viewer: NODE_OT_link_viewer = None) -> None:

  """

  Select node and link it to a viewer node

  """

  ...

def select_linked_from() -> None:

  """

  Select nodes linked from the selected ones

  """

  ...

def select_linked_to() -> None:

  """

  Select nodes linked to the selected ones

  """

  ...

def select_same_type_step(prev: bool = False) -> None:

  """

  Activate and view same node type, step by step

  """

  ...

def shader_script_update() -> None:

  """

  Update shader script node with new sockets and options from the script

  """

  ...

def simulation_zone_item_add() -> None:

  """

  Add a state item to the simulation zone

  """

  ...

def simulation_zone_item_move(direction: str = 'UP') -> None:

  """

  Move a simulation state item up or down in the list

  """

  ...

def simulation_zone_item_remove() -> None:

  """

  Remove a state item from the simulation zone

  """

  ...

def switch_view_update() -> None:

  """

  Update views of selected node

  """

  ...

def translate_attach(TRANSFORM_OT_translate: TRANSFORM_OT_translate = None, NODE_OT_attach: NODE_OT_attach = None) -> None:

  """

  Move nodes and attach to frame

  """

  ...

def translate_attach_remove_on_cancel(TRANSFORM_OT_translate: TRANSFORM_OT_translate = None, NODE_OT_attach: NODE_OT_attach = None) -> None:

  """

  Move nodes and attach to frame

  """

  ...

def tree_path_parent() -> None:

  """

  Go to parent node tree

  """

  ...

def view_all() -> None:

  """

  Resize view so you can see all nodes

  """

  ...

def view_selected() -> None:

  """

  Resize view so you can see selected nodes

  """

  ...

def viewer_border(xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True) -> None:

  """

  Set the boundaries for viewer operations

  """

  ...

"""


Curves Operators
****************

:func:`convert_from_particle_system`

:func:`convert_to_particle_system`

:func:`delete`

:func:`sculptmode_toggle`

:func:`select_all`

:func:`select_ends`

:func:`select_less`

:func:`select_linked`

:func:`select_more`

:func:`select_random`

:func:`set_selection_domain`

:func:`snap_curves_to_surface`

:func:`surface_set`

"""

import typing

def convert_from_particle_system() -> None:

  """

  Add a new curves object based on the current state of the particle system

  """

  ...

def convert_to_particle_system() -> None:

  """

  Add a new or update an existing hair particle system on the surface object

  """

  ...

def delete() -> None:

  """

  Remove selected control points or curves

  """

  ...

def sculptmode_toggle() -> None:

  """

  Enter/Exit sculpt mode for curves

  """

  ...

def select_all(action: str = 'TOGGLE') -> None:

  """

  (De)select all control points

  """

  ...

def select_ends(amount_start: int = 0, amount_end: int = 1) -> None:

  """

  Select end points of curves

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

def select_random(seed: int = 0, probability: float = 0.5) -> None:

  """

  Randomizes existing selection or create new random selection

  """

  ...

def set_selection_domain(domain: str = 'POINT') -> None:

  """

  Change the mode used for selection masking in curves sculpt mode

  """

  ...

def snap_curves_to_surface(attach_mode: str = 'NEAREST') -> None:

  """

  Move curves so that the first point is exactly on the surface mesh

  """

  ...

def surface_set() -> None:

  """

  Use the active object as surface for selected curves objects and set it as the parent

  """

  ...

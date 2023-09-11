"""


Math Types & Utilities (mathutils)
**********************************

This module provides access to math operations.

Note: Classes, methods and attributes that accept vectors also accept other numeric sequences,
such as tuples, lists.

The :mod:`mathutils` module provides the following classes:

* :class:`Color`,

* :class:`Euler`,

* :class:`Matrix`,

* :class:`Quaternion`,

* :class:`Vector`,

.. code::

  import mathutils
  from math import radians

  vec = mathutils.Vector((1.0, 2.0, 3.0))

  mat_rot = mathutils.Matrix.Rotation(radians(90.0), 4, 'X')
  mat_trans = mathutils.Matrix.Translation(vec)

  mat = mat_trans @ mat_rot
  mat.invert()

  mat3 = mat.to_3x3()
  quat1 = mat.to_quaternion()
  quat2 = mat3.to_quaternion()

  quat_diff = quat1.rotation_difference(quat2)

  print(quat_diff.angle)

:class:`Color`

:class:`Euler`

:class:`Matrix`

:class:`Quaternion`

:class:`Vector`

"""

from . import noise

from . import kdtree

from . import interpolate

from . import geometry

from . import bvhtree

import typing

class Color:

  """

  This object gives access to Colors in Blender.

  Most colors returned by Blender APIs are in scene linear color space, as defined by    the OpenColorIO configuration. The notable exception is user interface theming colors,    which are in sRGB color space.

  .. code::

    import mathutils

    # color values are represented as RGB values from 0 - 1, this is blue
    col = mathutils.Color((0.0, 0.0, 1.0))

    # as well as r/g/b attribute access you can adjust them by h/s/v
    col.s *= 0.5

    # you can access its components by attribute or index
    print("Color R:", col.r)
    print("Color G:", col[1])
    print("Color B:", col[-1])
    print("Color HSV: %.2f, %.2f, %.2f", col[:])


    # components of an existing color can be set
    col[:] = 0.0, 0.5, 1.0

    # components of an existing color can use slice notation to get a tuple
    print("Values: %f, %f, %f" % col[:])

    # colors can be added and subtracted
    col += mathutils.Color((0.25, 0.0, 0.0))

    # Color can be multiplied, in this example color is scaled to 0-255
    # can printed as integers
    print("Color: %d, %d, %d" % (col * 255.0)[:])

    # This example prints the color as hexadecimal
    print("Hexadecimal: %.2x%.2x%.2x" % (int(col.r * 255), int(col.g * 255), int(col.b * 255)))

  """

  def __init__(self, rgb: Vector) -> None:

    """

    :arg rgb:         
      (r, g, b) color values

    :type rgb:        
      3d vector

    """

    ...

  def copy(self) -> Color:

    """

    Returns a copy of this color.

    Note: use this to get a copy of a wrapped color with
no reference to the original data.

    """

    ...

  def freeze(self) -> None:

    """

    Make this object immutable.

    After this the object can be hashed, used in dictionaries & sets.

    """

    ...

  def from_aces_to_scene_linear(self) -> Color:

    """

    Convert from ACES2065-1 linear to scene linear color space.

    """

    ...

  def from_rec709_linear_to_scene_linear(self) -> Color:

    """

    Convert from Rec.709 linear color space to scene linear color space.

    """

    ...

  def from_scene_linear_to_aces(self) -> Color:

    """

    Convert from scene linear to ACES2065-1 linear color space.

    """

    ...

  def from_scene_linear_to_rec709_linear(self) -> Color:

    """

    Convert from scene linear to Rec.709 linear color space.

    """

    ...

  def from_scene_linear_to_srgb(self) -> Color:

    """

    Convert from scene linear to sRGB color space.

    """

    ...

  def from_scene_linear_to_xyz_d65(self) -> Color:

    """

    Convert from scene linear to CIE XYZ (Illuminant D65) color space.

    """

    ...

  def from_srgb_to_scene_linear(self) -> Color:

    """

    Convert from sRGB to scene linear color space.

    """

    ...

  def from_xyz_d65_to_scene_linear(self) -> Color:

    """

    Convert from CIE XYZ (Illuminant D65) to scene linear color space.

    """

    ...

  b: float = ...

  """

  Blue color channel.

  """

  g: float = ...

  """

  Green color channel.

  """

  h: float = ...

  """

  HSV Hue component in [0, 1].

  """

  hsv: float = ...

  """

  HSV Values in [0, 1].

  """

  is_frozen: bool = ...

  """

  True when this object has been frozen (read-only).

  """

  is_valid: bool = ...

  """

  True when the owner of this data is valid.

  """

  is_wrapped: bool = ...

  """

  True when this object wraps external data (read-only).

  """

  owner: typing.Any = ...

  """

  The item this is wrapping or None  (read-only).

  """

  r: float = ...

  """

  Red color channel.

  """

  s: float = ...

  """

  HSV Saturation component in [0, 1].

  """

  v: float = ...

  """

  HSV Value component in [0, 1].

  """

class Euler:

  """

  This object gives access to Eulers in Blender.

  `Euler angles <https://en.wikipedia.org/wiki/Euler_angles>`_ on Wikipedia.

  .. code::

    import mathutils
    import math

    # create a new euler with default axis rotation order
    eul = mathutils.Euler((0.0, math.radians(45.0), 0.0), 'XYZ')

    # rotate the euler
    eul.rotate_axis('Z', math.radians(10.0))

    # you can access its components by attribute or index
    print("Euler X", eul.x)
    print("Euler Y", eul[1])
    print("Euler Z", eul[-1])

    # components of an existing euler can be set
    eul[:] = 1.0, 2.0, 3.0

    # components of an existing euler can use slice notation to get a tuple
    print("Values: %f, %f, %f" % eul[:])

    # the order can be set at any time too
    eul.order = 'ZYX'

    # eulers can be used to rotate vectors
    vec = mathutils.Vector((0.0, 0.0, 1.0))
    vec.rotate(eul)

    # often its useful to convert the euler into a matrix so it can be used as
    # transformations with more flexibility
    mat_rot = eul.to_matrix()
    mat_loc = mathutils.Matrix.Translation((2.0, 3.0, 4.0))
    mat = mat_loc @ mat_rot.to_4x4()

  """

  def __init__(self, angles: Vector, order: str = 'XYZ') -> None:

    """

    :arg angles:      
      Three angles, in radians.

    :type angles:     
      3d vector

    :arg order:       
      Optional order of the angles, a permutation of ``XYZ``.

    :type order:      
      str

    """

    ...

  def copy(self) -> Euler:

    """

    Returns a copy of this euler.

    Note: use this to get a copy of a wrapped euler with
no reference to the original data.

    """

    ...

  def freeze(self) -> None:

    """

    Make this object immutable.

    After this the object can be hashed, used in dictionaries & sets.

    """

    ...

  def make_compatible(self, other: typing.Any) -> None:

    """

    Make this euler compatible with another,
so interpolating between them works as intended.

    Note: the rotation order is not taken into account for this function.

    """

    ...

  def rotate(self, other: Euler) -> None:

    """

    Rotates the euler by another mathutils value.

    """

    ...

  def rotate_axis(self, axis: str, angle: float) -> None:

    """

    Rotates the euler a certain amount and returning a unique euler rotation
(no 720 degree pitches).

    """

    ...

  def to_matrix(self) -> Matrix:

    """

    Return a matrix representation of the euler.

    """

    ...

  def to_quaternion(self) -> Quaternion:

    """

    Return a quaternion representation of the euler.

    """

    ...

  def zero(self) -> None:

    """

    Set all values to zero.

    """

    ...

  is_frozen: bool = ...

  """

  True when this object has been frozen (read-only).

  """

  is_valid: bool = ...

  """

  True when the owner of this data is valid.

  """

  is_wrapped: bool = ...

  """

  True when this object wraps external data (read-only).

  """

  order: str = ...

  """

  Euler rotation order.

  """

  owner: typing.Any = ...

  """

  The item this is wrapping or None  (read-only).

  """

  x: float = ...

  """

  Euler axis angle in radians.

  """

  y: float = ...

  """

  Euler axis angle in radians.

  """

  z: float = ...

  """

  Euler axis angle in radians.

  """

  def __getitem__(self, index: int) -> float:

    """

    Get the angle component at index.

    """

    ...

  def __setitem__(self, index: int, value: float) -> None:

    """

    Set the angle component at index.

    """

    ...

class Matrix:

  """

  This object gives access to Matrices in Blender, supporting square and rectangular
matrices from 2x2 up to 4x4.

  .. code::

    import mathutils
    import math

    # create a location matrix
    mat_loc = mathutils.Matrix.Translation((2.0, 3.0, 4.0))

    # create an identitiy matrix
    mat_sca = mathutils.Matrix.Scale(0.5, 4, (0.0, 0.0, 1.0))

    # create a rotation matrix
    mat_rot = mathutils.Matrix.Rotation(math.radians(45.0), 4, 'X')

    # combine transformations
    mat_out = mat_loc @ mat_rot @ mat_sca
    print(mat_out)

    # extract components back out of the matrix as two vectors and a quaternion
    loc, rot, sca = mat_out.decompose()
    print(loc, rot, sca)

    # recombine extracted components
    mat_out2 = mathutils.Matrix.LocRotScale(loc, rot, sca)
    print(mat_out2)

    # it can also be useful to access components of a matrix directly
    mat = mathutils.Matrix()
    mat[0][0], mat[1][0], mat[2][0] = 0.0, 1.0, 2.0

    mat[0][0:3] = 0.0, 1.0, 2.0

    # each item in a matrix is a vector so vector utility functions can be used
    mat[0].xyz = 0.0, 1.0, 2.0

  """

  def __init__(self, rows: typing.Any = None) -> None:

    """

    :arg rows:        
      Sequence of rows. When omitted, a 4x4 identity matrix is constructed.

    :type rows:       
      2d number sequence

    """

    ...

  @classmethod

  def Diagonal(cls, vector: Vector) -> Matrix:

    """

    Create a diagonal (scaling) matrix using the values from the vector.

    """

    ...

  @classmethod

  def Identity(cls, size: int) -> Matrix:

    """

    Create an identity matrix.

    """

    ...

  @classmethod

  def LocRotScale(cls, location: Vector, rotation: typing.Any, scale: Vector) -> typing.Any:

    """

    Create a matrix combining translation, rotation and scale,
acting as the inverse of the decompose() method.

    Any of the inputs may be replaced with None if not needed.

    .. code::

      # Compute local object transformation matrix:
      if obj.rotation_mode == 'QUATERNION':
          matrix = mathutils.Matrix.LocRotScale(obj.location, obj.rotation_quaternion, obj.scale)
      else:
          matrix = mathutils.Matrix.LocRotScale(obj.location, obj.rotation_euler, obj.scale)

    """

    ...

  @classmethod

  def OrthoProjection(cls, axis: typing.Union[str, Vector], size: int) -> Matrix:

    """

    Create a matrix to represent an orthographic projection.

    """

    ...

  @classmethod

  def Rotation(cls, angle: float, size: int, axis: typing.Union[str, Vector]) -> Matrix:

    """

    Create a matrix representing a rotation.

    """

    ...

  @classmethod

  def Scale(cls, factor: float, size: int, axis: Vector) -> Matrix:

    """

    Create a matrix representing a scaling.

    """

    ...

  @classmethod

  def Shear(cls, plane: str, size: int, factor: float) -> Matrix:

    """

    Create a matrix to represent an shear transformation.

    """

    ...

  @classmethod

  def Translation(cls, vector: Vector) -> Matrix:

    """

    Create a matrix representing a translation.

    """

    ...

  def adjugate(self) -> None:

    """

    Set the matrix to its adjugate.

    `Adjugate matrix <https://en.wikipedia.org/wiki/Adjugate_matrix>`_ on Wikipedia.

    """

    ...

  def adjugated(self) -> Matrix:

    """

    Return an adjugated copy of the matrix.

    """

    ...

  def copy(self) -> Matrix:

    """

    Returns a copy of this matrix.

    """

    ...

  def decompose(self) -> typing.Any:

    """

    Return the translation, rotation, and scale components of this matrix.

    """

    ...

  def determinant(self) -> float:

    """

    Return the determinant of a matrix.

    `Determinant <https://en.wikipedia.org/wiki/Determinant>`_ on Wikipedia.

    """

    ...

  def freeze(self) -> None:

    """

    Make this object immutable.

    After this the object can be hashed, used in dictionaries & sets.

    """

    ...

  def identity(self) -> None:

    """

    Set the matrix to the identity matrix.

    Note: An object with a location and rotation of zero, and a scale of one
will have an identity matrix.

    `Identity matrix <https://en.wikipedia.org/wiki/Identity_matrix>`_ on Wikipedia.

    """

    ...

  def invert(self, fallback: Matrix = None) -> None:

    """

    Set the matrix to its inverse.

    `Inverse matrix <https://en.wikipedia.org/wiki/Inverse_matrix>`_ on Wikipedia.

    """

    ...

  def invert_safe(self) -> None:

    """

    Set the matrix to its inverse, will never error.
If degenerated (e.g. zero scale on an axis), add some epsilon to its diagonal, to get an invertible one.
If tweaked matrix is still degenerated, set to the identity matrix instead.

    `Inverse Matrix <https://en.wikipedia.org/wiki/Inverse_matrix>`_ on Wikipedia.

    """

    ...

  def inverted(self, fallback: typing.Any = None) -> Matrix:

    """

    Return an inverted copy of the matrix.

    """

    ...

  def inverted_safe(self) -> Matrix:

    """

    Return an inverted copy of the matrix, will never error.
If degenerated (e.g. zero scale on an axis), add some epsilon to its diagonal, to get an invertible one.
If tweaked matrix is still degenerated, return the identity matrix instead.

    """

    ...

  def lerp(self, other: Matrix, factor: float) -> Matrix:

    """

    Returns the interpolation of two matrices. Uses polar decomposition, see   "Matrix Animation and Polar Decomposition", Shoemake and Duff, 1992.

    """

    ...

  def normalize(self) -> None:

    """

    Normalize each of the matrix columns.

    """

    ...

  def normalized(self) -> Matrix:

    """

    Return a column normalized matrix

    """

    ...

  def resize_4x4(self) -> None:

    """

    Resize the matrix to 4x4.

    """

    ...

  def rotate(self, other: Euler) -> None:

    """

    Rotates the matrix by another mathutils value.

    Note: If any of the columns are not unit length this may not have desired results.

    """

    ...

  def to_2x2(self) -> Matrix:

    """

    Return a 2x2 copy of this matrix.

    """

    ...

  def to_3x3(self) -> Matrix:

    """

    Return a 3x3 copy of this matrix.

    """

    ...

  def to_4x4(self) -> Matrix:

    """

    Return a 4x4 copy of this matrix.

    """

    ...

  def to_euler(self, order: str, euler_compat: Euler) -> Euler:

    """

    Return an Euler representation of the rotation matrix
(3x3 or 4x4 matrix only).

    """

    ...

  def to_quaternion(self) -> Quaternion:

    """

    Return a quaternion representation of the rotation matrix.

    """

    ...

  def to_scale(self) -> Vector:

    """

    Return the scale part of a 3x3 or 4x4 matrix.

    Note: This method does not return a negative scale on any axis because it is not possible to obtain this data from the matrix alone.

    """

    ...

  def to_translation(self) -> Vector:

    """

    Return the translation part of a 4 row matrix.

    """

    ...

  def transpose(self) -> None:

    """

    Set the matrix to its transpose.

    `Transpose <https://en.wikipedia.org/wiki/Transpose>`_ on Wikipedia.

    """

    ...

  def transposed(self) -> Matrix:

    """

    Return a new, transposed matrix.

    """

    ...

  def zero(self) -> Matrix:

    """

    Set all the matrix values to zero.

    """

    ...

  col: Matrix = ...

  """

  Access the matrix by columns, 3x3 and 4x4 only, (read-only).

  """

  is_frozen: bool = ...

  """

  True when this object has been frozen (read-only).

  """

  is_identity: bool = ...

  """

  True if this is an identity matrix (read-only).

  """

  is_negative: bool = ...

  """

  True if this matrix results in a negative scale, 3x3 and 4x4 only, (read-only).

  """

  is_orthogonal: bool = ...

  """

  True if this matrix is orthogonal, 3x3 and 4x4 only, (read-only).

  """

  is_orthogonal_axis_vectors: bool = ...

  """

  True if this matrix has got orthogonal axis vectors, 3x3 and 4x4 only, (read-only).

  """

  is_valid: bool = ...

  """

  True when the owner of this data is valid.

  """

  is_wrapped: bool = ...

  """

  True when this object wraps external data (read-only).

  """

  median_scale: float = ...

  """

  The average scale applied to each axis (read-only).

  """

  owner: typing.Any = ...

  """

  The item this is wrapping or None  (read-only).

  """

  row: Matrix = ...

  """

  Access the matrix by rows (default), (read-only).

  """

  translation: Vector = ...

  """

  The translation component of the matrix.

  """

  def __add__(self, value: Matrix) -> Matrix:

    """

    Add another matrix to this one.

    """

    ...

  def __sub__(self, value: Matrix) -> Matrix:

    """

    Subtract another matrix from this one.

    """

    ...

  def __mul__(self, value: typing.Union[Matrix, float]) -> Matrix:

    """

    Multiply this matrix with another one or a scala value.

    """

    ...

  def __rmul__(self, value: float) -> Matrix:

    """

    Multiply this matrix with a scala value.

    """

    ...

  def __imul__(self, value: typing.Union[Matrix, float]) -> Matrix:

    """

    Multiply this matrix by another one or a scala value.

    """

    ...

  def __matmul__(self, value: typing.Union[Matrix, Vector, Quaternion]) -> typing.Union[Matrix, Vector, Quaternion]:

    """

    Multiply this matrix with another matrix, a vector, or quaternion.

    """

    ...

  def __imatmul__(self, value: typing.Union[Matrix, Vector, Quaternion]) -> typing.Union[Matrix, Vector, Quaternion]:

    """

    Multiply this matrix with another matrix, a vector, or quaternion.

    """

    ...

  def __invert__(self) -> Matrix:

    """

    Invert this matrix.

    """

    ...

  def __truediv__(self, value: float) -> Matrix:

    """

    Divide this matrix by a float value.

    """

    ...

  def __itruediv__(self, value: float) -> Matrix:

    """

    Divide this matrix by a float value.

    """

    ...

  def __getitem__(self, index: int) -> Vector:

    """

    Get the row at given index.

    """

    ...

  def __setitem__(self, index: int, value: typing.Union[Vector, typing.Tuple[float, ...]]) -> None:

    """

    Set the row at given index.

    """

    ...

class Quaternion:

  """

  This object gives access to Quaternions in Blender.

  The constructor takes arguments in various forms:

  (), *no args*
    Create an identity quaternion

  (*wxyz*)
    Create a quaternion from a ``(w, x, y, z)`` vector.

  (*exponential_map*)
    Create a quaternion from a 3d exponential map vector.

    :meth:`to_exponential_map`

  (*axis, angle*)
    Create a quaternion representing a rotation of *angle* radians over *axis*.

    :meth:`to_axis_angle`

  .. code::

    import mathutils
    import math

    # a new rotation 90 degrees about the Y axis
    quat_a = mathutils.Quaternion((0.7071068, 0.0, 0.7071068, 0.0))

    # passing values to Quaternion's directly can be confusing so axis, angle
    # is supported for initializing too
    quat_b = mathutils.Quaternion((0.0, 1.0, 0.0), math.radians(90.0))

    print("Check quaternions match", quat_a == quat_b)

    # like matrices, quaternions can be multiplied to accumulate rotational values
    quat_a = mathutils.Quaternion((0.0, 1.0, 0.0), math.radians(90.0))
    quat_b = mathutils.Quaternion((0.0, 0.0, 1.0), math.radians(45.0))
    quat_out = quat_a @ quat_b

    # print the quat, euler degrees for mere mortals and (axis, angle)
    print("Final Rotation:")
    print(quat_out)
    print("%.2f, %.2f, %.2f" % tuple(math.degrees(a) for a in quat_out.to_euler()))
    print("(%.2f, %.2f, %.2f), %.2f" % (quat_out.axis[:] +
                                        (math.degrees(quat_out.angle), )))

    # multiple rotations can be interpolated using the exponential map
    quat_c = mathutils.Quaternion((1.0, 0.0, 0.0), math.radians(15.0))
    exp_avg = (quat_a.to_exponential_map() +
               quat_b.to_exponential_map() +
               quat_c.to_exponential_map()) / 3.0
    quat_avg = mathutils.Quaternion(exp_avg)
    print("Average rotation:")
    print(quat_avg)

  """

  def __init__(self, seq: Vector, angle: float = None) -> None:

    """

    :arg seq:         
      size 3 or 4

    :type seq:        
      :class:`Vector`

    :arg angle:       
      rotation angle, in radians

    :type angle:      
      float

    """

    ...

  def conjugate(self) -> None:

    """

    Set the quaternion to its conjugate (negate x, y, z).

    """

    ...

  def conjugated(self) -> Quaternion:

    """

    Return a new conjugated quaternion.

    """

    ...

  def copy(self) -> Quaternion:

    """

    Returns a copy of this quaternion.

    Note: use this to get a copy of a wrapped quaternion with
no reference to the original data.

    """

    ...

  def cross(self, other: Quaternion) -> Quaternion:

    """

    Return the cross product of this quaternion and another.

    """

    ...

  def dot(self, other: Quaternion) -> float:

    """

    Return the dot product of this quaternion and another.

    """

    ...

  def freeze(self) -> None:

    """

    Make this object immutable.

    After this the object can be hashed, used in dictionaries & sets.

    """

    ...

  def identity(self) -> Quaternion:

    """

    Set the quaternion to an identity quaternion.

    """

    ...

  def invert(self) -> None:

    """

    Set the quaternion to its inverse.

    """

    ...

  def inverted(self) -> Quaternion:

    """

    Return a new, inverted quaternion.

    """

    ...

  def make_compatible(self, other: typing.Any) -> None:

    """

    Make this quaternion compatible with another,
so interpolating between them works as intended.

    """

    ...

  def negate(self) -> Quaternion:

    """

    Set the quaternion to its negative.

    """

    ...

  def normalize(self) -> None:

    """

    Normalize the quaternion.

    """

    ...

  def normalized(self) -> Quaternion:

    """

    Return a new normalized quaternion.

    """

    ...

  def rotate(self, other: Euler) -> None:

    """

    Rotates the quaternion by another mathutils value.

    """

    ...

  def rotation_difference(self, other: Quaternion) -> Quaternion:

    """

    Returns a quaternion representing the rotational difference.

    """

    ...

  def slerp(self, other: Quaternion, factor: float) -> Quaternion:

    """

    Returns the interpolation of two quaternions.

    """

    ...

  def to_axis_angle(self) -> typing.Any:

    """

    Return the axis, angle representation of the quaternion.

    """

    ...

  def to_euler(self, order: str, euler_compat: Euler) -> Euler:

    """

    Return Euler representation of the quaternion.

    """

    ...

  def to_exponential_map(self) -> Vector:

    """

    Return the exponential map representation of the quaternion.

    This representation consist of the rotation axis multiplied by the rotation angle.
Such a representation is useful for interpolation between multiple orientations.

    To convert back to a quaternion, pass it to the :class:`Quaternion` constructor.

    """

    ...

  def to_matrix(self) -> Matrix:

    """

    Return a matrix representation of the quaternion.

    """

    ...

  def to_swing_twist(self, axis: typing.Any) -> typing.Any:

    """

    Split the rotation into a swing quaternion with the specified
axis fixed at zero, and the remaining twist rotation angle.

    """

    ...

  angle: float = ...

  """

  Angle of the quaternion.

  """

  axis: Vector = ...

  """

  Quaternion axis as a vector.

  """

  is_frozen: bool = ...

  """

  True when this object has been frozen (read-only).

  """

  is_valid: bool = ...

  """

  True when the owner of this data is valid.

  """

  is_wrapped: bool = ...

  """

  True when this object wraps external data (read-only).

  """

  magnitude: float = ...

  """

  Size of the quaternion (read-only).

  """

  owner: typing.Any = ...

  """

  The item this is wrapping or None  (read-only).

  """

  w: float = ...

  """

  Quaternion axis value.

  """

  x: float = ...

  """

  Quaternion axis value.

  """

  y: float = ...

  """

  Quaternion axis value.

  """

  z: float = ...

  """

  Quaternion axis value.

  """

  def __add__(self, value: Quaternion) -> Quaternion:

    """

    Add another quaternion to this one.

    """

    ...

  def __sub__(self, value: Quaternion) -> Quaternion:

    """

    Subtract another quaternion from this one.

    """

    ...

  def __mul__(self, value: typing.Union[Quaternion, float]) -> Quaternion:

    """

    Multiply this quaternion with another one or a scala value.

    """

    ...

  def __rmul__(self, value: float) -> Quaternion:

    """

    Multiply this quaternion with a scala value.

    """

    ...

  def __imul__(self, value: typing.Union[Quaternion, float]) -> Quaternion:

    """

    Multiply this quaternion with another one or a scala value.

    """

    ...

  def __matmul__(self, value: typing.Union[Quaternion, Vector]) -> typing.Union[Quaternion, Vector]:

    """

    Multiply with another quaternion or a vector.

    """

    ...

  def __imatmul__(self, value: typing.Union[Quaternion, Vector]) -> typing.Union[Quaternion, Vector]:

    """

    Multiply with another quaternion or a vector.

    """

    ...

  def __truediv__(self, value: float) -> Quaternion:

    """

    Divide this quaternion by a float value.

    """

    ...

  def __itruediv__(self, value: float) -> Quaternion:

    """

    Divide this quaternion by a float value.

    """

    ...

  def __getitem__(self, index: int) -> float:

    """

    Get quaternion component at index.

    """

    ...

  def __setitem__(self, index: int, value: float) -> None:

    """

    Set quaternion component at index.

    """

    ...

class Vector:

  """

  This object gives access to Vectors in Blender.

  .. code::

    import mathutils

    # zero length vector
    vec = mathutils.Vector((0.0, 0.0, 1.0))

    # unit length vector
    vec_a = vec.normalized()

    vec_b = mathutils.Vector((0.0, 1.0, 2.0))

    vec2d = mathutils.Vector((1.0, 2.0))
    vec3d = mathutils.Vector((1.0, 0.0, 0.0))
    vec4d = vec_a.to_4d()

    # other mathutuls types
    quat = mathutils.Quaternion()
    matrix = mathutils.Matrix()

    # Comparison operators can be done on Vector classes:

    # (In)equality operators == and != test component values, e.g. 1,2,3 != 3,2,1
    vec_a == vec_b
    vec_a != vec_b

    # Ordering operators >, >=, > and <= test vector length.
    vec_a > vec_b
    vec_a >= vec_b
    vec_a < vec_b
    vec_a <= vec_b


    # Math can be performed on Vector classes
    vec_a + vec_b
    vec_a - vec_b
    vec_a @ vec_b
    vec_a * 10.0
    matrix @ vec_a
    quat @ vec_a
    -vec_a


    # You can access a vector object like a sequence
    x = vec_a[0]
    len(vec)
    vec_a[:] = vec_b
    vec_a[:] = 1.0, 2.0, 3.0
    vec2d[:] = vec3d[:2]


    # Vectors support 'swizzle' operations
    # See https://en.wikipedia.org/wiki/Swizzling_(computer_graphics)
    vec.xyz = vec.zyx
    vec.xy = vec4d.zw
    vec.xyz = vec4d.wzz
    vec4d.wxyz = vec.yxyx

  """

  def __init__(self, seq: typing.Sequence[typing.Any]) -> None:

    """

    :arg seq:         
      Components of the vector, must be a sequence of at least two

    :type seq:        
      sequence of numbers

    """

    ...

  @classmethod

  def Fill(cls, size: int, fill: float = 0.0) -> None:

    """

    Create a vector of length size with all values set to fill.

    """

    ...

  @classmethod

  def Linspace(cls, start: int, stop: int, size: int) -> None:

    """

    Create a vector of the specified size which is filled with linearly spaced values between start and stop values.

    """

    ...

  @classmethod

  def Range(cls, start: int, stop: int, step: int = 1) -> None:

    """

    Create a filled with a range of values.

    """

    ...

  @classmethod

  def Repeat(cls, vector: typing.Any, size: int) -> None:

    """

    Create a vector by repeating the values in vector until the required size is reached.

    """

    ...

  def angle(self, other: Vector, fallback: typing.Any = None) -> float:

    """

    Return the angle between two vectors.

    """

    ...

  def angle_signed(self, other: Vector, fallback: typing.Any) -> float:

    """

    Return the signed angle between two 2D vectors (clockwise is positive).

    """

    ...

  def copy(self) -> Vector:

    """

    Returns a copy of this vector.

    Note: use this to get a copy of a wrapped vector with
no reference to the original data.

    """

    ...

  def cross(self, other: Vector) -> typing.Union[Vector, float]:

    """

    Return the cross product of this vector and another.

    Note: both vectors must be 2D or 3D

    """

    ...

  def dot(self, other: Vector) -> float:

    """

    Return the dot product of this vector and another.

    """

    ...

  def freeze(self) -> None:

    """

    Make this object immutable.

    After this the object can be hashed, used in dictionaries & sets.

    """

    ...

  def lerp(self, other: Vector, factor: float) -> Vector:

    """

    Returns the interpolation of two vectors.

    """

    ...

  def negate(self) -> None:

    """

    Set all values to their negative.

    """

    ...

  def normalize(self) -> None:

    """

    Normalize the vector, making the length of the vector always 1.0.

    Warning: Normalizing a vector where all values are zero has no effect.

    Note: Normalize works for vectors of all sizes,
however 4D Vectors w axis is left untouched.

    """

    ...

  def normalized(self) -> Vector:

    """

    Return a new, normalized vector.

    """

    ...

  def orthogonal(self) -> Vector:

    """

    Return a perpendicular vector.

    Note: the axis is undefined, only use when any orthogonal vector is acceptable.

    """

    ...

  def project(self, other: Vector) -> Vector:

    """

    Return the projection of this vector onto the *other*.

    """

    ...

  def reflect(self, mirror: Vector) -> Vector:

    """

    Return the reflection vector from the *mirror* argument.

    """

    ...

  def resize(self, size: typing.Any = 3) -> None:

    """

    Resize the vector to have size number of elements.

    """

    ...

  def resize_2d(self) -> None:

    """

    Resize the vector to 2D  (x, y).

    """

    ...

  def resize_3d(self) -> None:

    """

    Resize the vector to 3D  (x, y, z).

    """

    ...

  def resize_4d(self) -> None:

    """

    Resize the vector to 4D (x, y, z, w).

    """

    ...

  def resized(self, size: typing.Any = 3) -> Vector:

    """

    Return a resized copy of the vector with size number of elements.

    """

    ...

  def rotate(self, other: Euler) -> None:

    """

    Rotate the vector by a rotation value.

    Note: 2D vectors are a special case that can only be rotated by a 2x2 matrix.

    """

    ...

  def rotation_difference(self, other: Vector) -> Quaternion:

    """

    Returns a quaternion representing the rotational difference between this
vector and another.

    Note: 2D vectors raise an :exc:`AttributeError`.

    """

    ...

  def slerp(self, other: Vector, factor: float, fallback: typing.Any = None) -> Vector:

    """

    Returns the interpolation of two non-zero vectors (spherical coordinates).

    """

    ...

  def to_2d(self) -> Vector:

    """

    Return a 2d copy of the vector.

    """

    ...

  def to_3d(self) -> Vector:

    """

    Return a 3d copy of the vector.

    """

    ...

  def to_4d(self) -> Vector:

    """

    Return a 4d copy of the vector.

    """

    ...

  def to_track_quat(self, track: str, up: str) -> Quaternion:

    """

    Return a quaternion rotation from the vector and the track and up axis.

    """

    ...

  def to_tuple(self, precision: int = -1) -> typing.Tuple[typing.Any, ...]:

    """

    Return this vector as a tuple with.

    """

    ...

  def zero(self) -> None:

    """

    Set all values to zero.

    """

    ...

  is_frozen: bool = ...

  """

  True when this object has been frozen (read-only).

  """

  is_valid: bool = ...

  """

  True when the owner of this data is valid.

  """

  is_wrapped: bool = ...

  """

  True when this object wraps external data (read-only).

  """

  length: float = ...

  """

  Vector Length.

  """

  length_squared: float = ...

  """

  Vector length squared (v.dot(v)).

  """

  magnitude: float = ...

  """

  Vector Length.

  """

  owner: typing.Any = ...

  """

  The item this is wrapping or None  (read-only).

  """

  w: float = ...

  """

  Vector W axis (4D Vectors only).

  """

  ww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  www: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwwx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwwy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwwz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wwzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxwx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxwy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxwz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wxzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wyww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wywx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wywy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wywz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wyxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wyxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wyxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wyxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wyyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wyyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wyyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wyyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wyzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wyzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wyzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wyzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzwx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzwy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzwz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  wzzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  x: float = ...

  """

  Vector X axis.

  """

  xw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwwx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwwy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwwz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xwzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxwx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxwy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxwz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xxzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xyww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xywx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xywy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xywz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xyxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xyxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xyxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xyxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xyyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xyyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xyyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xyyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xyzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xyzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xyzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xyzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzwx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzwy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzwz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  xzzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  y: float = ...

  """

  Vector Y axis.

  """

  yw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywwx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywwy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywwz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ywzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxwx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxwy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxwz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yxzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yyww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yywx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yywy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yywz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yyxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yyxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yyxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yyxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yyyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yyyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yyyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yyyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yyzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yyzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yyzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yyzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzwx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzwy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzwz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  yzzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  z: float = ...

  """

  Vector Z axis (3D Vectors only).

  """

  zw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwwx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwwy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwwz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zwzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxwx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxwy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxwz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zxzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zyww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zywx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zywy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zywz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zyxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zyxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zyxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zyxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zyyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zyyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zyyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zyyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zyzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zyzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zyzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zyzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzww: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzwx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzwy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzwz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzxw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzxx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzxy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzxz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzyw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzyx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzyy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzyz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzzw: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzzx: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzzy: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  zzzz: typing.Any = ...

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  def __add__(self, value: Vector) -> Vector:

    """

    Add another vector to this one.

    """

    ...

  def __sub__(self, value: Vector) -> Vector:

    """

    Subtract another vector from this one.

    """

    ...

  def __mul__(self, value: typing.Union[Vector, float]) -> Vector:

    """

    Multiply this vector with another one or a scala value.

    """

    ...

  def __rmul__(self, value: float) -> Vector:

    """

    Multiply this vector with a scala value.

    """

    ...

  def __imul__(self, value: typing.Union[Vector, float]) -> Vector:

    """

    Multiply this vector with another one or a scala value.

    """

    ...

  def __matmul__(self, value: typing.Union[Matrix, Vector]) -> typing.Union[Vector, float]:

    """

    Multiply this vector with a matrix or another vector.

    """

    ...

  def __imatmul__(self, value: typing.Union[Matrix, Vector]) -> typing.Union[Vector, float]:

    """

    Multiply this vector with a matrix or another vector.

    """

    ...

  def __truediv__(self, value: float) -> Vector:

    """

    Divide this vector by a float value.

    """

    ...

  def __itruediv__(self, value: float) -> Vector:

    """

    Divide this vector by a float value.

    """

    ...

  def __getitem__(self, index: int) -> float:

    """

    Get vector component at index.

    """

    ...

  def __setitem__(self, index: int, value: float) -> None:

    """

    Set vector component at index.

    """

    ...

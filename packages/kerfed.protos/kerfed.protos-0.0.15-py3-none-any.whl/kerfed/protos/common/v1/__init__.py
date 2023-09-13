# kerfed.protos.common.v1
# ------------
#
# Helper to keep proto imports in one place.


from datetime import datetime
from typing import Any, List

from .address_pb2 import PostalAddress
from .combo_pb2 import Combo, ComboDescription, Combos
from .error_pb2 import Error
from .fab_pb2 import (
    AddFabrication,
    BentFabrication,
    FlatFabrication,
    PartFabrication,
    RollFabrication,
    TurnFabrication,
)
from .fileblob_pb2 import FileBlob
from .geometry_pb2 import Box, Cylinder, Geometry, Mesh
from .machine_pb2 import Machine
from .mill_pb2 import (
    CutDrill,
    CutFace,
    CutMill,
    Fixture,
    FixtureStrategy,
    MillFabrication,
    MillMachine,
    MillPreprocess,
)
from .model_pb2 import Model
from .money_pb2 import Money
from .ndarray_pb2 import NDArray, RigidTransform
from .order_pb2 import Order
from .outcome_pb2 import Outcome
from .price_pb2 import LinePrice, LineSpec, Operation, PriceMetadata
from .scene_pb2 import GeometrySummary, Scene
from .shipping_pb2 import ShippingParcel, ShippingRate
from .shop_pb2 import Shop, ShopDisbursement, ShopManufacturing
from .stock_pb2 import Stock, StockKind

# standard library
from .timestamp_pb2 import Timestamp
from .tool_pb2 import Tool, ToolParameters, ToolShape

try:
    import numpy as np
    from numpy.typing import ArrayLike as NumpyLike
except BaseException:
    # if numpy isn't installed just run as an any-type
    from typing import Any as NumpyLike

try:
    from google.protobuf.json_format import MessageToDict
except BaseException as E:
    MessageToDict = E

try:
    from trimesh import Trimesh
except BaseException:
    from typing import Any as Trimesh


def sum_money(monies: List[Money]) -> Money:
    """
    Sum a list of Money messages.

    Parameters
    ------------
    money : List[Money]
      List of money
    """
    # the currency code, i.e. 'usd'
    currency = monies[0].currency
    # we can only sum money in the same currency
    if any(currency != m.currency for m in monies[1:]):
        raise ValueError("Currencies must match!")

    # sum and return
    return Money(currency=currency, amount=sum(m.amount for m in monies))


def message_to_dict(msg, **kwargs) -> dict:
    """
    Convert a protobuf message to dict preserving the field names.

    Parameters
    -----------
    msg : protobuf
      Message to convert to a dict

    Returns
    -----------
    converted : dict
      Message converted to a dict.
    """
    return MessageToDict(msg, preserving_proto_field_name=True, **kwargs)


def format_money(money: Money) -> str:
    """
    Format a protobuf money message.

    Parameters
    -----------
    money : kerfed.protos.v1.money_pb2.Money
      Money object.

    Returns
    --------
    formatted : str
      Formatted string to show a user.
    """
    if money.currency.lower() == "usd":
        return f"${money.amount / 100.0:0.2f}"
    else:
        return f"{money.amount / 100} {money.currency.upper()}"


def numpy_to_rigid(matrix: NumpyLike) -> RigidTransform:
    """
    Convert a (4, 4) rigid homogenous transform
    to a protobuf RigidTransform object.


    Parameters
    -----------
    matrix : (4, 4) float
      Rigid homogeneous transform.

    Returns
    ------------
    rigid
      Rigid transform object.
    """
    assert matrix.shape == (4, 4)
    # strip off the last row which is [0, 0, 0, 1]
    # and make sure it's a double and flatten
    return RigidTransform(values=matrix[:3, :].astype(np.float64).ravel().tolist())


def rigid_to_numpy(rigid: RigidTransform) -> NumpyLike:
    """
    Convert a proto RigidTransform into a numpy array.

    Parameters
    --------------
    rigid
      Transformation passed over the wire.

    Returns
    -------------
    matrix : (4, 4) float
      Homogeneous transformation matrix.
    """
    if len(rigid.values) == 0:
        # empty messages return identity matrix
        return np.eye(4, dtype=np.float64)
    elif len(rigid.values) == 12:
        # transmitted with skipped the last row
        matrix = np.eye(4, dtype=np.float64)
        matrix[:3, :] = np.array(rigid.values, dtype=np.float64).reshape((3, 4))
    elif len(rigid.values) == 16:
        matrix = np.array(rigid.values, dtype=np.float64).reshape((4, 4))
    else:
        raise ValueError("transforms must be 0, 12 or 16 values!")

    # should be a rigid transform
    assert np.allclose(np.dot(matrix[:3, :3], matrix[:3, :3].T), np.eye(3))

    return matrix


def numpy_to_proto(array: NumpyLike) -> NDArray:
    """
    Convert a `numpy.ndarray` to a `proto.NDArray` object.

    Parameters
    -----------
    array : numpy.ndarray
      Multidimensional array

    Returns
    ----------
    serialized : proto.NDArray
      Serialized ND array.
    """
    assert isinstance(array, np.ndarray)

    # get the datatype kind
    dtype = {"i": "int64", "f": "float64"}[array.dtype.kind]
    return NDArray(shape=array.shape, **{dtype: array.ravel().tolist()})


def proto_to_numpy(message: NDArray) -> NumpyLike:
    """
    Convert a Protobuf NDArray message to a numpy array.

    Parameters
    -----------
    message : kerfed.protos.v1.ndarray.NDArray
      Serialized array

    Returns
    -------------
    array : (shape) float64 or int64
      Data converted
    """
    assert isinstance(message, NDArray)

    if len(message.float64) > 0:
        return np.array(message.float64, dtype=np.float64).reshape(message.shape)
    elif len(message.int64) > 0:
        return np.array(message.int64, dtype=np.int64).reshape(message.shape)

    raise ValueError("message contained no data!")


def proto_to_datetime(stamp: Timestamp) -> datetime:
    """
    Convert a proto timestamp method to a Python datetime.

    Parameters
    -----------
    stamp : kerfed.protos.common.v1.Timestamp
      Over the wire proto timestamp

    Returns
    ----------
    date : datetime
      Native Python datetime object.
    """
    # utcfromtimestamp was not what I wanted even though it seemed like it.
    return datetime.fromtimestamp(float(stamp.seconds) + float(stamp.nanos) * 1e-9)


def datetime_to_proto(stamp: datetime) -> Timestamp:
    """
    Convert a native Python datetime into a proto message.

    Parameters
    --------------
    stamp : datetime
      Source timestamp.

    Returns
    ---------
    proto : kerfed.protos.common.v1.Timestamp
      Converted timestamp in proto.
    """
    seconds = stamp.timestamp()
    nanos = round((seconds % 1.0) * 1e9)
    return Timestamp(seconds=int(seconds), nanos=nanos)


def mesh_to_proto(mesh: Trimesh) -> Geometry:
    """
    Convert a native Trimesh object into a proto Mesh.
    """
    import trimesh

    if isinstance(mesh, trimesh.primitives.Box):
        # serialized Box primitive as box
        p = mesh.primitive
        return Geometry(
            box=Box(x=p.extents[0], y=p.extents[1], z=p.extents[2]),
            transform=numpy_to_rigid(p.transform),
        )
    elif isinstance(mesh, trimesh.Trimesh):
        export = mesh.export(file_type="glb")
        # serialize mesh vertices
        return Geometry(mesh=Mesh(blob=FileBlob(name="neutral.glb", data=export)))
    else:
        raise ValueError(f"unsupported kind: `{type(mesh)}`")


def proto_to_mesh(proto: Geometry) -> Trimesh:
    """
    Convert a protobuf Geometry into a native Trimesh object.
    """
    import trimesh

    if len(proto.transform.values) > 0:
        transform = rigid_to_numpy(proto.transform)
    else:
        transform = None

    if proto.HasField("mesh"):
        blob = proto.mesh.blob
        if blob.name != "neutral.glb":
            raise ValueError(blob.name)
        scene = trimesh.load_mesh(
            file_obj=trimesh.util.wrap_as_stream(blob.data),
            file_type="glb",
            process=False,
        )
        assert len(scene.geometry) == 1
        return next(iter(scene.geometry.values()))
    elif proto.HasField("box"):
        box = proto.box
        return trimesh.primitives.Box(
            extents=[box.x, box.y, box.z], transform=transform
        )
    else:
        raise NotImplementedError()


__all__ = [
    "PostalAddress",
    "ShippingRate",
    "ShippingParcel",
    "Model",
    "Money",
    "Order",
    "PartFabrication",
    "LinePrice",
    "LineSpec",
    "Operation",
    "PriceMetadata",
    "Machine",
    "Error",
    "Stock",
    "StockKind",
    "Outcome",
    "FileBlob",
    "NDArray",
    "Combo",
    "Combos",
    "ComboDescription",
    "Scene",
    "Timestamp",
    "proto_to_datetime",
    "datetime_to_proto",
    "GeometrySummary",
    "FlatFabrication",
    "AddFabrication",
    "TurnFabrication",
    "RollFabrication",
    "BentFabrication",
    "MillFabrication",
]

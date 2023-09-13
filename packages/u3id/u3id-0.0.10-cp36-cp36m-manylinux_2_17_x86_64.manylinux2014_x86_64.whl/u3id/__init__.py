import sys
import os

version = (0, 0, 10)
__version__ = "0.0.10"

if os.environ.get("MSGPACK_PUREPYTHON") or sys.version_info[0] == 2:
    from .fallback import U3IDFactory, U3ID
else:
    try:
        from ._u3id import U3IDFactory, U3ID
    except ImportError:
        from .fallback import U3IDFactory, U3ID

from .fallback import U3IDFactory as U3IDFactory_py, U3ID as U3ID_py
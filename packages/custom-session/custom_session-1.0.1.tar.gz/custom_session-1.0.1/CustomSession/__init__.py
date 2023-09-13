try:
    from models import SessionMetaData
    from exceptions import *
    from sessions.async_session import AsyncSession
    from sessions.sync_session import SyncSession
except ModuleNotFoundError:
    from .models import SessionMetaData
    from .exceptions import *
    from .sessions.async_session import AsyncSession
    from .sessions.sync_session import SyncSession

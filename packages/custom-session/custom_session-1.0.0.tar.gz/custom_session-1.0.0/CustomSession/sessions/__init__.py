try:
    from async_session import AsyncSession
    from sync_session import SyncSession
except ImportError:
    from .async_session import AsyncSession
    from .sync_session import SyncSession

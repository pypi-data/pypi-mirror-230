try:
    from models import SessionMetaData
    from exceptions import *
    from sessions.async_session import AsyncSession
    from sessions.sync_session import SyncSession
    from identity import RandomIdentity, Address, Email, CreditCard, Person
except ModuleNotFoundError:
    from .models import SessionMetaData
    from .exceptions import *
    from .sessions.async_session import AsyncSession
    from .sessions.sync_session import SyncSession
    from .identity import RandomIdentity, Address, Email, CreditCard, Person

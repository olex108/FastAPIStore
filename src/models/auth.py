from .base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy import func

from datetime import datetime, timezone
from datetime import timedelta


def get_refresh_expire():
    return datetime.now(timezone.utc) + timedelta(days=7)


class RefreshSession(Base):
    __tablename__ = "refresh_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    refresh_token: Mapped[str] = mapped_column(String, unique=True, index=True)
    expires_at: Mapped[datetime] =  mapped_column(
        DateTime(timezone=True),
        default=get_refresh_expire
    )

from typing import Optional
from datetime import datetime, timedelta

from croydon import ctx
from croydon.models import StorableModel
from croydon.models.fields import StringField, DatetimeField, ReferenceField, OnDestroy, BoolField
from croydon.models.index import Index, IndexDirection, IndexKey
from croydon.util import now, uuid4_string

from .user import User


class Token(StorableModel):

    COLLECTION = "tokens"
    KEY_FIELD = "token"
    INDEXES = [
        Index(
            keys=[
                IndexKey("user_id", IndexDirection.ASCENDING),
                IndexKey("token_type", IndexDirection.ASCENDING),
            ]
        )
    ]

    DEFAULT_TTL = timedelta(days=90)

    token_type = StringField(default="auth", required=True, rejected=True)
    token = StringField(default=uuid4_string, required=True, rejected=True, unique=True)
    created_at = DatetimeField(default=now, required=True, rejected=True)
    updated_at = DatetimeField(default=now, required=True, rejected=True)
    expires_at = DatetimeField(default=lambda: Token.calculate_expires_at())
    description = StringField(default="")
    user_id: ReferenceField[User] = ReferenceField(
        reference_model=User,
        required=True,
        rejected=True,
        restricted=True,
        on_destroy=OnDestroy.CASCADE
    )
    auto_prolonged = BoolField(default=True)

    def touch(self):
        self.updated_at = now()

    async def user(self) -> Optional[User]:
        return await User.get(self.user_id)

    def is_expired(self) -> bool:
        return now() > self.expires_at

    @classmethod
    def calculate_expires_at(cls) -> datetime:
        return now() + cls.DEFAULT_TTL

    async def auto_prolong(self):
        if not self.auto_prolonged:
            return
        ttl = self.expires_at - now()
        if ttl < timedelta(days=7):
            self.expires_at = self.calculate_expires_at()
            await self.save()
            ctx.log.debug(f"token {self.token} auto-prolonged")

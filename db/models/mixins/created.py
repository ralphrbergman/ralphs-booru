from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

class CreatedMixin:
    created: Mapped[datetime] = mapped_column(default = func.now())

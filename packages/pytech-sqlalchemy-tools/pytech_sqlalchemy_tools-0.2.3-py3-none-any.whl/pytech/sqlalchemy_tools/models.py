from sqlalchemy.orm import MappedAsDataclass, DeclarativeBase

__all__ = [
    "BaseSqlModel",
]


class BaseSqlModel(MappedAsDataclass, DeclarativeBase):
    """subclasses will be converted to dataclasses"""
    pass

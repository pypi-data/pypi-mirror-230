"""
Module implementing the sqlmodel orm part of the user table
"""
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

import pandas as pd
from sqlmodel import col
from sqlmodel import Field
from sqlmodel import Relationship
from sqlmodel import select
from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel.sql.expression import SelectOfScalar

from core_devoops.db_insertion import create_or_update
from core_devoops.db_insertion import Insertor
from core_devoops.permissions import Permission
from core_devoops.read_write import load_json_file


if TYPE_CHECKING:
    from core_devoops.app_rights import AppRight


class AppUser(SQLModel, table=True):  # type: ignore
    """
    Simple user class: an id associate to a user with a password
    """
    __tablename__ = 'app_user'
    id: Optional[int] = Field(default=None, primary_key=True)
    user: str = Field(index=True)
    password: str
    permission: Permission = Field(default=Permission.ADMIN)
    client: Optional[str] = Field(default=None)
    rights: List['AppRight'] = Relationship(back_populates='user')


def user_convertor(df: pd.DataFrame) -> List[Dict]:
    """
    Dummy user convertor
    """
    return []


def user_reductor(in_db_row: AppUser,  db_row: AppUser) -> AppUser:
    """
    Update an existing in_db_row with new information coming from db_row
    """
    in_db_row.user = db_row.user
    in_db_row.password = db_row.password
    return in_db_row


def user_selector(db_row: AppUser) -> SelectOfScalar:
    """
    Criteria on which to decide whether creating a new row or updating an existing one in db
    """
    return select(AppUser).where(col(AppUser.user) == db_row.user,
                                 col(AppUser.permission) == db_row.permission,
                                 col(AppUser.client) == db_row.client)


USER_INSERTOR = Insertor(convertor=user_convertor, selector=user_selector,
                         reductor=user_reductor, db_schema=AppUser)


def upsert_app_users(file_path: Path, session: Session) -> None:
    """
    Upsert db users with a list of users provided in the file_path (json format)
    """
    for user in load_json_file(file_path):
        session.add(create_or_update(session, user, USER_INSERTOR))
        session.commit()

"""Separated dependencies module. This is used instead of adding to __main__.py to prevent cyclic imports."""
from typing import TypeAlias

from sqlmodel import create_engine

engine = create_engine('sqlite://', echo=True)

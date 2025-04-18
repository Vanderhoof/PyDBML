import os

from . import _classes
from .parser import PyDBML
from .database import Database

load = PyDBML.parse_file
loads = PyDBML.parse

def dump(db: Database, fp: str | os.PathLike):
    with open(fp, 'w') as f:
        f.write(db.dbml)

def dumps(db: Database) -> str:
    return db.dbml
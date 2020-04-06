import sqlalchemy

from .common import database, sqlalchemy_metadata

# register models with sqlalchemy_metadata by importing
from .session import Session


def create_db():
    """Create the database using sqlalchemy.
    """
    engine = sqlalchemy.create_engine(str(database.url))
    sqlalchemy_metadata.create_all(engine)


if __name__ == "__main__":
    create_db()

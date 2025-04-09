"""Set up database."""

from sqlalchemy import Engine, create_engine

from dao.models import Base


def setup(database_path: str) -> Engine:
    """Set up database."""
    engine = create_engine(database_path, isolation_level="SERIALIZABLE")
    Base.metadata.create_all(engine)
    return engine


if __name__ == "__main__":
    setup("sqlite:///my_db.db")

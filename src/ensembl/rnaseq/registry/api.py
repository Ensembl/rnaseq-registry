from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from database_schema import dataset, sample, organism
import argschema


Base = declarative_base()


class RnaseqRegistry:
    """Interface for the RNA-Seq Registry."""

    def __init__(self, db: str) -> None:
        self.db = db


class InputSchema(argschema.ArgSchema):
    """Input arguments expected by the entry point of this module."""

    dbname = argschema.fields.String(required=True, metadata={"description": "Database name for sqllite"})


def main():
    """Main script entry-point."""
    mod = argschema.ArgSchemaParser(schema_type=InputSchema)
    dbname = mod.args["dbname"]
    engine = create_engine(f"sqlite:///{dbname}", echo=True)

    # Create tables
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
import argschema
from ensembl.rnaseq.registry.database_schema import dataset, organism, sample



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
    dataset()
    organism()
    sample()

    # Create tables
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()

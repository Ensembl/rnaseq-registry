# See the NOTICE file distributed with this work for additional information
# regarding copyright ownership.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
import argschema

"""RNA-Seq registry API module."""

__all__ = [
    "RnaseqRegistry",
]


class RnaseqRegistry:
    """Interface for the RNA-Seq Registry."""

    def __init__(self, db: str) -> None:
        self.db = db
        self.engine = create_engine(f"sqlite:///{db}", echo=True)

    def create_load(self):
        metadata = MetaData()

        dataset = Table(
            "dataset", metadata, Column("name", String, primary_key=True), Column("organism", String)
        )

        sample = Table(
            "sample", metadata, Column("SRA accession", String, primary_key=True), Column("dataset", String)
        )

        organism = Table(
            "organism",
            metadata,
            Column("organism_abbrv", String, primary_key=True),
            Column("component", String),
        )

        metadata.create_all(self.engine)


class InputSchema(argschema.ArgSchema):
    """Input arguments expected by the entry point of this module."""

    dbname = argschema.fields.String(required=True, metadata={"descriptions": "Database name for sqllite"})


def main():
    """Main script entry-point."""
    mod = argschema.ArgSchemaParser(schema_type=InputSchema)
    registry = RnaseqRegistry(mod.args["dbname"])
    registry.create_load()


if __name__ == "__main__":
    main()

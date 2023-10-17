#!/usr/bin/env python
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
"""Generates one JSON file per metadata type inside `manifest`, including the manifest itself.

Can be imported as a module and called as a script as well, with the same parameters and expected outcome.
"""

from os import PathLike
from pathlib import Path

import argparse
from sqlalchemy import create_engine

from ensembl.rnaseq.registry.api import RnaseqRegistry


def get_engine(dbfile: PathLike):
    """Returns an SQLalchemy engine.

    Args:
        dbfile (PathLike): Path to the SQLite file to use as registry.
    """
    db_url = f"sqlite:///{dbfile}"
    return create_engine(db_url, echo=True)


def create_db(args):
    """Actions for the subcommand "create"."""
    db = args.database

    if Path(db).is_file():
        if not args.force:
            print(f"Database already exists: {db}")
            return
        Path(db).unlink()
        print(f"Recreate the database {db} from scratch")
    else:
        print(f"Create the new database {db}")

    engine = get_engine(args.database)
    # SQLAlchemy create_db here

    reg = RnaseqRegistry(engine)
    reg.create_db()


def main() -> None:
    """Main script entry-point."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="Subcommands")

    # Create submenu
    create_parser = subparsers.add_parser("create")
    create_parser.set_defaults(func=create_db)
    create_parser.add_argument("database", help="SQLite3 RNA-Seq registry database")
    create_parser.add_argument("--force", action="store_true", help="Replace if the db already exists")

    # Parse args and start the submenu action
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.print_help()


if __name__ == "__main__":
    main()

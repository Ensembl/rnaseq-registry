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

import logging
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
    return create_engine(db_url)


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


def change_component(args):
    """Actions for the subcommand "component"."""
    engine = get_engine(args.database)
    reg = RnaseqRegistry(engine)

    if args.add:
        reg.add_component(args.add)

    elif args.get:
        component = reg.get_component(args.get)
        print(component)

    elif args.remove:
        reg.remove_component(args.remove)

    elif args.list:
        components = reg.list_components()
        for component in components:
            print(component)


def change_organism(args):
    """Actions for the subcommand "organism"."""
    engine = get_engine(args.database)
    reg = RnaseqRegistry(engine)

    if args.add:
        if not args.component:
            print("Need a component for the organism")
            raise ValueError("Need a component")
        reg.add_organism(args.add, args.component)

    elif args.get:
        organism = reg.get_organism(args.get)
        print(organism)

    elif args.remove:
        reg.remove_organism(args.remove)

    elif args.list:
        organisms = reg.list_organisms(args.component)
        for organism in organisms:
            print(organism)

    elif args.load:
        loaded_count = reg.load_organisms(args.load)
        print(f"Loaded {loaded_count} organisms")


def change_dataset(args):
    """Actions for the subcommand "dataset"."""
    engine = get_engine(args.database)
    reg = RnaseqRegistry(engine)

    if args.load:
        loaded_count = reg.load_datasets(args.load, release=args.release, replace=args.replace, ignore=args.ignore)
        print(f"Loaded {loaded_count} datasets")
    else:
        datasets = reg.list_datasets(
            component=args.component, organism=args.organism, dataset_name=args.dataset, release=args.release
        )

        if args.list:
            print(f"{len(datasets)} datasets selected")
            for dataset in datasets:
                print(dataset)

        if args.remove:
            for dataset in datasets:
                reg.remove_dataset(dataset)

        if args.dump_file:
            reg.dump_datasets(Path(args.dump_file), datasets)


def do_nothing(args) -> None:
    pass


def main() -> None:
    """Main script entry-point."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="Subcommands")
    parser.set_defaults(func=do_nothing)

    # Create submenu
    create_parser = subparsers.add_parser("create")
    create_parser.set_defaults(func=create_db)
    create_parser.add_argument("database", help="SQLite3 RNA-Seq registry database")
    create_parser.add_argument("--force", action="store_true", help="Replace if the db already exists")

    # Component submenu
    component_parser = subparsers.add_parser("component")
    component_parser.set_defaults(func=change_component)
    component_parser.add_argument("database", help="SQLite3 RNA-Seq registry database")
    component_parser.add_argument("--add", help="Name of a component to add")
    component_parser.add_argument("--remove", help="Name of a component to remove")
    component_parser.add_argument("--get", help="Name of a component to show")
    component_parser.add_argument("--list", action="store_true", help="Print the list of components")

    # Organism submenu
    organism_parser = subparsers.add_parser("organism")
    organism_parser.set_defaults(func=change_organism)
    organism_parser.add_argument("database", help="SQLite3 RNA-Seq registry database")
    organism_parser.add_argument("--component", help="Name of a component")
    organism_parser.add_argument("--add", help="Name of a organism to add")
    organism_parser.add_argument("--remove", help="Name of a organism to remove")
    organism_parser.add_argument("--get", help="Name of a organism to show")
    organism_parser.add_argument("--list", action="store_true", help="Print the list of organisms")
    organism_parser.add_argument(
        "--load", help="Load organism abbrevs and components from a tab file (component\torganism_abbrev)"
    )

    # Dataset submenu
    dataset_parser = subparsers.add_parser("dataset")
    dataset_parser.set_defaults(func=change_dataset)
    dataset_parser.add_argument("database", help="SQLite3 RNA-Seq registry database")
    dataset_parser.add_argument("--load", help="Dataset data to load in json format")
    dataset_parser.add_argument("--component", help="Filter with a component")
    dataset_parser.add_argument("--organism", help="Filter with an organism")
    dataset_parser.add_argument("--dataset", help="Filter with a dataset name")
    dataset_parser.add_argument("--release", help="Filter with a release (or use this value to load as default)")
    dataset_parser.add_argument("--replace", action="store_true", help="Replace duplicate datasets when loading")
    dataset_parser.add_argument("--ignore", action="store_true", help="Ignore duplicate datasets when loading and load the rest")
    dataset_parser.add_argument("--remove", action="store_true", help="Remove the selected datasets")
    dataset_parser.add_argument("--list", action="store_true", help="Show the selected datasets")
    dataset_parser.add_argument("--dump_file", help="Dump the selected datasets to this file")

    # Parse args and start the submenu action
    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()

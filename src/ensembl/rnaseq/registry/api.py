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
"""RNA-Seq registry API module."""

import json
from typing import List, Optional
from pathlib import Path
from os import PathLike

from jsonschema import validate
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, joinedload

from ensembl.rnaseq.registry.database_schema import Base, Component, Organism, Dataset, Sample, Accession

__all__ = [
    "RnaseqRegistry",
]

cur_dir = Path(__file__).parent
_RNASEQ_SCHEMA_PATH = Path(cur_dir, "schemas/brc4_rnaseq_schema.json")


class RnaseqRegistry:
    """Interface for the RNA-Seq Registry."""

    def __init__(self, engine: Engine) -> None:
        """Create the Registry interface with the provided engine.

        Args:
            engine: Predefined engine to use.
        """
        self.engine = engine
        with Session(engine) as session:
            self.session = session

    def create_db(self) -> None:
        """Populate a database with the SQLalchemy-defined schema."""
        Base.metadata.create_all(bind=self.engine)

    def add_component(self, name: str) -> Component:
        """Insert a new component.

        Args:
            name: name of the component
        """
        new_comp = Component(name=name)
        self.session.add(new_comp)
        self.session.commit()
        return new_comp

    def get_component(self, name: str, create: bool = False) -> Component:
        """Retrieve a component.

        Args:
        name : Name of the component.
        create : Flag indicating whether to create the component if not found.
        """
        stmt = select(Component).where(Component.name == name)
        component = self.session.scalars(stmt).first()

        if not component:
            if create:
                component = self.add_component(name)
            else:
                raise ValueError(f"No component named {name}")
        return component

    def remove_component(self, name: str) -> None:
        """Delete a component.

        Args:
        name : Name of the component to remove.
        """
        component = self.get_component(name)
        self.session.delete(component)
        self.session.commit()

    def list_components(self) -> List[Component]:
        """List all components."""

        stmt = select(Component).order_by(Component.name)
        components = list(self.session.scalars(stmt).all())
        return components

    def add_organism(self, name: str, component_name: str) -> Organism:
        """Insert a new organism.

        Args:
        name : Name of the organism to add.
        component_name : Name of the component of the organism
        """
        try:
            component = self.get_component(component_name)
        except ValueError as err:
            raise ValueError("Cannot add organism for unknown component") from err

        new_org = Organism(abbrev=name, component=component)
        self.session.add(new_org)
        self.session.commit()
        return new_org

    def get_organism(self, name: str) -> Organism:
        """Retrieve an organism.

        Args:
        name : Name of the organism.
        """
        stmt = select(Organism).options(joinedload(Organism.component)).where(Organism.abbrev == name)

        organism = self.session.scalars(stmt).first()

        if not organism:
            raise ValueError(f"No organism named {name}")
        return organism

    def remove_organism(self, name: str) -> None:
        """Delete an organism.

        Args:
        name : Name of the organism to remove.
        """
        organism = self.get_organism(name)
        self.session.delete(organism)
        self.session.commit()

    def list_organisms(self, component: Optional[str] = None) -> List[Organism]:
        """List all organisms.

        Args:
        component: filter by component.
        """

        stmt = select(Organism).join(Component).order_by(Component.name, Organism.abbrev)
        if component:
            stmt = stmt.where(Component.name == component)
        organisms = list(self.session.scalars(stmt).all())
        return organisms

    def load_organisms(self, input_file: PathLike) -> int:
        """Import organisms and their components from a file.

        Args:
        input_file : Path to the input tab-delimited file.
        """
        # First, get the existing components and abbrevs
        components = {comp.name: comp for comp in self.list_components()}
        abbrevs = {org.abbrev for comp in components.values() for org in comp.organisms}

        # Next, get the list of new components and abbrevs, minus the known ones
        new_orgs_data = []
        loaded_count = 0
        with Path(input_file).open("r") as in_data:
            for line in in_data:
                line = line.strip()
                if line == "":
                    continue
                parts = line.split("\t")
                if len(parts) != 2:
                    raise ValueError(f"Organism line requires 2 values (got {parts})")
                (component_name, organism_abbrev) = parts

                # On the fly, create the new components
                if component_name not in components:
                    components[component_name] = self.add_component(component_name)

                if organism_abbrev in abbrevs:
                    continue
                abbrevs.add(organism_abbrev)

                new_orgs_data.append({"name": organism_abbrev, "component": component_name})

        # Now that we've created all the components, add the organisms attached to them
        orgs_to_add = []
        for new_org_data in new_orgs_data:
            org_component = new_org_data["component"]
            new_org = Organism(abbrev=new_org_data["name"], component=components[org_component])
            orgs_to_add.append(new_org)

            loaded_count += 1

        self.session.add_all(orgs_to_add)
        self.session.commit()

        return loaded_count

    def load_datasets(self, input_file: PathLike) -> int:
        """Import datasets from a json file.

        Args:
        input_file : Path to the input json file.
        """
        # Validate the json file
        json_schema_file = _RNASEQ_SCHEMA_PATH
        with open(input_file) as input_fh:
            json_data = json.load(input_fh)
        with open(json_schema_file) as schema_fh:
            schema = json.load(schema_fh)
        validate(instance=json_data, schema=schema)

        # Load the datasets
        abbrevs = {org.abbrev: org for org in self.list_organisms()}
        new_datasets_list: List = []
        loaded_count = 0
        for dataset in json_data:
            organism_name = dataset["species"]
            if not organism_name in abbrevs:
                print(f"Organism '{organism_name}' is not in the registry")
                continue
            samples = []
            for run in dataset["runs"]:
                accessions = [Accession(sra_id=acc) for acc in run["accessions"]]
                samples.append(Sample(name=run["name"], accessions=accessions))
            new_dataset = Dataset(
                name=dataset["name"], organism_id=abbrevs[organism_name].id, samples=samples
            )
            new_datasets_list.append(new_dataset)
            loaded_count += 1

        self.session.add_all(new_datasets_list)
        self.session.commit()

        return loaded_count

    def get_dataset(self, organism_name: str, dataset_name: str) -> Dataset:
        """Retrieve a dataset for a given organism.

        Args:
        dataset_name : Name of the dataset.
        organism_name : Organism abbrev associated with the dataset.
        """
        stmt = (
            select(Dataset)
            .join(Organism)
            .options(
                joinedload(Dataset.samples),
            )
            .where(Dataset.name == dataset_name)
            .where(Organism.abbrev == organism_name)
        )
        dataset = self.session.scalars(stmt).first()
        if not dataset:
            raise ValueError(f"No dataset named {dataset_name} for {organism_name}")
        return dataset

    def remove_dataset(self, dataset: Dataset) -> None:
        """Delete a dataset."""
        self.session.delete(dataset)
        self.session.commit()

    def list_datasets(self, component: str = "", organism: str = "", dataset_name: str = "") -> List[Dataset]:
        """Get all datasets with the provided filters."""

        stmt = (
            select(Dataset)
            .join(Organism)
            .join(Component)
            .options(
                joinedload(Dataset.samples),
                joinedload(Dataset.organism),
            )
        )
        if component:
            stmt = stmt.where(Component.name == component)
        if organism:
            stmt = stmt.where(Organism.abbrev == organism)
        if dataset_name:
            stmt = stmt.where(Dataset.name == dataset_name)

        datasets = self.session.scalars(stmt).unique()
        return list(datasets)

    def dump_datasets(self, dump_path: Path, datasets: List[Dataset]) -> None:
        """Write all datasets in one json file."""
        json_data = [dataset.to_json_struct() for dataset in datasets]
        with dump_path.open("w") as out_json:
            out_json.write(json.dumps(json_data, indent=2, sort_keys=True))

    def dump_datasets_folder(self, dump_path: Path, datasets: List[Dataset]) -> None:
        """Print the datasets to files in a folder structure: build_xx/component/orgAbbrev_dataset_name.json

        Args:
        dump_path: Path to a folder to dump the data.
        datasets: List of datasets to dump.

        """
        for dataset in datasets:
            folder_path: Path = dump_path / f"build_{dataset.release}" / dataset.organism.component.name
            folder_path.mkdir(parents=True, exist_ok=True)
            file_path = folder_path / f"{dataset.organism.abbrev}_{dataset.name}.json"
            with file_path.open("w") as out_json:
                out_json.write(json.dumps(dataset.to_json_struct(), indent=2, sort_keys=True))

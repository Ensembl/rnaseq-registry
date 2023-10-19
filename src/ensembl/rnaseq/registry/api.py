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

from typing import List

from sqlalchemy import Engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from ensembl.rnaseq.registry.database_schema import Base, Component, Organism

__all__ = [
    "RnaseqRegistry",
]


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
        """Insert a new component."""
        new_comp = Component(name=name)
        self.session.add(new_comp)
        self.session.commit()
        return new_comp

    def get_component(self, name: str) -> Component:
        """Retrieve a component."""
        stmt = select(Component).where(Component.name == name)
        component = self.session.scalars(stmt).first()

        if not component:
            raise ValueError(f"No component named {name}")
        return component

    def remove_component(self, name: str) -> None:
        """Delete a component."""
        component = self.get_component(name)
        self.session.delete(component)
        self.session.commit()

    def list_components(self) -> List[Component]:
        """List all components."""

        stmt = select(Component)
        components = list(self.session.scalars(stmt).unique().all())
        return components

    def add_organism(self, name: str, component_name: str) -> Organism:
        """Insert a new organism."""
        component = self.get_component(component_name)

        new_org = Organism(organism_abbrev=name, component=component)
        self.session.add(new_org)
        self.session.commit()
        return new_org

    def get_organism(self, name: str) -> Organism:
        """Retrieve an organism."""
        stmt = select(Organism).options(joinedload(Organism.component)).where(Organism.organism_abbrev == name)

        organism = self.session.scalars(stmt).first()

        if not organism:
            raise ValueError(f"No organism named {name}")
        return organism

    def remove_organism(self, name: str) -> None:
        """Delete an organism."""
        organism = self.get_organism(name)
        self.session.delete(organism)
        self.session.commit()

    def list_organisms(self) -> List[Organism]:
        """List all organisms."""

        stmt = select(Organism)
        organisms = list(self.session.scalars(stmt).unique().all())
        return organisms

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

from ensembl.rnaseq.registry.database_schema import Base, Component

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

    def create_db(self) -> None:
        """Populate a database with the SQLalchemy-defined schema."""
        Base.metadata.create_all(bind=self.engine)

    def add_component(self, name: str) -> Component:
        """Insert a new component."""
        new_comp = Component(name=name)
        with Session(self.engine) as session:
            session.add(new_comp)
            session.commit()
        return new_comp

    def get_component(self, name: str) -> Component:
        """Retrieve a component."""
        stmt = select(Component).where(Component.name == name)
        with Session(self.engine) as session:
            component = session.scalars(stmt).first()

        if not component:
            raise ValueError(f"No component named {name}")
        return component

    def remove_component(self, name: str) -> None:
        """Delete a component."""
        component = self.get_component(name)
        with Session(self.engine) as session:
            session.delete(component)
            session.commit()

    def list_components(self) -> List[Component]:
        """Delete a component."""

        stmt = select(Component)
        with Session(self.engine) as session:
            components = list(session.scalars(stmt))
        return components

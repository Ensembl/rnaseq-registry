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

"""Schema in SQLAlchemy to describe RNA-Seq datasets."""

from typing import List
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm import mapped_column, relationship


__all__ = ["Base", "Dataset", "Sample", "Organism"]


class Base(DeclarativeBase):
    """Import declarative Base."""


class Dataset(Base):
    """Create a table dataset"""

    __tablename__ = "dataset"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    organism_id: Mapped[int] = mapped_column(ForeignKey("organism.id"))
    organism: Mapped["Organism"] = relationship(back_populates="datasets")
    UniqueConstraint(name, organism_id)

    # Relationships
    samples: Mapped[List["Sample"]] = relationship(back_populates="dataset", cascade="all")

    def __repr__(self) -> str:
        return f"dataset(name={self.name!r}, samples={self.samples!r})"


class Sample(Base):
    """Create a table sample"""

    __tablename__ = "sample"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("dataset.id"))

    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="samples")
    accessions: Mapped[List["Accession"]] = relationship(back_populates="sample", cascade="all")

    def __repr__(self) -> str:
        return f"sample(accessions={self.accessions!r}, dataset={self.dataset!r})"


class Accession(Base):
    """Create a table for accession"""

    __tablename__ = "accession"
    id: Mapped[int] = mapped_column(primary_key=True)
    sra_id: Mapped[str] = mapped_column(String)
    sample_id: Mapped[int] = mapped_column(ForeignKey("sample.id"))

    # Relationships
    sample: Mapped[Sample] = relationship(back_populates="accessions", cascade="all")

    def __repr__(self) -> str:
        return f"accession(sra_id={self.sra_id!r}, samples={self.sample!r})"


class Organism(Base):
    """Create a table organism"""

    __tablename__ = "organism"
    id: Mapped[int] = mapped_column(primary_key=True)
    abbrev: Mapped[str] = mapped_column(String, unique=True)
    component_id: Mapped[int] = mapped_column(ForeignKey("component.id"))
    component: Mapped["Component"] = relationship(back_populates="organisms")
    datasets: Mapped["Dataset"] = relationship(back_populates="organism")

    def __repr__(self) -> str:
        return f"organism(abbrv={self.abbrev!r}, component={self.component.name!r})"


class Component(Base):
    """Create a table component"""

    __tablename__ = "component"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)

    # Relationships
    organisms: Mapped[List[Organism]] = relationship(back_populates="component", cascade="all")

    def __repr__(self) -> str:
        return f"component(name={self.name!r}, organisms={len(self.organisms)})"

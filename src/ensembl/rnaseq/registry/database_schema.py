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
from sqlalchemy import String, ForeignKey
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
    organism: Mapped[str] = mapped_column(ForeignKey("organism.id"))

    # Relationships
    samples: Mapped[List["Sample"]] = relationship(back_populates="dataset", cascade="all", lazy="joined")

    def __repr__(self) -> str:
        return f"dataset(name={self.name!r}, organism={self.organism!r})"


class Sample(Base):
    """Create a table sample"""

    __tablename__ = "sample"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    SRA_accession: Mapped[str] = mapped_column(ForeignKey("accession.sra_id"), nullable=False)
    dataset_id: Mapped[str] = mapped_column(ForeignKey("dataset.id"))
     
    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="samples", lazy="joined")
    accessions: Mapped["Accession"] = relationship(back_populates="samples", lazy="joined")

    def __repr__(self) -> str:
        return f"sample(SRA_accession={self.SRA_accession!r}, dataset={self.dataset!r})"


class Organism(Base):
    """Create a table organism"""

    __tablename__ = "organism"
    id: Mapped[int] = mapped_column(primary_key=True)
    organism_abbrev: Mapped[str] = mapped_column(String, unique=True)
    component_id: Mapped[str] = mapped_column(ForeignKey("component.id"))
    component: Mapped["Component"] = relationship(back_populates="organisms", lazy="joined")

    def __repr__(self) -> str:
        return f"organism(organism_abbrv={self.organism_abbrev!r}, component={self.component.name!r})"


class Component(Base):
    """Create a table component"""

    __tablename__ = "component"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)

    # Relationships
    organisms: Mapped[List[Organism]] = relationship(back_populates="component", cascade="all", lazy="joined")

    def __repr__(self) -> str:
        return f"component(name={self.name!r}, organisms={len(self.organisms)})"

class Accession(Base):
    """Create a table for accession"""

    __tablename__ = "accession"
    id: Mapped[int] = mapped_column(primary_key=True)
    sra_id: Mapped[str] = mapped_column(unique=True)

    # Relationships
    samples: Mapped[List[Sample]] = relationship(back_populates="accessions", cascade="all", lazy="joined")

    def __repr__(self) -> str:
        return f"accession(sra_id={self.sra_id!r}, samples={self.samples.name!r})"
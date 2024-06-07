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

from typing import Dict, List
from sqlalchemy import Boolean, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm import mapped_column, relationship


__all__ = ["Base", "Component", "Organism", "Dataset", "Sample", "Accession"]


class Base(DeclarativeBase):
    """Import declarative Base."""


class Component(Base):
    """Create a table component"""

    __tablename__ = "component"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)

    # Relationships
    organisms: Mapped[List["Organism"]] = relationship(back_populates="component", cascade="all")

    def __repr__(self) -> str:
        return f"component(name={self.name!r}, organisms={len(self.organisms)})"

    def __str__(self) -> str:
        datasets_count = sum(len(org.datasets) for org in self.organisms)
        line = [self.name, f"({len(self.organisms)} organisms)", f"({datasets_count} datasets)"]
        return "\t".join(line)


class Organism(Base):
    """Create a table organism"""

    __tablename__ = "organism"
    id: Mapped[int] = mapped_column(primary_key=True)
    abbrev: Mapped[str] = mapped_column(String, unique=True)
    component_id: Mapped[int] = mapped_column(ForeignKey("component.id"))
    component: Mapped["Component"] = relationship(back_populates="organisms")
    datasets: Mapped[List["Dataset"]] = relationship(back_populates="organism")

    def __repr__(self) -> str:
        return f"organism(abbrev={self.abbrev!r}, component={self.component.name!r})"

    def __str__(self) -> str:
        n_datasets = len(self.datasets)
        line = [self.component.name, self.abbrev, f"({n_datasets} datasets)"]
        return "\t".join(line)


class Dataset(Base):
    """Create a table dataset"""

    __tablename__ = "dataset"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    release: Mapped[int] = mapped_column(Integer, default=0)
    retired: Mapped[int] = mapped_column(Integer, default=0)
    latest: Mapped[bool] = mapped_column(Boolean, default=True)

    organism_id: Mapped[int] = mapped_column(ForeignKey("organism.id"))
    organism: Mapped["Organism"] = relationship(back_populates="datasets")
    UniqueConstraint(name, organism_id, latest, retired)

    # Relationships
    samples: Mapped[List["Sample"]] = relationship(back_populates="dataset", cascade="all")

    def __repr__(self) -> str:
        return (
            f"dataset(from={self.organism!r}, name={self.name!r}, "
            f"samples={len(self.samples)}, retired={self.retired}, latest={self.latest})"
        )

    def __str__(self) -> str:
        n_samples = len(self.samples)
        line = [str(self.release)]
        if not self.latest:
            line += [f"retired {self.retired}"]
        if self.organism:
            line += [self.organism.component.name, self.organism.abbrev]
        line += [self.name, f"({n_samples} samples)"]
        return "\t".join(line)

    def to_json_struct(self) -> Dict:
        """Represent the data ready to be dumped as json."""
        dataset_struct: Dict = {
            "component": self.organism.component.name,
            "species": self.organism.abbrev,
            "name": self.name,
            "release": self.release,
        }
        runs: List[Dict] = []
        for sample in self.samples:
            accessions = [acc.sra_id for acc in sample.accessions]
            runs.append({"name": sample.name, "accessions": accessions})
        dataset_struct["runs"] = runs
        return dataset_struct


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

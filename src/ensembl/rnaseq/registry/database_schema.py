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
from sqlalchemy import String, create_engine
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

class Base(DeclarativeBase):
    pass

class Dataset(Base):
    """Create a table dataset
    """
    __tablename__= "dataset"
    name: Mapped[str] = mapped_column(primary_key=True)
    organism: Mapped[str] = mapped_column(String)
    #sample = relationship("Sample")
    
    def __repr__(self) -> str:
        return f"dataset(name={self.name!r}, organism={self.organism!r})"

class Sample(Base):
    """Create a table sample
    """
    __tablename__= "sample"
    SRA_accession: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    dataset: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f"sample(SRA_accession={self.SRA_accession!r}, dataset={self.dataset!r})"

class Organism(Base):
    """Create a table organism
    """
    __tablename__= "organism"
    organism_abbrv: Mapped[str] = mapped_column(primary_key=True)
    component: Mapped[str] = mapped_column(String)

    def __repr__(self) -> str:
        return f"organism(organism_abbrv={self.organism_abbrv!r}, component={self.component!r})"

class create_db():
    def __init__(self,dbname)-> None:
        """create database tables if they do not exist already."""
        engine = create_engine(f"sqlite:///{dbname}", echo=True,  future=True)
        Base.metadata.create_all(bind=engine)
     
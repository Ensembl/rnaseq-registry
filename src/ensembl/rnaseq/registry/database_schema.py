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

from typing import List
from typing import Optional
from sqlalchemy.orm import Mapped , mapped_column, relationship, DeclarativeBase
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
import argschema


class Base(DeclarativeBase):
    pass
    
class dataset(Base):
    __tablename__= "dataset"

    name: Mapped[str] = mapped_column(primary_key=True)
    organism: Mapped[str] = mapped_column(String)
    
    
    def __repr__(self) -> str:
        return f"dataset(name={self.name!r}, organism={self.organism!r})"


class sample(Base):
    """Sample table class
    """
    __tablename__= "sample"

    SRA_accession: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    dataset: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f"sample(SRA_accession={self.SRA_accession!r}, dataset={self.dataset!r})"

class organism(Base):
    """Organisms table class    
    """
    __tablename__= "organism"

    organism_abbrv: Mapped[str] = mapped_column(primary_key=True)
    component: Mapped[str] = mapped_column(String)





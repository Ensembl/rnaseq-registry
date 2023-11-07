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
"""
Unit tests for the RNA-Seq registry API.
"""
from pathlib import Path

import pytest
from sqlalchemy import inspect as sql_inspect, create_engine
from sqlalchemy.engine import Engine

from ensembl.rnaseq.registry.api import RnaseqRegistry


_CUR_DIR = Path(__file__).parent


class Test_RNASeqRegistry:
    """Tests for the RNASeqRegistry module."""

    @pytest.fixture
    def orgs_file(self):
        """Location of the organism file."""
        return Path(_CUR_DIR, "data", "orgs_file.tab")

    @pytest.fixture
    def ok_dataset_file(self):
        """Location of the ok dataset file."""
        return Path(_CUR_DIR, "data", "ok_input_dataset.json")

    @pytest.fixture(scope="function")
    def engine(self) -> Engine:
        """Generate the Engine. Use an in-memory DB."""
        test_engine = create_engine("sqlite:///:memory:")
        return test_engine

    def test_init(self, engine: Engine) -> None:
        """Check the RNASeqRegistry object can be created."""
        reg = RnaseqRegistry(engine)
        assert isinstance(reg, RnaseqRegistry)

    def test_create_tables(self, engine: Engine) -> None:
        """Test creating tables from scratch."""

        reg = RnaseqRegistry(engine)
        reg.create_db()

        # Check if the tables are created in the test database file
        insp = sql_inspect(reg.engine)
        assert insp.has_table("dataset")
        assert insp.has_table("sample")
        assert insp.has_table("organism")
        assert insp.has_table("component")
        assert insp.has_table("accession")

    def test_add_get_component(self, engine: Engine) -> None:
        """Test adding a new component."""

        reg = RnaseqRegistry(engine)
        reg.create_db()

        reg.add_component("TestDB")
        reg.get_component("TestDB")
        assert reg

    def test_remove_component(self, engine: Engine) -> None:
        """Test removing a component."""

        db_name = "TestDB"
        reg = RnaseqRegistry(engine)
        reg.create_db()
        reg.add_component(db_name)
        assert reg.get_component(db_name)
        reg.remove_component(db_name)

    def test_add_get_organism(self, engine: Engine) -> None:
        """Test adding a new organism."""

        reg = RnaseqRegistry(engine)
        reg.create_db()

        org = "speciesA"
        comp = "TestDB"
        reg.add_component(comp)
        reg.add_organism(org, comp)
        organism = reg.get_organism(org)
        assert organism

    def test_load_organisms(self, engine: Engine, orgs_file: Path) -> None:
        """Test adding organisms from a file."""

        reg = RnaseqRegistry(engine)
        reg.create_db()

        reg.load_organisms(orgs_file)

        species_a = reg.get_organism("speciesA")
        assert species_a
        test_component = reg.get_component("TestDB")
        assert test_component

        # Check counts
        num_components = len(reg.list_components())
        num_organisms = len(reg.list_organisms())
        assert num_components == 2
        assert num_organisms == 3

        # Try to load again, should not fail, and not load anything new
        reg.load_organisms(orgs_file)
        num_components_after = len(reg.list_components())
        num_organisms_after = len(reg.list_organisms())
        assert num_components == num_components_after
        assert num_organisms == num_organisms_after

    def test_load_datasets(self, engine: Engine, orgs_file: Path, ok_dataset_file: Path) -> None:
        """Test adding datasets from a file."""

        reg = RnaseqRegistry(engine)
        reg.create_db()
        reg.load_organisms(orgs_file)
        reg.load_datasets(ok_dataset_file)

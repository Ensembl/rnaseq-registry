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
from contextlib import nullcontext as does_not_raise
from pathlib import Path
from typing import Callable, ContextManager, Optional

import pytest
from pytest import raises
from sqlalchemy import inspect as sql_inspect, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from ensembl.rnaseq.registry.api import RnaseqRegistry


_CUR_DIR = Path(__file__).parent


class Test_RNASeqRegistry:
    """Tests for the RNASeqRegistry module."""

    @pytest.fixture
    def shared_orgs_file(self, data_dir: Path):
        """Location of the organism file."""
        return data_dir / "shared_orgs_file.tab"

    @pytest.fixture
    def shared_dataset_file(self, data_dir: Path):
        """Location of the ok dataset file."""
        return data_dir / "shared_input_dataset.json"

    @pytest.fixture(scope="function")
    def engine(self) -> Engine:
        """Generate the Engine. Use an in-memory DB."""
        test_engine = create_engine("sqlite:///:memory:")
        return test_engine

    # Tests start here
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
        assert insp.has_table("component")
        assert insp.has_table("organism")
        assert insp.has_table("dataset")
        assert insp.has_table("sample")
        assert insp.has_table("accession")

    @pytest.mark.dependency(name="add_get_feature")
    @pytest.mark.parametrize(
        "added_component, get_component, expectation",
        [
            pytest.param("TestDB", "TestDB", does_not_raise(), id="Add/Get existing component"),
            pytest.param("TestDB", "LOREM_IPSUM_DB", raises(ValueError), id="Get non-existing component"),
        ],
    )
    def test_add_get_component(
        self, engine: Engine, added_component: str, get_component: str, expectation: ContextManager
    ) -> None:
        """Test adding a new component."""

        reg = RnaseqRegistry(engine)
        reg.create_db()

        with expectation:
            reg.add_component(added_component)
            reg.get_component(get_component)
            assert reg

    @pytest.mark.dependency(depends=["add_get_feature"])
    @pytest.mark.parametrize(
        "added_component, removed_component, expectation",
        [
            pytest.param("TestDB", "TestDB", does_not_raise(), id="Remove existing component"),
            pytest.param("TestDB", "LOREM_IPSUM_DB", raises(ValueError), id="Remove non-existing component"),
        ],
    )
    def test_remove_component(
        self, engine: Engine, added_component: str, removed_component: str, expectation: ContextManager
    ) -> None:
        """Test removing a component."""

        reg = RnaseqRegistry(engine)
        reg.create_db()
        reg.add_component(added_component)
        with expectation:
            reg.remove_component(removed_component)

    @pytest.mark.dependency(depends=["add_get_feature"])
    @pytest.mark.parametrize(
        "added_component, added_organism, get_organism, expectation",
        [
            pytest.param("TestDB", "SpeciesA", "SpeciesA", does_not_raise(), id="Add/get existing organism"),
            pytest.param(
                "TestDB",
                "SpeciesA",
                "LOREM_IPSUM_SPECIES",
                raises(ValueError),
                id="Get non-existing organism",
            ),
        ],
    )
    def test_add_get_organism(
        self,
        engine: Engine,
        added_component: str,
        added_organism: str,
        get_organism: str,
        expectation: ContextManager,
    ) -> None:
        """Test adding a new organism."""

        reg = RnaseqRegistry(engine)
        reg.create_db()

        reg.add_component(added_component)
        with expectation:
            reg.add_organism(added_organism, added_component)
            organism = reg.get_organism(get_organism)
            assert organism

    @pytest.mark.dependency(depends=["add_get_feature"])
    @pytest.mark.parametrize(
    "organism_file, removed_organism, expectation",
    [
        pytest.param("organisms_ok.tab", "SpeciesA", does_not_raise(), id="Remove existing organism"),
        pytest.param("organisms_ok.tab", "LOREM_IPSUM_A", raises(ValueError), id="Remove non-existing organism"),
    ],
    )
    def test_remove_organism(
        self,  data_dir: Path, engine: Engine, organism_file: Path, removed_organism: str, expectation: ContextManager) -> None:
        """Test removing an organism."""

        reg = RnaseqRegistry(engine)
        reg.create_db()
        reg.load_organisms(data_dir / organism_file)
        with expectation:
            reg.remove_organism(removed_organism)

    @pytest.mark.dependency(depends=["add_get_feature"])
    @pytest.mark.parametrize(
        "organism_file, component, organism, expectation",
        [
            pytest.param("organisms_ok.tab", "TestDB", "SpeciesA", does_not_raise(), id="Import organisms"),
        ],
    )
    def test_load_organisms(
        self,
        data_dir: Path,
        engine: Engine,
        organism_file: Path,
        component: str,
        organism: str,
        expectation: ContextManager,
    ) -> None:
        """Test adding organisms from a file."""

        reg = RnaseqRegistry(engine)
        reg.create_db()

        with expectation:
            reg.load_organisms(data_dir / organism_file)

        test_component = reg.get_component(component)
        assert test_component
        species_a = reg.get_organism(organism)
        assert species_a

        # Check counts
        num_components = len(reg.list_components())
        num_organisms = len(reg.list_organisms())
        assert num_components == 2
        assert num_organisms == 3

        # Try to load again, should not fail, and not load anything new
        reg.load_organisms(data_dir / organism_file)
        num_components_after = len(reg.list_components())
        num_organisms_after = len(reg.list_organisms())
        assert num_components == num_components_after
        assert num_organisms == num_organisms_after

    @pytest.mark.dependency(name="load_datasets")
    @pytest.mark.parametrize(
        "dataset_file, release, expectation",
        [
            pytest.param("shared_input_dataset.json", 10, does_not_raise(), id="OK dataset"),
            pytest.param("datasets_same_name_ok.json", 10, does_not_raise(), id="Load 2 datasets same name"),
            pytest.param(
                "datasets_same_name_same_org.json", 10, raises(IntegrityError), id="2 datasets same name"
            ),
        ],
    )
    def test_load_datasets(
        self,
        data_dir: Path,
        engine: Engine,
        shared_orgs_file: Path,
        dataset_file: Path,
        release: int,
        expectation: ContextManager,
    ) -> None:
        """Test adding datasets from a file."""

        reg = RnaseqRegistry(engine)
        reg.create_db()
        reg.load_organisms(shared_orgs_file)
        with expectation:
            assert reg.load_datasets(data_dir / dataset_file, release=release)

    @pytest.mark.dependency(name="list_datasets")
    @pytest.mark.parametrize(
        "datasets_file, component, organism, dataset, in_release, out_release, number_expected, expectation",
        [
            pytest.param(
                "datasets_several.json",
                None,
                None,
                None,
                10,
                None,
                3,
                does_not_raise(),
                id="Get all datasets",
            ),
            pytest.param(
                "datasets_several.json",
                None,
                None,
                None,
                10,
                10,
                3,
                does_not_raise(),
                id="Get all datasets for this release",
            ),
            pytest.param(
                "datasets_several.json",
                None,
                "speciesA",
                "dataset_A1",
                10,
                None,
                1,
                does_not_raise(),
                id="Get 1 exact dataset",
            ),
            pytest.param(
                "datasets_several.json",
                None,
                "speciesA",
                None,
                10,
                None,
                2,
                does_not_raise(),
                id="Datasets for 1 species",
            ),
            pytest.param(
                "datasets_several.json",
                "TestDB",
                None,
                None,
                10,
                None,
                3,
                does_not_raise(),
                id="Datasets for 1 component",
            ),
            pytest.param(
                "datasets_several.json",
                "NoDB",
                None,
                None,
                10,
                None,
                0,
                does_not_raise(),
                id="Unknown component",
            ),
            pytest.param(
                "datasets_several.json",
                "TestDB",
                "LOREM",
                None,
                10,
                None,
                0,
                does_not_raise(),
                id="Unknown species",
            ),
        ],
    )
    def test_list_datasets(
        self,
        data_dir: Path,
        engine: Engine,
        shared_orgs_file: Path,
        datasets_file: Path,
        component: str,
        organism: str,
        dataset: str,
        in_release: Optional[int],
        out_release: Optional[int],
        number_expected: int,
        expectation: ContextManager,
    ) -> None:
        """Test getting a filtered list of datasets."""

        reg = RnaseqRegistry(engine)
        reg.create_db()
        reg.load_organisms(shared_orgs_file)

        if in_release is not None:
            reg.load_datasets(data_dir / datasets_file, release=in_release)
        else:
            reg.load_datasets(data_dir / datasets_file)
        with expectation:
            datasets = reg.list_datasets(
                component=component, organism=organism, dataset_name=dataset, release=out_release
            )
            assert len(datasets) == number_expected

    @pytest.mark.dependency(name="remove_dataset", depends=["list_datasets"])
    @pytest.mark.parametrize(
        "organism_name, dataset_name, deleted_num",
        [
            pytest.param("speciesA", "dataset_A1", 1, id="OK dataset"),
            pytest.param("speciesA", "datasets_Lorem_Ipsum", 0, id="Dataset does not exist"),
            pytest.param("species_FOOBAR", "datasets_Lorem_Ipsum", 0, id="Organism does not exist"),
        ],
    )
    def test_remove_dataset(
        self,
        engine: Engine,
        shared_orgs_file: Path,
        shared_dataset_file: Path,
        organism_name: str,
        dataset_name: str,
        deleted_num: str,
    ) -> None:
        """Test adding a new component."""
        fake_release = 10

        reg = RnaseqRegistry(engine)
        reg.create_db()
        reg.load_organisms(shared_orgs_file)
        reg.load_datasets(shared_dataset_file, release=fake_release)
        datasets = reg.list_datasets(organism=organism_name, dataset_name=dataset_name)
        print(reg.list_datasets(organism_name))
        assert len(datasets) == deleted_num
        for dataset in datasets:
            reg.remove_dataset(dataset)
    
    @pytest.mark.dependency(depends=["list_datasets"])
    @pytest.mark.parametrize(
        "organism_name, dataset_name, expectation",
        [
            pytest.param("speciesA", "dataset_A1", does_not_raise(), id="OK to retire dataset"),
            pytest.param("speciesA", "datasets_Lorem_Ipsum",raises(KeyError), id="Dataset does not exist"),
        ],
    )
    def test_retire_dataset(
        self,
        engine: Engine,
        shared_orgs_file: Path,
        shared_dataset_file: Path,
        organism_name: str,
        dataset_name: str,
        expectation: ContextManager, 
    ) -> None:
        """Test retire a dataset."""
        fake_release = 10

        reg = RnaseqRegistry(engine)
        reg.create_db()
        reg.load_organisms(shared_orgs_file)
        reg.load_datasets(shared_dataset_file, release=fake_release)
        datasets = reg.list_datasets(organism=organism_name, dataset_name=dataset_name)

        for dataset in datasets:
            with expectation: 
                reg.retire_dataset(dataset)
    
    @pytest.mark.dependency(name="dump_datasets", depends=["list_datasets"])
    @pytest.mark.parametrize(
        "datasets_file, expected_dumped_file, expectation",
        [
            pytest.param(
                "datasets_several.json", "datasets_several_sorted.json", does_not_raise(), id="Dump same file"
            ),
        ],
    )
    def test_dump_datasets(
        self,
        assert_files: Callable,
        data_dir: Path,
        tmp_path: Path,
        engine: Engine,
        shared_orgs_file: Path,
        datasets_file: Path,
        expected_dumped_file: Path,
        expectation: ContextManager,
    ) -> None:
        """Test dumping a dataset file."""
        component = None
        organism = None
        dataset = None
        release = None
        fake_release = 0

        reg = RnaseqRegistry(engine)
        reg.create_db()
        reg.load_organisms(shared_orgs_file)

        reg.load_datasets(data_dir / datasets_file, release=fake_release)
        dumped_path = tmp_path / "output_dump.json"
        with expectation:
            datasets = reg.list_datasets(
                component=component, organism=organism, dataset_name=dataset, release=release
            )
            reg.dump_datasets(dumped_path, datasets)
            assert_files(dumped_path, data_dir / expected_dumped_file)

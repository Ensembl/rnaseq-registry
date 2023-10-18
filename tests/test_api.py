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

import pytest
from sqlalchemy import inspect, create_engine, Engine

from ensembl.rnaseq.registry.api import RnaseqRegistry


class Test_RNASeqRegistry:
    """Tests for the RNASeqRegistry module."""

    @pytest.fixture(scope="module")
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
        insp = inspect(reg.engine)
        assert insp.has_table("dataset")
        assert insp.has_table("sample")
        assert insp.has_table("organism")

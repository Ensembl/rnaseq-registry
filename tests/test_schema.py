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
Unit tests of the main RNA-Seq schema module.
"""

import pytest
from sqlalchemy import inspect

from ensembl.rnaseq.registry.database_schema import Base, Dataset, Sample, Organism, create_db


class Test_schema:
    """Tests for the database_schema registry module."""

    @pytest.fixture(scope='module')
    def engine(self) -> "Engine":
        """
        Generate the Engine. Use an in-memory DB.
        """
        test_db = "test_db"
        test_engine = create_db(test_db)
        assert isinstance(test_engine, create_db)
        print(test_db)
        return test_engine
        
    
    def test_create_tables(self, engine: "Engine") -> None:
        """Test creating tables from scratch."""
        
        insp = inspect(engine)
        # Check if the tables are created in the test database file
        assert insp.has_table("dataset")
        assert insp.has_table("sample")
        assert insp.has_table("organism")


    
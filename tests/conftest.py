# See the NOTICE file distributed with this work for additional information
# regarding copyright ownership.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Local directory-specific hook implementations.

"""

from difflib import unified_diff
from pathlib import Path
from typing import Callable

import pytest
from pytest import FixtureRequest


@pytest.fixture(name="data_dir", scope="module")
def local_data_dir(request: FixtureRequest) -> Path:
    """Returns the path to the test data folder matching the test's name.

    Args:
        request: Fixture providing information of the requesting test function.

    """
    return Path(request.module.__file__).with_suffix("")


@pytest.fixture(name="assert_files")
def assert_files() -> Callable[[Path, Path], None]:
    """Provide a function that asserts two files and show a diff if they differ."""

    def _assert_files(result_path: Path, expected_path: Path) -> None:
        with open(result_path, "r") as result_fh:
            results = result_fh.readlines()
        with open(expected_path, "r") as expected_fh:
            expected = expected_fh.readlines()
        files_diff = list(unified_diff(results, expected, fromfile="Test-made file", tofile="Expected file"))
        assert_message = f"Test-made and expected files differ\n{' '.join(files_diff)}"
        assert len(files_diff) == 0, assert_message

    return _assert_files

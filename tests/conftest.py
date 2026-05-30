import json
import os
from typing import Any

import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))


@pytest.fixture
def worked_chain() -> dict[str, Any]:
    with open(os.path.join(ROOT, "worked-example", "recovery_drone_chain.json")) as f:
        return json.load(f)


@pytest.fixture
def worked_expected() -> dict[str, Any]:
    with open(os.path.join(ROOT, "worked-example", "recovery_drone_expected.json")) as f:
        return json.load(f)

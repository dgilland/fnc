from unittest import mock

import pytest


@pytest.fixture
def mocksleep():
    with mock.patch("time.sleep") as mocked:
        yield mocked

from datetime import datetime

import pytest


@pytest.fixture
def time_tracker():
    tick = datetime.now()
    yield  # pass CPU to run our test
    tock = datetime.now()
    diff = tock - tick
    print(f'\n runtime: {diff.total_seconds()}')

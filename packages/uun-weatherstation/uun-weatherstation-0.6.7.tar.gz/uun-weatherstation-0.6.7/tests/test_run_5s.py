import pytest
import time

class TestPackageRun:
    def test_config(self, gateway):
        with gateway as g:
            time.sleep(5)


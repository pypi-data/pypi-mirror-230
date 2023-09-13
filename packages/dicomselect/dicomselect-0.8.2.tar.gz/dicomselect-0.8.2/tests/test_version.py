from dicomselect import version as dicomselect_version
from setup import version


def test_version():
    assert version == dicomselect_version
    
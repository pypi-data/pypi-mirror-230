import argparse
import pytest
from hcristian.main import main
from jnpr.junos import Device
from lxml import etree


def test_hc(monkeypatch):
    mock_response = """
    <rpc-reply>
        <name>junos</name>
        <comment>JUNOS Software Release [12.1I20130220_0302_hhuang]</comment>
    </rpc-reply>
    """

    def mock_parse_args(*args):
        return argparse.Namespace(device="vsrx1")

    def mock_device(*args, **kwargs):
        # Mock the behavior of the Device class here
        class MockedDevice:
            def __init__(self, *args, **kwargs):
                pass

            def open(self):
                pass

            def close(self):
                pass

            @property
            def rpc(self):
                return MockedRPC()

        class MockedRPC:
            def get_software_information(self, *args, **kwargs):
                result = etree.fromstring(mock_response)
                return result

        return MockedDevice(*args, **kwargs)

    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", mock_parse_args)
    monkeypatch.setattr(Device, "__new__", mock_device)
    assert (
        main()
        == "JUNOS Software Release [12.1I20130220_0302_hhuang] installed on vsrx1"
    )


def test_hc_raises():
    with pytest.raises(ValueError):
        main()

import cjen
from cjen import MetaMysql


class TestData(MetaMysql):

    @cjen.operate.mysql.bytes_to_bool
    @cjen.operate.common.value
    def open(self): ...



def test_bytes_to_bool():
    data = TestData()
    data.meta_data["open"] = b'\x01'
    assert data.open() is True
    data.meta_data["open"] = b'\x00'
    assert data.open() is False
    data.meta_data["open"] = None
    assert data.open() is False
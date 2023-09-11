import unittest
import unittest.mock
from unittest.mock import patch
from smd import red


class TestBrushed(unittest.TestCase):

    def setUp(self) -> None:
        self.dev = red.Red(1)

    def tearDown(self) -> None:
        pass

    def test_set_variables(self):
        pass

    def test_get_variables(self):
        pass

    def test_reboot(self):
        pass

    def test_EEPROM_write(self):
        pass

    def test_ping(self):
        pass

    def change_id(self):
        pass


class TestMaster(unittest.TestCase):
    def setUp(self) -> None:
        patcher = patch("smd.red.serial.Serial", autospec=True)
        self.mock = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock.reset_mock()

    def tearDown(self) -> None:
        pass

    def test_set_variables(self):
        pass

    def test_get_variables(self):
        pass

    def test_reboot(self):
        pass

    def test_EEPROM_write(self):
        pass

    def test_ping(self):
        pass

    def test_update_baudrate(self):
        pass

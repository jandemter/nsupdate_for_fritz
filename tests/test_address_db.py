"""
Copyright 2020 Jan Demter <jan@demter.de>

This file is part of nsupdate_for_fritz.

nsupdate_for_fritz is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

nsupdate_for_fritz is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with nsupdate_for_fritz.  If not, see <http://www.gnu.org/licenses/>.
"""
import unittest

from nsupdate_for_fritz.address_db import AddressDB

class AddressDBTest(unittest.TestCase):
    """test address DB cache"""

    def setUp(self) -> None:
        self.adb = AddressDB(':memory:')

    def test_v4_new(self):
        self.adb.begin_transaction()
        changed = self.adb.address_changed('testv4', '192.0.2.23')
        self.assertTrue(changed)
        self.adb.commit()

    def test_v6_new(self):
        self.adb.begin_transaction()
        changed = self.adb.address_changed('testv6', '2001:DB8::23', 6)
        self.assertTrue(changed)
        self.adb.commit()

    def test_v4_present(self):
        self.adb.begin_transaction()
        self.adb.address_changed('testv4present', '192.0.2.42')
        self.adb.commit()
        self.adb.begin_transaction()
        changed = self.adb.address_changed('testv4present', '192.0.2.42')
        self.assertFalse(changed)

    def test_v6_present(self):
        self.adb.begin_transaction()
        self.adb.address_changed('testv6present', '2001:DB8::42', 6)
        self.adb.commit()
        self.adb.begin_transaction()
        changed = self.adb.address_changed('testv6present', '2001:DB8::42', 6)
        self.assertFalse(changed)

    def test_changed_status_v4(self):
        adb = AddressDB(':memory:')
        self.assertFalse(adb.some_address_changed)
        adb.begin_transaction()
        changed = adb.address_changed('test4changed', '192.0.2.64')
        self.assertTrue(changed)
        self.assertTrue(adb.some_address_changed)

    def test_changed_status_v6(self):
        adb = AddressDB(':memory:')
        self.assertFalse(adb.some_address_changed)
        adb.begin_transaction()
        changed = adb.address_changed('test6changed', '2001:DB8::64', 6)
        self.assertTrue(changed)
        self.assertTrue(adb.some_address_changed)

if __name__ == '__main__':
    unittest.main()

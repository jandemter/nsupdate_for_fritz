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
import socket
import unittest
import ipaddress

import requests

import nsupdate_for_fritz.addresses


def fritzbox_absent():
    try:
        res = requests.get('http://fritz.box/', timeout=5)
        if res.status_code == 200 and b'FRITZ!Box' in res.content:
            return False
        else:
            return True
    except requests.exceptions.RequestException:
        return True


def v6_connectivity_absent():
    s = None
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        # address is Google DNS, as it's an UDP socket this will not generate any traffic
        s.connect(('2001:4860:4860::8888', 54321))
        sockname = s.getsockname()
    except OSError:
        if s is not None:
            s.close()
        return True
    local_v6_addr = ipaddress.IPv6Address(sockname[0])
    s.close()
    if local_v6_addr.is_global:
        return False
    return True


@unittest.skipIf(fritzbox_absent(), 'no real FRITZ!Box present')
class RealFritzboxTests(unittest.TestCase):
    def test_get_ipv4_address(self):
        v4_address = nsupdate_for_fritz.addresses.get_fritz_ip_address()
        # having no v4 address is ok since fritz!os 7.20 for IPv6-only upstream
        if v4_address == '':
            self.assertFalse(v6_connectivity_absent(), "no v6 connectivity and no IPv4 address found")
            return
        self.assertRegex(v4_address, r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

    @unittest.skipIf(v6_connectivity_absent(), 'no IPv6 connectivity')
    def test_get_ipv6_address(self):
        v6_address = nsupdate_for_fritz.addresses.get_v6_address('fritz.box')
        v6_ip_address = ipaddress.IPv6Address(v6_address)
        self.assertTrue(v6_ip_address.is_global)


if __name__ == '__main__':
    unittest.main()

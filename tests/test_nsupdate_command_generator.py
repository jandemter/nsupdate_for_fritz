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
from unittest.mock import patch
import textwrap

import nsupdate_for_fritz.nsupdate
from tests import helpers

test_config_path = helpers.config_files_path()


@patch('nsupdate_for_fritz.nsupdate.get_fritz_ip_address', lambda x: '192.0.2.23')
class NsupdateCommandGeneratorTest(unittest.TestCase):
    def test_a_record(self):
        nsupdate_commands = nsupdate_for_fritz.nsupdate.generate_nsupdate_commands(test_config_path / 'test_A_config.ini')
        reference_commands = bytes(textwrap.dedent("""
            key KEY_TYPE_HERE:NSUPDATE_KEY_NAME_HERE NSUPDATE_KEY_HERE
            server NAMESERVER_HERE
            zone ZONE_NAME_HERE

            update delete testhostname.ZONE_NAME_HERE. A
            update add testhostname.ZONE_NAME_HERE. 300 A 192.0.2.23

            send"""), 'utf8')
        self.assertEqual(nsupdate_commands, reference_commands)

    def test_no_txt_config_section(self):
        nsupdate_commands = nsupdate_for_fritz.nsupdate.generate_nsupdate_commands(test_config_path /
                                                                               'test_no_txt_config.ini')
        reference_commands = bytes(textwrap.dedent("""
            key KEY_TYPE_HERE:NSUPDATE_KEY_NAME_HERE NSUPDATE_KEY_HERE
            server NAMESERVER_HERE
            zone ZONE_NAME_HERE

            update delete testhostname.ZONE_NAME_HERE. A
            update add testhostname.ZONE_NAME_HERE. 300 A 192.0.2.23

            send"""), 'utf8')
        self.assertEqual(nsupdate_commands, reference_commands)

    def test_txt_records(self):
        nsupdate_commands = nsupdate_for_fritz.nsupdate.generate_nsupdate_commands(test_config_path / 'test_TXT_config.ini')
        reference_commands = bytes(textwrap.dedent("""
            key KEY_TYPE_HERE:NSUPDATE_KEY_NAME_HERE NSUPDATE_KEY_HERE
            server NAMESERVER_HERE
            zone ZONE_NAME_HERE

            update delete sometxt.ZONE_NAME_HERE. TXT
            update add sometxt.ZONE_NAME_HERE. 30 TXT hello

            update delete _acme-challenge.some-hostname.ZONE_NAME_HERE. TXT
            update add _acme-challenge.some-hostname.ZONE_NAME_HERE. 30 TXT abcde123fg567

            send"""), 'utf8')
        self.assertEqual(nsupdate_commands, reference_commands)

    @patch('nsupdate_for_fritz.addresses.socket.getaddrinfo', helpers.mock_v6_getaddr)
    def test_aaaa_records(self):
        nsupdate_commands = nsupdate_for_fritz.nsupdate.generate_nsupdate_commands(test_config_path /
                                                                               'test_AAAA_config.ini')
        reference_commands = bytes(textwrap.dedent("""
            key KEY_TYPE_HERE:NSUPDATE_KEY_NAME_HERE NSUPDATE_KEY_HERE
            server NAMESERVER_HERE
            zone ZONE_NAME_HERE

            update delete testhostname.ZONE_NAME_HERE. AAAA
            update add testhostname.ZONE_NAME_HERE. 300 AAAA 2a00:1450:4001:824::200e

            update delete some-other-hostname.ZONE_NAME_HERE. AAAA
            update add some-other-hostname.ZONE_NAME_HERE. 300 AAAA 2001:4860:4860::8888

            send"""), 'utf8')
        self.assertEqual(nsupdate_commands, reference_commands)

    @patch('nsupdate_for_fritz.addresses.socket.getaddrinfo', helpers.mock_v6_getaddr)
    def test_aaaa_fritzbox(self):
        nsupdate_commands = nsupdate_for_fritz.nsupdate.generate_nsupdate_commands(test_config_path /
                                                                               'test_AAAA_fritzbox_config.ini')
        reference_commands = bytes(textwrap.dedent("""
            key KEY_TYPE_HERE:NSUPDATE_KEY_NAME_HERE NSUPDATE_KEY_HERE
            server NAMESERVER_HERE
            zone ZONE_NAME_HERE

            update delete fritz-test.ZONE_NAME_HERE. AAAA
            update add fritz-test.ZONE_NAME_HERE. 300 AAAA 2001:4860:4860::8844

            send"""), 'utf8')
        self.assertEqual(nsupdate_commands, reference_commands)


@patch('nsupdate_for_fritz.nsupdate.get_fritz_ip_address',
       lambda x: '192.0.2.46' if x == 'fratz.test' else None)
@patch('nsupdate_for_fritz.addresses.socket.getaddrinfo', helpers.mock_v6_getaddr)
class NsupdateCommandGeneratorOtherFritzboxNameTest(unittest.TestCase):
    def test_a_record_aaaa_fritzbox(self):
        nsupdate_commands = nsupdate_for_fritz.nsupdate.generate_nsupdate_commands(
            test_config_path / 'test_other_fritzbox_name_config.ini')
        reference_commands = bytes(textwrap.dedent("""
            key KEY_TYPE_HERE:NSUPDATE_KEY_NAME_HERE NSUPDATE_KEY_HERE
            server NAMESERVER_HERE
            zone ZONE_NAME_HERE

            update delete testhostname.ZONE_NAME_HERE. A
            update add testhostname.ZONE_NAME_HERE. 300 A 192.0.2.46

            update delete fritz-test.ZONE_NAME_HERE. AAAA
            update add fritz-test.ZONE_NAME_HERE. 300 AAAA 2001:4860:4860::effe

            send"""), 'utf8')
        self.assertEqual(nsupdate_commands, reference_commands)


if __name__ == '__main__':
    unittest.main()

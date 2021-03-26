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
import sys
import unittest
from unittest.mock import patch
import textwrap
import contextlib
from io import StringIO
import subprocess

from tests.helpers import config_files_path, util_path

import nsupdate_for_fritz.util


class CliUtilityDryRunTests(unittest.TestCase):
    reference_commands = textwrap.dedent("""
            key KEY_TYPE_HERE:NSUPDATE_KEY_NAME_HERE NSUPDATE_KEY_HERE
            server NAMESERVER_HERE
            zone ZONE_NAME_HERE

            update delete sometxt.ZONE_NAME_HERE. TXT
            update add sometxt.ZONE_NAME_HERE. 30 TXT hello

            update delete _acme-challenge.some-hostname.ZONE_NAME_HERE. TXT
            update add _acme-challenge.some-hostname.ZONE_NAME_HERE. 30 TXT abcde123fg567

            send
            """)

    @patch('sys.argv', ['nsupdate_for_fritz', '--dry-run', str(config_files_path() / 'test_TXT_config.ini')])
    def test_cli(self):
        stdout = StringIO()
        with contextlib.redirect_stdout(stdout):
            ret = nsupdate_for_fritz.util.main()
        self.assertEqual(ret, 0)
        stdout.seek(0)
        self.assertEqual(stdout.read(), self.reference_commands)

    @unittest.skipIf(sys.hexversion < 0x3070000, 'capture_output unavailable in Python 3.6 and lower')
    def test_cli_python(self):
        cli = subprocess.run((sys.executable, util_path(), '--dry-run',
                              config_files_path() / 'test_TXT_config.ini'),
                             capture_output=True, encoding='utf8')
        self.assertEqual(cli.returncode, 0)
        self.assertEqual(cli.stdout, self.reference_commands)

    @unittest.skipIf(sys.hexversion < 0x3070000, 'capture_output unavailable in Python 3.6 and lower')
    def test_cli_python_m(self):
        cli = subprocess.run((sys.executable, '-m', 'nsupdate_for_fritz', '--dry-run',
                              config_files_path() / 'test_TXT_config.ini'),
                             capture_output=True, encoding='utf8')
        self.assertEqual(cli.returncode, 0)
        self.assertEqual(cli.stdout, self.reference_commands)


if __name__ == '__main__':
    unittest.main()

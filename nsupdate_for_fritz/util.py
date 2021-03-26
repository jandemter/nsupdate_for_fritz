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
import subprocess
import sys
from pathlib import Path
import argparse
import logging

from nsupdate_for_fritz.address_db import AddressDB
from nsupdate_for_fritz.nsupdate import generate_nsupdate_commands


def main() -> int:
    """main CLI entry point"""
    config_file_path = Path(__file__).parent.parent.joinpath('config.ini')
    parser = argparse.ArgumentParser(
        description='uses nsupdate to update zones with addresses of your FRITZ!Box')
    parser.add_argument('config_file', nargs='?', default=config_file_path,
                        help=f'path to config file (optional, uses {config_file_path} by default), '
                             'use "-" for stdin')
    parser.add_argument('--dry-run', action='store_true',
                        help='no changes done, only echoes updates to be sent')
    parser.add_argument('--debug', '-d', action='store_true', help='enable debug logging')
    parser.add_argument('--address-cache', '-a', help='address cache DB file', default=None)
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig()

    logging.debug('using config file %s', args.config_file)

    address_db = AddressDB(args.address_cache)
    address_db.begin_transaction()

    nsupdate_commands = generate_nsupdate_commands(args.config_file, address_db)
    if nsupdate_commands is None:
        return 2

    if args.address_cache and not address_db.some_address_changed:
        logging.debug('nothing changed, not running nsupdate')
        return 0

    if args.dry_run:
        print(nsupdate_commands.decode('utf8'))
        return 0

    logging.debug('running nsupdate')
    nsupdate = subprocess.run('nsupdate', input=nsupdate_commands, check=False)
    if nsupdate.returncode != 0:
        logging.error('nsupdate failed - check output')
        return nsupdate.returncode

    address_db.commit()
    return 0


if __name__ == '__main__':
    sys.exit(main())

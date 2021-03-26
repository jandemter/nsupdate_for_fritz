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
import logging
import pathlib
import sqlite3
from sqlite3.dbapi2 import Cursor
from typing import Union, Optional

from nsupdate_for_fritz.exceptions import NsupdateFritzCacheFailure

logger = logging.getLogger(__name__)


class AddressDB:
    """manages an IP address cache DB"""
    db_conn: sqlite3.Connection
    cursor: Cursor
    some_address_changed: bool

    def __init__(self, db_file: Optional[Union[pathlib.Path, str]]):
        if db_file is None:
            db_file = ':memory:'
        logger.debug('using AddressDB at "%s"', db_file)
        self.db_conn = sqlite3.connect(db_file)
        self.db_conn.execute("""CREATE TABLE IF NOT EXISTS last_addresses (
                            hostname VARCHAR(256) NOT NULL,
                            address VARCHAR(256) NOT NULL,
                            protocol INTEGER UNSIGNED CHECK ( protocol IN (4, 6)) NOT NULL,
                            UNIQUE(hostname, protocol) ON CONFLICT ABORT)""")
        self.some_address_changed = False

    def begin_transaction(self):
        """begin DB transaction"""
        self.cursor = self.db_conn.cursor()
        self.cursor.execute('BEGIN TRANSACTION')

    def commit(self):
        """commit DB transcation"""
        self.cursor.execute('COMMIT')
        self.cursor.close()

    def address_changed(self, hostname: str, current_address: str,
                        protocol: int = 4) -> bool:
        """will return whether the supplied hostname/address combination has changed and
           update the DB if it did"""
        self.cursor.execute(
            'SELECT address FROM last_addresses WHERE hostname = ? AND protocol = ?',
            (hostname, protocol))
        result = self.cursor.fetchone()
        if result is not None and result[0] == current_address:
            logger.debug("address for '%s' did not change (%s, IPv%s)", hostname,
                         current_address, protocol)
            return False
        self.some_address_changed = True
        self.update_address(hostname, current_address, protocol)
        return True

    def update_address(self, hostname: str, current_address: str, protocol: int = 4):
        """update address cache entry"""
        self.cursor.execute(
            '''INSERT INTO last_addresses (address, hostname, protocol) VALUES (?, ?, ?)
            ON CONFLICT (hostname, protocol) DO UPDATE SET address=?''',
            (current_address, hostname, protocol, current_address))
        if self.cursor.rowcount != 1:
            self.cursor.execute('ROLLBACK')
            raise NsupdateFritzCacheFailure(
                f'updating {hostname} (IPv{protocol}) failed')

        logger.debug("updated '%s' to %s (IPv%s)", hostname, current_address, protocol)

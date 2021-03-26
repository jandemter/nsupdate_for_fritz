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
import textwrap
from configparser import ConfigParser
from pathlib import Path
import logging
from typing import Union

from nsupdate_for_fritz.addresses import get_fritz_ip_address, get_v6_address
from nsupdate_for_fritz.exceptions import NsupdateFritzIPv4Missing
from nsupdate_for_fritz.address_db import AddressDB

logger = logging.getLogger(__name__)


def read_config(config_file_path: Union[Path, str]) -> ConfigParser:
    """parse configuration .ini file with ConfigParser"""
    config: ConfigParser = ConfigParser(strict=True)
    if config_file_path == '-':
        logger.debug('reading config from stdin')
        config.read_string(sys.stdin.read())
    else:
        logger.debug('reading config file')
        with open(config_file_path) as config_file:
            config.read_file(config_file)
    logger.debug('%d config sections, %d entries', len(config.sections()),
                 sum(len(x) for x in config.sections()))
    return config


def generate_nsupdate_commands(config_file_path: Union[Path, str],
                               address_db: AddressDB = None) -> bytes:
    """generates commands to be sent to nsupdate from configuration file and addresses"""

    if address_db is None:
        address_db = AddressDB(':memory:')
        address_db.begin_transaction()

    config = read_config(config_file_path)

    fritzbox_name = get_fritzbox_name(config)

    # will hold the IPv4 address of the FRITZ!Box (if any)
    ip_address = None

    zone = config['server']['zone']

    nsupdate_commands = textwrap.dedent(f"""
        key {config['server']['key_type']}:{config['server']['key_name']} {config['server']['key']}
        server {config['server']['name']}
        zone {zone}
    """)

    for hostname in config['hosts']:
        if 'v4' in config['hosts'][hostname]:
            if ip_address is None:
                ip_address = get_fritz_ip_address(fritzbox_name)
            if ip_address == '':
                raise NsupdateFritzIPv4Missing(
                    f"no IPv4 address found, cannot nsupdate '{hostname}'")

            this_address_changed = address_db.address_changed(hostname, ip_address, 4)

            if not this_address_changed:
                continue

            nsupdate_commands += textwrap.dedent(f"""
                update delete {hostname}.{zone}. A
                update add {hostname}.{zone}. {config['server']['TTL_A']} A {ip_address}
            """)
        if 'v6:' in config['hosts'][hostname]:
            v6_hostname = config['hosts'][hostname].split('v6:')[1]
            v6_address = get_v6_address(v6_hostname, fritzbox_name)

            this_address_changed = address_db.address_changed(hostname, v6_address, 6)
            if not this_address_changed:
                continue

            nsupdate_commands += textwrap.dedent(f"""
                update delete {hostname}.{zone}. AAAA
                update add {hostname}.{zone}. {config['server']['TTL_AAAA']} AAAA {v6_address}
            """)
        elif 'v6' in config['hosts'][hostname]:
            v6_address = get_v6_address(hostname, fritzbox_name)

            this_address_changed = address_db.address_changed(hostname, v6_address, 6)
            if not this_address_changed:
                continue

            nsupdate_commands += textwrap.dedent(f"""
                update delete {hostname}.{zone}. AAAA
                update add {hostname}.{zone}. {config['server']['TTL_AAAA']} AAAA {v6_address}
            """)

    if 'txt' in config:
        for hostname in config['txt']:
            nsupdate_commands += textwrap.dedent(f"""
                update delete {hostname}.{zone}. TXT
                update add {hostname}.{zone}. {config['server']['TTL_TXT']} TXT {config['txt'][hostname]}
            """)

    nsupdate_commands += "\nsend"

    return bytes(nsupdate_commands, encoding='utf8')


def get_fritzbox_name(config: ConfigParser) -> str:
    """returns the configured hostname of the FRITZ!Box or the default one"""
    if config.has_section('fritzbox'):
        fritzbox_name = config['fritzbox']['name']
    else:
        fritzbox_name = 'fritz.box'
    return fritzbox_name

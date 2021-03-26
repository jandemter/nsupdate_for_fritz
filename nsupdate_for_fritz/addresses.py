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
import ipaddress
import re
import socket
import logging

import requests

from nsupdate_for_fritz.exceptions import NsupdateFritzNoMatch

logger = logging.getLogger(__name__)


def get_fritz_ip_address(fritzbox_name: str='fritz.box') -> str:
    """get current IPv4 address (if any) from AVM FRITZ!Box"""
    logger.debug('getting IPv4 address')

    post_data = """<?xml version='1.0' encoding='utf-8'?>
        <s:Envelope s:encodingStyle='http://schemas.xmlsoap.org/soap/encoding/'
                xmlns:s='http://schemas.xmlsoap.org/soap/envelope/'>
            <s:Body>
                <u:GetExternalIPAddress xmlns:u='urn:schemas-upnp-org:service:WANIPConnection:1' />
            </s:Body>
        </s:Envelope>"""
    headers = {
        'SoapAction': 'urn:schemas-upnp-org:service:WANIPConnection:1#GetExternalIPAddress',
        'Content-Type': 'text/xml; charset="utf-8"'}

    res = requests.post(f'http://{fritzbox_name}:49000/igdupnp/control/WANIPConn1',
                        data=post_data, headers=headers)
    res.raise_for_status()
    result = re.search(
        rb'<NewExternalIPAddress>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|)</NewExternalIPAddress>',
        res.content)

    if result is None:
        raise NsupdateFritzNoMatch('IPv4 regex did not match')

    v4_address = result.groups()[0]
    if v4_address == b'':
        logger.debug('no IPv4 address found, DS-Lite/CGN in use?')
    else:
        logger.debug('IPv4 address is %s', v4_address)
    return str(v4_address, encoding='utf8')


def get_v6_address(v6_hostname: str, fritzbox_name: str='fritz.box') -> str:
    """gets the IPv6 address of any host currently connected to the FRITZ!Box"""
    logger.debug('getting IPv6 address for %s', v6_hostname)

    if v6_hostname in (fritzbox_name, f'{fritzbox_name}.'):
        v6_hostname_int = f'{fritzbox_name}.'
    else:
        v6_hostname_int = f"{v6_hostname}.{fritzbox_name}."
    v6_addresses = socket.getaddrinfo(v6_hostname_int, None, socket.AF_INET6, socket.SOCK_STREAM)

    logger.debug('got %d IPv6 addresses: %r', len(v6_addresses), v6_addresses)

    # filter non-global addresses (i.e. ULA ones that AVM configures)
    v6_addresses = [addr for addr in v6_addresses if ipaddress.IPv6Address(addr[4][0]).is_global]

    if len(v6_addresses) > 0:
        v6_address = v6_addresses[0][4][0]
        logger.debug('IPv6 address for %s is %s', v6_hostname_int, v6_address)
        return v6_address

    raise ValueError(f'no global v6 address found for {v6_hostname}')

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
import pathlib
import socket


def config_files_path() -> pathlib.Path:
    return pathlib.Path(__file__).parent / 'test_configs'


def util_path() -> pathlib.Path:
    return pathlib.Path(__file__).parent.parent / 'nsupdate_for_fritz' / 'util.py'


def mock_v6_getaddr(hostname, _, af, sock_type):
    if af == socket.AF_INET6 and sock_type == socket.SOCK_STREAM:
        if hostname == 'testhostname.fritz.box.':
            return (
                (
                    socket.AF_INET6,
                    socket.SOCK_STREAM,
                    socket.IPPROTO_TCP,
                    '',
                    ('2a00:1450:4001:824::200e', 0, 0, 0)
                ),
            )
        elif hostname == 'test-v6-hostname.fritz.box.':
            return (
                (
                    socket.AF_INET6,
                    socket.SOCK_STREAM,
                    socket.IPPROTO_TCP,
                    '',
                    ('2001:4860:4860::8888', 0, 0, 0)
                ),
            )
        elif hostname == 'fritz.box.':
            return (
                (
                    socket.AF_INET6,
                    socket.SOCK_STREAM,
                    socket.IPPROTO_TCP,
                    '',
                    ('2001:4860:4860::8844', 0, 0, 0)
                ),
            )
        elif hostname == 'fratz.test.':
            return (
                (
                    socket.AF_INET6,
                    socket.SOCK_STREAM,
                    socket.IPPROTO_TCP,
                    '',
                    ('2001:4860:4860::effe', 0, 0, 0)
                ),
            )
        else:
            raise socket.gaierror(8, '[Errno 8] nodename nor servname provided, or not known')
    else:
        raise ValueError('mock handles AF_INET6 only')

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
from setuptools import setup, find_packages

setup(name='nsupdate_for_fritz',
      version='0.1.0',
      author='Jan Demter',
      author_email='jan@demter.de',
      url='https://github.com/jandemter/nsupdate_for_fritz',
      download_url='https://github.com/jandemter/nsupdate_for_fritz/zipball/master',
      license='GPLv3',
      description='Gets current IP address of your AVM FRITZ!Box and uses nsupdate to update A records with it',
      long_description="""
          nsupdate_for_fritz gets the current IPv4 address of your AVM FRITZ!Box and then uses nsupdate to update
          one or more A records with it. It can also do the same for IPv6 addresses of hosts on your network.
      """,
      classifiers=['Development Status :: 3 - Alpha',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Topic :: Internet',
                   'Topic :: Utilities',
                   'Intended Audience :: End Users/Desktop',
                   'Environment :: Console',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8',
                   'Programming Language :: Python :: 3.9',
                   'Programming Language :: Python :: 3.10',
                   'Programming Language :: Python :: 3.11',
                   ],
      packages=find_packages(),
      entry_points={'console_scripts': ['nsupdate_for_fritz = nsupdate_for_fritz.util:main']},
      install_requires=['requests'],
      test_suite="tests"
      )

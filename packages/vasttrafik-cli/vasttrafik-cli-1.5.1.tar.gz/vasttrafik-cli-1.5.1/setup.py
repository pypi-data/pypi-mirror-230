#!/usr/bin/env python3

# vasttrafik-cli
# Copyright (C) 2023 Salvo "LtWorf" Tomaselli
#
# vasttrafik-cli is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# author Salvo "LtWorf" Tomaselli <tiposchi@tiscali.it>

from setuptools import setup

setup(
    version='1.5.1',
    name='vasttrafik-cli',
    description='CLI for the public transport in Göteborg and the Västra Götaland county',
    packages=['vasttrafik'],
    keywords='tram göteborg västtrafik cli',
    author="Salvo 'LtWorf' Tomaselli",
    author_email='tiposchi@tiscali.it',
    maintainer="Salvo 'LtWorf' Tomaselli",
    maintainer_email='tiposchi@tiscali.it',
    url='https://codeberg.org/ltworf/vasttrafik-cli',
    license='GPL3',
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Environment :: Console',
    ],
    entry_points={
        'console_scripts': [
            'trip = vasttrafik.cli:tripmain',
            'stops = vasttrafik.cli:stopsmain',
        ]
    },
    install_requires=[
        'typedload',
        'xtermcolor',
        'configobj',
        'wcwidth',
    ]
)

# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2012, 2013, 2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import absolute_import, unicode_literals
from functools import partial
from glob import glob
from importlib import import_module
import os
from subprocess import Popen, PIPE, STDOUT
import sys


class SetupError(Exception):

    def __init__(self, e):
        super(SetupError, self).__init__(e)


class SetupDB(object):
    'Setup the database tables'
    @staticmethod
    def get_sql_filenames_from_products(products):
        '''Get the SQL files from the products

:param str products: The products, as a whitespace seperated string
:returns: The SQL files to load, in order.
:rtype: A ``list`` of ``str``.'''
        retval = []
        for moduleId in [p.strip() for p in products.split()]:
            module = import_module(moduleId)
            sqlDir = os.path.join(os.path.join(*module.__path__), 'sql')
            sqlFiles = glob(os.path.join(sqlDir, '*sql'))
            sqlFiles.sort()  # The files should be numbered, so sortable.
            retval += sqlFiles
        assert type(retval) == list
        return retval

    def setup_database(self, user, host, port, database, products):
        e = partial(self.get_sql_filenames_from_products, user, host, port,
                        database)
        for filename in (products):
            s, o = e(filename=filename)
            m = o if o else '.'
            if s == 0:
                sys.stdout.write(m)
            else:
                raise SetupError(m)

    @staticmethod
    def execute_psql_with_file(user, host, port, database, filename):
        # We pass the -w option to psql because we trust that the
        # gs_install_ubuntu.sh script has set up the PGPASSFILE environment
        # variable.
        cmd = ['psql', '-w', '-U', user, '-h', host, '-p', port,
                        '-d', database, '-f', filename]
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT)
        p.wait()
        output = p.stdout.read()
        retval = (p.returncode, output)
        return retval

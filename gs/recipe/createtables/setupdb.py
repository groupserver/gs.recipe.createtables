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
from collections import namedtuple
from functools import partial
from glob import glob
from importlib import import_module
import os
from subprocess import Popen, PIPE, STDOUT
import sys


#: The named tuple that is used to return the output from the pipe
OutputReturn = namedtuple('OutputReturn', ('returncode', 'output'))


class SetupError(Exception):
    'An error with some SQL'
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
        for moduleId in [p.strip() for p in products.split() if p.strip()]:
            module = import_module(moduleId)
            sqlDir = os.path.join(os.path.join(*module.__path__), 'sql')
            sqlFiles = glob(os.path.join(sqlDir, '*sql'))
            sqlFiles.sort()  # The files should be numbered, so sortable.
            retval += sqlFiles
        assert type(retval) == list
        return retval

    def setup_database(self, user, host, port, database, products):
        '''Setup the databases with the SQL files in the named products.

:param str user: The PostgreSQL user.
:param str host: The PostgreSQL host.
:param str port: The PostgreSQL port.
:param str database: The name of the PostgreSQL database to connect to.
:param str products: The products to process, seperated by newline ``\n``
                     characters.
:returns: ``None``
:raises SetupError: There was an issue processing a file.

For each file that was successfully processed a ``.`` is displayed on the
standard outout.'''
        e_sql = partial(self.execute_psql_with_file, user, host, port, database)
        for filename in self.get_sql_filenames_from_products(products):
            r = e_sql(filename=filename)
            m = r.output if r.output else '.'
            if r.returncode == 0:
                sys.stdout.write(m)
            else:
                msg = 'Issue processing {0}\n{1}'.format(filename, m)
                raise SetupError(msg)

    @staticmethod
    def execute_psql_with_file(user, host, port, database, filename):
        '''Execute SQL in PostgreSQL

:param str user: The PostgreSQL user.
:param str host: The PostgreSQL host.
:param str port: The PostgreSQL port.
:param str database: The name of the PostgreSQL database to connect to.
:param str filename: The name of the SQL file to execute.
:returns: The return-code and output from :prog:`psql`.
:rtype: :class:`OutputReturn`.

The :meth:`execute_psql_with_file` method connects to the :prog:`psql`
command-line programme with a pipe, passing the paramaters necessary to connect
to the database. The output is read and returned along with the return-code
from :prog:`psql`.

.. seealso:: The :manpage:`psql(1)` manual page.'''
        # We pass the -w option to psql because we trust that the
        # gs_install_ubuntu.sh script has set up the PGPASSFILE environment
        # variable.
        cmd = ['psql', '-w', '-U', user, '-h', host, '-p', port,
                        '-d', database, '-f', filename]
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT)
        returncode = p.wait()
        output = p.stdout.read()
        retval = OutputReturn(returncode, output)
        return retval

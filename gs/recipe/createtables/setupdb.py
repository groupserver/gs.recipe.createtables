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
from contextlib import contextmanager
from functools import partial
import os
import pkg_resources
from subprocess import Popen, PIPE, STDOUT
import sys
from tempfile import NamedTemporaryFile

#: The named tuple that is used to return the output from the pipe
OutputReturn = namedtuple('OutputReturn', ('returncode', 'output'))


class SetupError(Exception):
    'An error with some SQL'
    def __init__(self, e):
        super(SetupError, self).__init__(e)


class SetupDB(object):
    '''Setup the database tables

:param str user: The PostgreSQL user.
:param str password: The password for the PostgreSQL user.
:param str host: The PostgreSQL host.
:param str port: The PostgreSQL port.
:param str database: The name of the PostgreSQL database to connect to.'''

    def __init__(self, user, password, host, port, database):
        # Set up the password-string. See 31.15 of the PostgreSQL manual
        # <http://www.postgresql.org/docs/9.3/static/libpq-pgpass.html>
        # The password is used with the setup_database method.
        p = '{host}:{port}:{database}:{user}:{password}'
        self.password = p.format(host=host, port=port, database=database,
                                    user=user, password=password)
        # Shouts out to Haskell Brooks Curry. Respect.
        self.exec_sql = partial(self.execute_psql_with_file, user=user,
                                host=host, port=port, database=database)

    @staticmethod  # Neither "self" nor class is used in this method.
    @contextmanager  # This method is used with a "with" statement
    def password_file(password):
        '''Write a password to a temporary file, to be used for auth later.

:param str password: The password to write to the temporary file.
:returns: The name of the file that contains the password.
:rtype: ``str``.

The :meth:`password_file` method provides a *context* *manager* that writes the
:arg:`password` argument to a temporary file and returns the name of the file.
Once the context closes the file containing the password is deleted.'''
        with NamedTemporaryFile('w', delete=False) as outfile:
            outfile.write(password)
            retval = outfile.name
        try:
            # Ensure that only the current user can read and write the file.
            os.chmod(retval, 0o0600)
            yield retval  # Return the filename
        finally:
            os.remove(retval)  # Ensure the file is deleted

    def setup_database(self, products, eggsDir):
        '''Setup the databases with the SQL files in the named products.

:param str products: The products to process, seperated by newline ``\n``
                     characters.
:param str eggsDir: The directory that contains the eggs for all the products.
:returns: ``None``
:raises SetupError: There was an issue processing a file.

This is the main entry-point to the :class:`SetupDB` class. It connects to
:prog:`PostgreSQL` using the connection information provided and adds the
SQL in the ``sql`` directories of the :arg:`products`.

For each file that was successfully processed a ``.`` is displayed on the
standard outout.'''
        with self.password_file(self.password) as passFile:
            sqlFiles = self.get_sql_filenames_from_products(products, eggsDir)
            for filename in sqlFiles:
                r = self.exec_sql(passFile=passFile, filename=filename)
                if r.returncode == 0:
                    sys.stdout.write('.')
                else:
                    msg = 'Issue processing {0}\n{1}'.format(filename, r.output)
                    raise SetupError(msg)

    def get_sql_filenames_from_products(self, products, eggsDir):
        '''Get the SQL files from the products

:param str products: The products, as a newline-seperated string
:param str eggsDir: The directory that contains the eggs for all the products.
:returns: The SQL files to load, in order. The files have absolute paths
          (starting from "/") and end in ``.sql``.
:rtype: A ``list`` of ``str``.'''
        productIds = [p.strip() for p in products.split('\n') if p.strip()]
        self.add_projects_to_working_set(productIds, eggsDir)
        retval = []
        for productId in productIds:
            if pkg_resources.resource_isdir(productId, 'sql'):
                allFiles = pkg_resources.resource_listdir(productId, 'sql')
                sqlFiles = [os.path.join('sql', s) for s in allFiles
                            if s[-4:] == '.sql']
                sqlFiles.sort()  # The files should be numbered, so sortable.
                fullFilenames = [pkg_resources.resource_filename(productId, f)
                                for f in sqlFiles]
                retval += fullFilenames
        assert type(retval) == list
        return retval

    @staticmethod
    def add_projects_to_working_set(projects, eggsDir):
        '''Add the list of porjects to the globlal "working_set".

:param list projects: The list of project-names to process.
:param str eggsDir: The directory that contains the eggs for all the products.
:returns: ``None``.'''
        environment = pkg_resources.Environment()
        for distribution in pkg_resources.find_distributions(eggsDir):
            environment += distribution
        ws = pkg_resources.working_set
        for projectName in projects:
            requirement = pkg_resources.Requirement.parse(projectName)
            for distribution in ws.resolve([requirement], environment):
                ws.add(distribution)

    @staticmethod
    def execute_psql_with_file(user, passFile, host, port, database, filename):
        '''Execute SQL in PostgreSQL

:param str user: The PostgreSQL user.
:param str passFile: The file that contains the PostgreSQL password of the user.
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
        # --=mpj17=-- Note: the -w flag
        cmd = ['psql', '-w', '-U', user, '-h', host, '-p', port,
                        '-d', database, '-f', filename]
        env = {'PATH': os.environ['PATH'],  # To find psql
                'PGPASSFILE': passFile}  # To authenticate
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, env=env)
        returncode = p.wait()
        output = p.stdout.read()
        retval = OutputReturn(returncode, output)
        return retval

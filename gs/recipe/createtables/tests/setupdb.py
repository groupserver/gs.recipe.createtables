# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2014, 2015 OnlineGroups.net and Contributors.
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
from __future__ import absolute_import, unicode_literals, print_function
from mock import patch, MagicMock
import os
from unittest import TestCase
import gs.recipe.createtables.setupdb as sdb
UTF8 = 'utf-8'


class TestSetupDB(TestCase):

    def setUp(self):
        self.setupDB = sdb.SetupDB('fake_user', 'fake_password',
                                    'db.example.com', '5432', 'fake_db')

    def test_password_file(self):
        password = 'This is a password. Honest.'
        with self.setupDB.password_file(password) as f:
            self.assertTrue(os.path.exists(f),
                            'Password file "{0}" does not exist'.format(f))
            with open(f, 'r') as infile:
                d = infile.read()
            self.assertEqual(password, d,
                                'The password in the password-file is wrong')

            s = os.stat(f)
            # The permissions are the last 12 bits of the mode == 0xFFF
            perms = oct(s.st_mode & 0o7777)
            # Use oct() on the literal for Py3 and Py2 compatibility
            self.assertEqual(oct(0o600), perms,  # RW for the user only.
                                'The permissions are too lax')

            fnForLater = f
        self.assertFalse(os.path.exists(fnForLater),
                        'The password file "{0}" exists'.format(fnForLater))

    def sql_file_test(self, f):
        self.assertEqual('/', f[0],
                        'Path is not from root: {0}'.format(f[0]))
        self.assertEqual('.sql', f[-4:],
                        'Not an SQL file: {0}'.format(f))
        self.assertTrue(os.path.exists(f),
                        'File does not exist: "{0}"'.format(f))

    def test_get_sql_filenames_from_product(self):
        'Can the system extract the SQL for a product?'
        products = 'gs.option\n'
        r = self.setupDB.get_sql_filenames_from_products(products, '')
        self.assertEqual(1, len(r))
        for filename in r:
            self.sql_file_test(filename)

    def test_get_sql_filenames_from_multiple_products(self):
        'Can the SQL be extracted for multiple products?'
        products = 'gs.option\nProducts.GSAuditTrail\n'
        r = self.setupDB.get_sql_filenames_from_products(products, '')
        self.assertEqual(2, len(r))
        for filename in r:
            self.sql_file_test(filename)

    def test_get_sql_filenames_from_multiple_products_2(self):
        'Do blank lines screw us up?'
        products = '\n\ngs.option\n\nProducts.GSAuditTrail\n\n'
        r = self.setupDB.get_sql_filenames_from_products(products, '')
        self.assertEqual(2, len(r))
        for filename in r:
            self.sql_file_test(filename)

    def test_execute_psql_with_file(self):
        'Can we construct a pipe to psql?'
        with patch('gs.recipe.createtables.setupdb.Popen', autospec=True) as Po:
            instance = Po.return_value
            instance.stdout = MagicMock(name='stdout')
            instance.stdout.read.return_value = 'East Kipling Road'
            instance.wait.return_value = 0

            r = self.setupDB.execute_psql_with_file('fake-user',
                    'fake-password', 'db.example.com', '5433', 'fake-db',
                    '/tmp/filename.sql')

            # Do we get the return-code from Popen back?
            self.assertEqual(0, r.returncode)
            # Do we get the data from the pipe back?
            self.assertEqual('East Kipling Road', r.output)
            # Did we call psql?
            args, kwargs = Po.call_args
            self.assertEqual('psql', args[0][0])

    def exec_sql_test(self, fn):
        self.assertEqual(1, fn.call_count,
                            'SetupDB.exec_sql called too many times')
        args, kwargs = fn.call_args
        self.assertIn('filename', kwargs)
        self.assertEqual('/tmp/filename.sql', kwargs['filename'])
        self.assertIn('passFile', kwargs)

    def test_setup_database_normal(self):
        self.setupDB.get_sql_filenames_from_products = \
            MagicMock(name='get_sql', return_value=['/tmp/filename.sql'])
        outputReturn = sdb.OutputReturn(returncode=0, output='')
        self.setupDB.exec_sql = MagicMock(name='exec_sql',
                                            return_value=outputReturn)

        with patch('gs.recipe.createtables.setupdb.sys.stdout') as sdb_stdout:
            self.setupDB.setup_database('gs.option', 'eggs/')

        gsqlf = self.setupDB.get_sql_filenames_from_products
        gsqlf.assert_called_once_with('gs.option', 'eggs/')
        self.exec_sql_test(self.setupDB.exec_sql)
        sdb_stdout.write.assert_called_once_with('.')

    def test_setup_database_issues(self):
        self.setupDB.get_sql_filenames_from_products = \
            MagicMock(name='get_sql', return_value=['/tmp/filename.sql'])
        outputReturn = sdb.OutputReturn(returncode=1, output='Issues!!')
        self.setupDB.exec_sql = MagicMock(name='exec_psql_w_f',
                                            return_value=outputReturn)
        with patch('gs.recipe.createtables.setupdb.sys.stdout') as sdb_stdout:
            self.assertRaises(sdb.SetupError, self.setupDB.setup_database,
                              'gs.option', 'eggs/')
            self.exec_sql_test(self.setupDB.exec_sql)

        self.assertEqual(0, sdb_stdout.call_count)

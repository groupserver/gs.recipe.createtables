# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2014 OnlineGroups.net and Contributors.
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
from mock import patch, MagicMock
from unittest import TestCase
import gs.recipe.createtables.setupdb as sdb
UTF8 = 'utf-8'


class TestSetupDB(TestCase):

    def test_get_sql_filenames_from_product(self):
        'Can the system extract the SQL for a product?'
        setupDB = sdb.SetupDB()
        products = 'gs.option\n'
        r = setupDB.get_sql_filenames_from_products(products)
        self.assertEqual(1, len(r))

    def test_get_sql_filenames_from_multiple_products(self):
        'Can the SQL be extracted for multiple products?'
        setupDB = sdb.SetupDB()
        products = 'gs.option\nProducts.GSAuditTrail\n'
        r = setupDB.get_sql_filenames_from_products(products)
        self.assertEqual(2, len(r))

    def test_get_sql_filenames_from_multiple_products_2(self):
        'Do blank lines screw us up?'
        setupDB = sdb.SetupDB()
        products = '\n\ngs.option\n\nProducts.GSAuditTrail\n\n'
        r = setupDB.get_sql_filenames_from_products(products)
        self.assertEqual(2, len(r))

    def test_execute_psql_with_file(self):
        'Can we construct a pipe to psql?'
        with patch('gs.recipe.createtables.setupdb.Popen', autospec=True) as Po:
            instance = Po.return_value
            instance.stdout = MagicMock(name='stdout')
            instance.stdout.read.return_value = 'East Kipling Road'
            instance.wait.return_value = 0

            setupDB = sdb.SetupDB()
            r = setupDB.execute_psql_with_file('fake-user', 'db.example.com',
                                    '5433', 'database', '/tmp/filename.sql')

            # Do we get the return-code from Popen back?
            self.assertEqual(0, r.returncode)
            # Do we get the data from the pipe back?
            self.assertEqual('East Kipling Road', r.output)
            # Did we call psql?
            args, kwargs = Po.call_args
            self.assertEqual('psql', args[0][0])

    def test_setup_database_normal(self):
        setupDB = sdb.SetupDB()
        setupDB.get_sql_filenames_from_products = \
            MagicMock(name='get_sql', return_value=['/tmp/filename.sql'])
        outputReturn = sdb.OutputReturn(returncode=0, output='')
        setupDB.execute_psql_with_file = \
            MagicMock(name='exec_sql', return_value=outputReturn)
        sdb.sys.stdout.write = MagicMock(name='sdb_stdout')

        setupDB.setup_database('fake-user', 'db.example.com', '5433',
                                'database', 'gs.option')

        gsqlf = setupDB.get_sql_filenames_from_products
        gsqlf.assert_called_once_with('gs.option')
        setupDB.execute_psql_with_file.assert_called_once_with('fake-user',
            'db.example.com', '5433', 'database', filename='/tmp/filename.sql')
        sdb.sys.stdout.write.assert_called_once_with('.')

    def test_setup_database_issues(self):
        setupDB = sdb.SetupDB()
        setupDB.get_sql_filenames_from_products = \
            MagicMock(name='get_sql', return_value=['/tmp/filename.sql'])
        outputReturn = sdb.OutputReturn(returncode=1, output='Issues!!')
        setupDB.execute_psql_with_file = \
            MagicMock(name='exec_sql', return_value=outputReturn)
        sdb.sys.stdout.write = MagicMock(name='sdb_stdout')

        self.assertRaises(sdb.SetupError, setupDB.setup_database, 'fake-user',
                            'db.example.com', '5433', 'database', 'gs.option')

        setupDB.execute_psql_with_file.assert_called_once_with('fake-user',
            'db.example.com', '5433', 'database', filename='/tmp/filename.sql')
        self.assertEqual(0, sdb.sys.stdout.write.call_count)

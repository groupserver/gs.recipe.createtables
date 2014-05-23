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
#import codecs
from mock import patch, MagicMock
#import os
#from shutil import rmtree
#from tempfile import mkdtemp
from unittest import TestCase
#from zc.buildout import UserError
import gs.recipe.createtables.setupdb
UTF8 = 'utf-8'


class TestSetupDB(TestCase):

    def test_get_sql_filenames_from_product(self):
        'Can the system extract the SQL for a product?'
        setupDB = gs.recipe.createtables.setupdb.SetupDB()
        products = 'gs.option\n'
        r = setupDB.get_sql_filenames_from_products(products)
        self.assertEqual(1, len(r))

    def test_get_sql_filenames_from_multiple_products(self):
        'Can the SQL be extracted for multiple products?'
        setupDB = gs.recipe.createtables.setupdb.SetupDB()
        products = 'gs.option\nProducts.GSAuditTrail\n'
        r = setupDB.get_sql_filenames_from_products(products)
        self.assertEqual(2, len(r))

    def test_execute_psql_with_file(self):
        'Can we construct a pipe to psql?'
        with patch('gs.recipe.createtables.setupdb.Popen', autospec=True) as Po:
            instance = Po.return_value
            instance.stdout = MagicMock(name='stdout')
            instance.stdout.read.return_value = 'East Kipling Road'
            instance.wait.return_value = 0

            setupDB = gs.recipe.createtables.setupdb.SetupDB()
            r = setupDB.execute_psql_with_file('fake-user', 'db.example.com',
                                    '5433', 'database', '/tmp/filename.sql')

            self.assertEqual(0, r.returncode)
            self.assertEqual('East Kipling Road', r.output)

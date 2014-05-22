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
#from mock import MagicMock, patch
#import os
#from shutil import rmtree
#from tempfile import mkdtemp
from unittest import TestCase
#from zc.buildout import UserError
import gs.recipe.createtables.setupdb
UTF8 = 'utf-8'


class TestSetupDB(TestCase):

    def test_get_sql_filenames_from_products(self):
        setupDB = gs.recipe.createtables.setupdb.SetupDB()
        products = 'gs.option\n'
        r = setupDB.get_sql_filenames_from_products(products)
        self.assertEqual(1, len(r))

    def test_get_sql_filenames_from_multiple_products(self):
        setupDB = gs.recipe.createtables.setupdb.SetupDB()
        products = 'gs.option\nProducts.GSAuditTrail\n'
        r = setupDB.get_sql_filenames_from_products(products)
        self.assertEqual(2, len(r))

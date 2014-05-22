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
import codecs
from mock import MagicMock, patch
import os
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase
from zc.buildout import UserError
import gs.recipe.createtables.recipe
UTF8 = 'utf-8'


class TestRecipe(TestCase):
    'Test the CreateTablesRecipe class'
    def setUp(self):
        self.tempdir = mkdtemp()
        self.bindir = os.path.join(self.tempdir, 'bin')
        os.mkdir(self.bindir)
        vardir = os.path.join(self.tempdir, 'var')
        os.mkdir(vardir)

        self.buildout = {'buildout': {'directory': self.tempdir,
                                        'bin-directory': self.bindir, }, }
        self.options = {}
        self.options['recipe'] = 'gs.recipe.createtables'
        self.options['database_username'] = 'example_db_user'
        self.options['database_host'] = 'db.example.com'
        self.options['database_port'] = '5433'
        self.options['database_name'] = 'example_db'

        #gs.recipe.config.recipe.ConfigCreator.write_token = \
        #    MagicMock(return_value='fake-token')

        gs.recipe.config.recipe.sys.stdout = MagicMock()
        gs.recipe.config.recipe.sys.stderr = MagicMock()

    def tearDown(self):
        rmtree(self.tempdir)
        self.tempdir = self.bindir = None

    def test_error(self):
        'Test an error being raised'
        sdb = gs.recipe.createtables.recipe.SetupDB
        with patch.object(sdb, 'setup_database', autospec=True) as mock_s_db:
            mock_s_db.side_effect = OSError

            recipe = gs.recipe.createtables.recipe.CreateTablesRecipe(
                                        self.buildout, self.name, self.options)
            r = recipe.should_run()
            self.assertTrue(r)
            self.assertRaises(UserError, recipe.install)

            r = recipe.should_run()
            self.assertTrue(r)  # Should not be locked after the raise

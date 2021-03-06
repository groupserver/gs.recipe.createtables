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
import sys
from zc.buildout import UserError
from gs.recipe.base import Recipe
from .setupdb import (SetupDB, SetupError)

# The order of the modules is important
#gs.option
#Products.GSAuditTrail
#gs.profile.email.base
#gs.profile.email.verify
#gs.profile.password
#Products.CustomUserFolder
#gs.group.messages.post
#gs.group.messages.topic
#Products.XWFMailingListManager
#gs.group.member.invite.base
#gs.group.member.request
#Products.GSGroupMember


class CreateTablesRecipe(Recipe):
    def install(self):
        """Installer"""
        if self.should_run():
            tableCreator = SetupDB(self.options['database_username'],
                                    self.options['database_password'],
                                    self.options['database_host'],
                                    self.options['database_port'],
                                    self.options['database_name'])
            try:
                products = self.options['products']
                eggsDir = self.buildout['buildout']['eggs-directory']
                tableCreator.setup_database(products, eggsDir)
            except (OSError, ImportError, SetupError) as e:
                m = '{0} Issue setting up the database tables\n{1}\n\n'
                msg = m.format(self.name, e)
                raise UserError(msg)
            else:
                self.mark_locked()
                sys.stdout.write('\nTables created\n\n')
        return tuple()

    def update(self):
        """Updater"""
        self.install()

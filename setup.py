# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013, 2014 OnlineGroups.net and Contributors.
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
import codecs
import os
from setuptools import setup, find_packages
from version import get_version

version = get_version()

with codecs.open('README.txt', encoding='utf-8') as f:
    long_description = f.read()
with codecs.open(os.path.join("docs", "HISTORY.txt"), encoding='utf-8') as f:
    long_description += '\n' + f.read()

entry_point = 'gs.recipe.createtables.recipe:CreateTablesRecipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

setup(name='gs.recipe.createtables',
      version=version,
      description="Setup the GroupServer SQL tables in PostgreSQL",
      long_description=long_description,
      classifiers=[
        "Development Status :: 4 - Beta",
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Zope Public License',
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
      ],
      keywords='groupserver, recipe, setup, database, table',
      author='Michael JasonSmith',
      author_email='mpj17@onlinegroups.net',
      url='',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['gs', 'gs.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'zc.buildout',
        'gs.group.member.invite.base',
        'gs.group.member.request',
        'gs.group.messages.post',
        'gs.group.messages.topic',
        'gs.option',
        'gs.profile.email.base',
        'gs.profile.email.verify',
        'gs.profile.password',
        'Products.CustomUserFolder',
        'Products.GroupServer',
        'Products.GSAuditTrail',
        'Products.GSGroupMember',
        'Products.XWFMailingListManager', ],
      entry_points=entry_points,
      )

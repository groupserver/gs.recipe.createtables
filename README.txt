==========================
``gs.recipe.createtables``
==========================
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A ``zc.buildout`` recipe to add SQL tables for GroupServer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2014-05-22
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 4.0 International License`_
  by `OnlineGroups.net`_.

Introduction
============

This product provides a ``zc.buildout`` recipe_ for creating the
default SQL tables required by GroupServer_.

Recipe
======

Calling the recipe is done by ``buildout``. It is configured like
other ``zc.buildout`` recipes::

  [create-tables]
  recipe = gs.recipe.createtables
  database_username = postgresql_db_user
  database_host = localhost
  database_port = 5433
  database_name = groupserver
  products = 
     gs.option
     Products.GSAuditTrail
     gs.profile.email.base
     gs.profile.email.verify
     gs.profile.password
     Products.CustomUserFolder
     gs.group.messages.post
     gs.group.messages.topic
     Products.XWFMailingListManager
     gs.group.member.invite.base
     gs.group.member.request
     Products.GSGroupMember

Parameters
----------

Five values must be provided to the recipe.

``database_username``:
  The name of the PostgreSQL user.

``database_host``:
  The host-name of the machine that runs PostgreSQL.

``database_port``: 
  The port that PostgreSQL is listening to on.

``database_name``:
  The name of the PostgreSQL database.

``products``:
  The products that contain the SQL files that, in turn, define
  the tables.

When the recipe is run it will load each product listed in
``products``, and run PostgreSQL passing all the ``*.sql`` files
in the ``sql`` directory in each product. For example, in the
case of ``gs.option`` there is one SQL file in
``gs.option/gs/option/sql/01-option.sql``.

Lock file
---------

To prevent the recipe from being run more than once a *lock file*
is created, ``var/create-tables.cfg``, within the GroupServer
installation directory. (The name is actually taken from the name
of the section in the configuration file.)

Resources
=========

- Code repository: https://source.iopen.net/groupserver/gs.recipe.createtables
- Questions and comments to http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
..  _Creative Commons Attribution-Share Alike 4.0 International License:
    http://creativecommons.org/licenses/by-sa/4.0/


..  LocalWords:  SQL sql createtables cfg buildout username
..  LocalWords:  postgresql localhost GSAuditTrail GSGroupMember
..  LocalWords:  CustomUserFolder XWFMailingListManager

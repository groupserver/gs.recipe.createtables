# -*- coding: utf-8 -*-
from glob import glob
import os
from subprocess import Popen, PIPE, STDOUT
import sys

#lint:disable
import gs.group.member.invite.base, gs.group.member.request, \
    gs.group.messages.post, gs.group.messages.topic,\
    gs.option, gs.profile.email.base, gs.profile.email.verify,\
    gs.profile.password, Products.CustomUserFolder, Products.GSAuditTrail,\
    Products.GSGroupMember, Products.XWFMailingListManager
#lint:enable


class SetupError(Exception):

    def __init__(self, e):
        super(SetupError, self).__init__(e)


class SetupDB(object):

    def setup_database(self, user, host, port, database):
        # The order of the modules is important.
        modules = (gs.option,
                   Products.GSAuditTrail,
                   gs.profile.email.base,
                   gs.profile.email.verify,
                   gs.profile.password,
                   Products.CustomUserFolder,
                   gs.group.messages.post,
                   gs.group.messages.topic,
                   Products.XWFMailingListManager,
                   gs.group.member.invite.base,
                   gs.group.member.request,
                   Products.GSGroupMember)

        for module in modules:
            for fname in self.get_sql_filenames_from_module(module):
                s, o = self.execute_psql_with_file(user, host, port, database,
                                                    fname)
                m = (o and o) or '.'
                if s == 0:
                    sys.stdout.write(m)
                else:
                    raise SetupError(m)

    def get_sql_filenames_from_module(self, module):
        path = os.path.join(os.path.join(*module.__path__), 'sql')
        retval = glob(os.path.join(path, '*sql'))
        retval.sort()
        assert type(retval) == list
        return retval

    def execute_psql_with_file(self, user, host, port, database, filename):
        # We pass the -w option to psql because we trust that the
        # gs_install_ubuntu.sh script has set up the PGPASSFILE environment
        # variable.
        cmd = ['psql', '-w', '-U', user, '-h', host, '-p', port,
                        '-d', database, '-f', filename]
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT)
        p.wait()
        output = p.stdout.read()
        retval = (p.returncode, output)
        return retval

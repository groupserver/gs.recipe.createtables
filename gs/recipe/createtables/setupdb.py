# -*- coding: utf-8 -*-
import commands
from glob import glob
import os
import gs.group.member.invite.base, gs.group.member.request, \
    gs.group.messages.post, gs.group.messages.topic,\
    gs.option, gs.profile.email.base, gs.profile.email.verify,\
    gs.profile.password, Products.CustomUserFolder, Products.GSAuditTrail,\
    Products.GSGroupMember, Products.XWFMailingListManager

class SetupDB(object):
    def setup_database(self, user, password, host, port, database):
        # The order of the modules is important.
        modules = (gs.option,
                   gs.profile.email.base,
                   Products.CustomUserFolder,
                   gs.group.messages.post,
                   gs.group.messages.topic,
                   Products.XWFMailingListManager,
                   Products.GSAuditTrail,
                   gs.group.member.invite.base,
                   gs.group.member.request,
                   gs.profile.password,
                   gs.profile.email.verify,
                   Products.GSGroupMember)

        for module in modules:
            for fname in self.get_sql_filenames_from_module(module):
                s,o = execute_psql_with_file(user, host, port, database, 
                    fname)
                print ((o and o) or '.')

    def get_sql_filenames_from_module(self, module):
        path = os.path.join(os.path.join(*module.__path__), 'sql')
        retval = glob(os.path.join(path, '*sql'))
        retval.sort()
        assert type(retval) == list
        return retval
    
    def execute_psql_with_file(self, user, host, port, database, filename):
        cmd = 'psql -U %s -h %s -p %s -d %s -f %s' % (user, host, port,
                                                      database, filename)
        status, output = commands.getstatusoutput(cmd)
        return (status, output)

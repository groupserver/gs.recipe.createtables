# -*- coding: utf-8 -*-
import os
import sys
from setupdb import SetupDB

class Recipe(object):
    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

        # suppress script generation
        self.options['scripts'] = ''
        options['bin-directory'] = buildout['buildout']['bin-directory']

    def runonce(self)
        runonce = 'run-once' in self.options and \
                   self.options['run-once'].lower() or 'true'
        #We'll use the existance of this file as flag for the run-once option
        file_name = os.path.join(self.buildout['buildout']['directory'],
                                 'var', "%s.cfg" % self.name)

        if runonce not in ['false', 'off', 'no']:
            if os.path.exists(file_name):
                m = '''
************************************************
Skipped: [%s] has already been run
If you want to run it again set the run-once option
to false or delete "%s"
************************************************
''' % (self.name, file_name)
                sys.stdout.write(m)
                sys.exit(0)
            else:
                file(file_name, 'w').write('1')

    def install(self):
        """Installer"""
        self.runonce()
        tableCreator = SetupDB()
        tableCreator.setup_datbase(self.options['database_username'],
                                   self.options['database_password'],
                                   self.options['database_host'], 
                                   self.options['database_port'], 
                                   self.options['database_name'])
        return tuple()

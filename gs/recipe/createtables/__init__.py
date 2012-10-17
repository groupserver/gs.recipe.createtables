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

    def should_run(self):
        runonce = ((('run-once' in self.options)
                    and self.options['run-once'].lower()) or 'true')
        retval = True  # Uncharactistic optomisim
        if runonce not in ['false', 'off', 'no']:
            # The existance of this file is flag for the run-once option
            file_name = os.path.join(self.buildout['buildout']['directory'],
                                     'var', "%s.cfg" % self.name)
            if os.path.exists(file_name):
                m = '''
************************************************
Skipped: The setup script [%s] has already been run
If you want to run it again set the run-once option
to false or delete "%s"
************************************************\n''' % (self.name, file_name)
                sys.stdout.write(m)
                retval = False
            else:
                file(file_name, 'w').write('1')
        return retval

    def install(self):
        """Installer"""
        if not (self.should_run()):
            tableCreator = SetupDB()
            tableCreator.setup_database(self.options['database_username'],
                                        self.options['database_host'],
                                        self.options['database_port'],
                                        self.options['database_name'])
            sys.stdout.write('\nTables created\n')
        return tuple()

    def update(self):
        """Updater"""
        self.install()

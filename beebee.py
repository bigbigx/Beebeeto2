#!/usr/bin/env python
# coding=utf-8

# Author: www.webhhh.net
# Create: 2014-10-15
# Team: FF0000 TeAm <http://www.ff0000.cc>

import sys
import traceback
import logging

from pprint import pprint
from optparse import OptionParser, OptionGroup
from beeplugins import BeePlugins
from util import logset



BEEBEETO_STATEMENT = \
    "This POC is created for security research. "\
    "It cannot be used in illegal ways, the user should be responsible for the usage of it."\
    "All Rights Reserved by BeeBeeTo.com."



class BeeBee(object):
    poc_info = {
        # id/name to be edit by BeeBeeto
        'poc': {
            'id': None,
            'name': None,
            'author': 'Beebeeto',
            'create_date': '2014-07-15',
        },
        # to be edit by you
        'protocol': {
            'name': None,  # 'openssl' e.g.
            'port': None,  # must be int type, 443 e.g.
            'layer3_protocol': ['tcp'],
        },
        # to be edit by you
        'vul': {
            'app_name': None,
            'vul_version': None,
            'type': None,
            'tag': [],
            'desc': None,
            'references': [],
        },
    }

    def __init__(self, run_in_shell=True):
        if run_in_shell:
            self._parse_cmd()
        self.run_in_shell = run_in_shell


    def _parse_cmd(self):
        usage = 'usage: %prog [options] arg1 arg2'
        self.base_parser = OptionParser(usage=usage, description=BEEBEETO_STATEMENT)
        self.user_parser = OptionGroup(self.base_parser,
                                       title='POC Specified Options',
                                       description='These options are specified by the author'
                                                   ' of this poc, so they are available'
                                                   ' only in this poc.')
        self.base_parser.add_option_group(self.user_parser)
        self.__init_base_parser()
        self._init_user_parser()

        (self.options, self.args) = self.base_parser.parse_args()
        if self.options.update:
            self._update_poc()
            sys.exit()
 
        if not self.options.target:
            print '\n[*] No target input!\n'
            self.base_parser.print_help()
            sys.exit()

    def __init_base_parser(self):
        self.base_parser.add_option('-t', '--target', action='store', dest='target',
                                    default=None, help='the target to be checked by this poc.')
        self.base_parser.add_option('-v', '--verify',
                                    action='store_true', dest='verify', default=True,
                                    help='run poc in verify mode.')
        self.base_parser.add_option('-e', '--exploit',
                                    action='store_false', dest='verify',
                                    help='run poc in exploit mode.')
        self.base_parser.add_option('--verbose', action='store_true', dest='verbose',
                                    default=False, help='print debug debug information.')
        self.base_parser.add_option('--info', action='callback', callback=self.__cb_print_poc_info,
                                    help='print poc information.')
        self.base_parser.add_option('-n', '--name', action='store', dest='name',
                                    default=None, help='use the name to filter the poc.')
        self.base_parser.add_option('-d', '--debug', action='store_true', dest='debug',
                                    default=False, help='print debug debug information.')
        self.base_parser.add_option('--update', action='store', dest='update',
                                    default=None, help='update the poc.')


    def _update_poc(self): 
        update.g_cookie = self.options.update
        update.main()
        return

    def _init_user_parser(self):
        #self.user_parser.add_option('-x', help='example')
        pass

    def __cb_print_poc_info(self, option, opt, value, parser):
        pprint(self.poc_info, stream=None, indent=2, width=80, depth=None)
        sys.exit()

    def __normalize_target(self, target):
        if self.poc_info['protocol']['name'] == 'http':
            return http.normalize_url(target)
        elif self.poc_info['protocol']['name'] == 'https':
            return http.normalize_url(target, https=True)
        else:
            return target

    def run(self, options=None):
        options = self.options.__dict__ if self.run_in_shell else options
        options['target'] = self.__normalize_target(options['target'])
        args = {
            'options': options,
            'success': False,
            'poc_ret': {},
        }

        bp = BeePlugins()
        nameinfo =  options['name']
        if  ".py" in nameinfo:
            bp.add_plugin(nameinfo[:nameinfo.rfind(".")])
        else:
            bp.add_plugin(None, nameinfo)

        for plugin in bp.get_plugin_list():
            result = {}
            args['success'] = False
            args['poc_ret'] = {}

            try:
                if options['verify']:
                    fun = getattr(plugin, 'verify')
                    args = fun(args)
                else:
                    fun = getattr(plugin, 'exploit')
                    args = fun(args)
                result.update(args)
            except Exception, err:
                if options['verbose']:
                    traceback.print_exc()
                    sys.exit()
                result.update(args)
                result['exception'] = str(err)

            # print debug info
            if options['debug']: 
                pprint(result)
            else: 
                print(" [+] %-50s %s" % (plugin.__module__, result['success']))
            
            # write log
            logging.info(result)

if __name__ == '__main__':
    from pprint import pprint

    bf = BeeBee()
    bf.run()

#!/usr/bin/env python
#
###############################################################################
#   Copyright (C) 2016-2018 Cortney T. Buffington, N0MJS <n0mjs@me.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
###############################################################################

'''
This module generates the configuration data structure for hblink.py and
assoicated programs that use it. It has been seaparated into a different
module so as to keep hblink.py easeier to navigate. This file only needs
updated if the items in the main configuraiton file (usually hblink.cfg)
change.
'''

import configparser
import sys
import os
import const

from socket import gethostbyname, gaierror

# Does anybody read this stuff? There's a PEP somewhere that says I should do this.
__author__     = 'Cortney T. Buffington, N0MJS'
__copyright__  = 'Copyright (c) 2016-2018 Cortney T. Buffington, N0MJS and the K0USY Group'
__credits__    = 'Colin Durbridge, G4EML, Steve Zingman, N4IRS; Mike Zingman, N4IRR; Jonathan Naylor, G4KLX; Hans Barthen, DL5DI; Torsten Shultze, DG1HT'
__license__    = 'GNU GPLv3'
__maintainer__ = 'Cort Buffington, N0MJS'
__email__      = 'n0mjs@me.com'

# Processing of ALS goes here. It's separated from the acl_build function because this
# code is hblink config-file format specific, and acl_build is abstracted
def process_acls(_config):
    # Global registration ACL
    _config['GLOBAL']['REG_ACL'] = acl_build(_config['GLOBAL']['REG_ACL'], const.PEER_MAX)

    # Global subscriber and TGID ACLs
    for acl in ['SUB_ACL', 'TG1_ACL', 'TG2_ACL']:
        _config['GLOBAL'][acl] = acl_build(_config['GLOBAL'][acl], const.ID_MAX)

    # System level ACLs
    for system in _config['SYSTEMS']:
        # Registration ACLs (which make no sense for peer systems)
        if _config['SYSTEMS'][system]['MODE'] == 'MASTER':
            _config['SYSTEMS'][system]['REG_ACL'] = acl_build(_config['SYSTEMS'][system]['REG_ACL'], const.PEER_MAX)

        # Subscriber and TGID ACLs (valid for all system types)
        for acl in ['SUB_ACL', 'TG1_ACL', 'TG2_ACL']:
            _config['SYSTEMS'][system][acl] = acl_build(_config['SYSTEMS'][system][acl], const.ID_MAX)

# Create an access control list that is programatically useable from human readable:
# ORIGINAL:  'DENY:1-5,3120101,3120124'
# PROCESSED: (False, set([(1, 5), (3120124, 3120124), (3120101, 3120101)]))
def acl_build(_acl, _max):
    if not _acl:
        return(True, set((const.ID_MIN, _max)))

    acl = [] #set()
    sections = _acl.split(':')

    if sections[0] == 'PERMIT':
        action = True
    else:
        action = False

    for entry in sections[1].split(','):
        if entry == 'ALL':
            acl.append((const.ID_MIN, _max))
            break

        elif '-' in entry:
            start,end = entry.split('-')
            start,end = int(start), int(end)
            if (const.ID_MIN <= start <= _max) or (const.ID_MIN <= end <= _max):
                acl.append((start, end))
            else:
                sys.exit('ACL CREATION ERROR, VALUE OUT OF RANGE ({} - {}) IN RANGE-BASED ENTRY: {}'.format(const.ID_MIN, _max, entry))
        else:
            id = int(entry)
            if (const.ID_MIN <= id <= _max):
                acl.append((id, id))
            else:
                 sys.exit('ACL CREATION ERROR, VALUE OUT OF RANGE ({} - {}) IN SINGLE ID ENTRY: {}'.format(const.ID_MIN, _max, entry))

    return (action, acl)

def _validate_port(port, section):
    if not (1 <= port <= 65535):
        sys.exit('CONFIG ERROR in [{}]: PORT {} is out of valid range (1-65535)'.format(section, port))

def _validate_radio_id(radio_id, section):
    if not (const.ID_MIN <= radio_id <= const.ID_MAX):
        sys.exit('CONFIG ERROR in [{}]: RADIO_ID {} is out of valid range ({}-{})'.format(section, radio_id, const.ID_MIN, const.ID_MAX))

def _validate_log_path(log_file):
    if log_file and log_file != '/dev/null':
        log_dir = os.path.dirname(os.path.abspath(log_file))
        if not os.path.isdir(log_dir):
            sys.exit('CONFIG ERROR in [LOGGER]: LOG_FILE directory does not exist: {}'.format(log_dir))

def _resolve_hostname(hostname, section):
    try:
        return gethostbyname(hostname)
    except gaierror as err:
        sys.exit('CONFIG ERROR in [{}]: Cannot resolve hostname \'{}\': {}'.format(section, hostname, err))

def build_config(_config_file):
    config = configparser.ConfigParser()

    if not config.read(_config_file):
        sys.exit('Configuration file \''+_config_file+'\' is not a valid configuration file! Exiting...')        

    CONFIG = {}
    CONFIG['GLOBAL'] = {}
    CONFIG['REPORTS'] = {}
    CONFIG['LOGGER'] = {}
    CONFIG['ALIASES'] = {}
    CONFIG['SYSTEMS'] = {}

    try:
        for section in config.sections():
            if section == 'GLOBAL':
                CONFIG['GLOBAL'].update({
                    'PATH': config.get(section, 'PATH'),
                    'PING_TIME': config.getint(section, 'PING_TIME'),
                    'MAX_MISSED': config.getint(section, 'MAX_MISSED'),
                    'USE_ACL': config.get(section, 'USE_ACL'),
                    'REG_ACL': config.get(section, 'REG_ACL'),
                    'SUB_ACL': config.get(section, 'SUB_ACL'),
                    'TG1_ACL': config.get(section, 'TGID_TS1_ACL'),
                    'TG2_ACL': config.get(section, 'TGID_TS2_ACL')
                })

            elif section == 'REPORTS':
                CONFIG['REPORTS'].update({
                    'REPORT': config.getboolean(section, 'REPORT'),
                    'REPORT_INTERVAL': config.getint(section, 'REPORT_INTERVAL'),
                    'REPORT_PORT': config.getint(section, 'REPORT_PORT'),
                    'REPORT_CLIENTS': config.get(section, 'REPORT_CLIENTS').split(',')
                })

            elif section == 'LOGGER':
                CONFIG['LOGGER'].update({
                    'LOG_FILE': config.get(section, 'LOG_FILE'),
                    'LOG_HANDLERS': config.get(section, 'LOG_HANDLERS'),
                    'LOG_LEVEL': config.get(section, 'LOG_LEVEL'),
                    'LOG_NAME': config.get(section, 'LOG_NAME')
                })
                if not CONFIG['LOGGER']['LOG_FILE']:
                    CONFIG['LOGGER']['LOG_FILE'] = '/dev/null'

            elif section == 'ALIASES':
                CONFIG['ALIASES'].update({
                    'TRY_DOWNLOAD': config.getboolean(section, 'TRY_DOWNLOAD'),
                    'PATH': config.get(section, 'PATH'),
                    'PEER_FILE': config.get(section, 'PEER_FILE'),
                    'SUBSCRIBER_FILE': config.get(section, 'SUBSCRIBER_FILE'),
                    'TGID_FILE': config.get(section, 'TGID_FILE'),
                    'PEER_URL': config.get(section, 'PEER_URL'),
                    'SUBSCRIBER_URL': config.get(section, 'SUBSCRIBER_URL'),
                    'STALE_TIME': config.getint(section, 'STALE_DAYS') * 86400,
                })

            elif config.getboolean(section, 'ENABLED'):
                if config.get(section, 'MODE') == 'PEER':
                    CONFIG['SYSTEMS'].update({section: {
                        'MODE': config.get(section, 'MODE'),
                        'ENABLED': config.getboolean(section, 'ENABLED'),
                        'LOOSE': config.getboolean(section, 'LOOSE'),
                        'SOCK_ADDR': (_resolve_hostname(config.get(section, 'IP'), section), config.getint(section, 'PORT')),
                        'IP': _resolve_hostname(config.get(section, 'IP'), section),
                        'PORT': config.getint(section, 'PORT'),
                        'MASTER_SOCKADDR': (_resolve_hostname(config.get(section, 'MASTER_IP'), section), config.getint(section, 'MASTER_PORT')),
                        'MASTER_IP': _resolve_hostname(config.get(section, 'MASTER_IP'), section),
                        'MASTER_PORT': config.getint(section, 'MASTER_PORT'),
                        'PASSPHRASE': bytes(config.get(section, 'PASSPHRASE'), 'utf-8'),
                        'CALLSIGN': bytes(config.get(section, 'CALLSIGN').ljust(8)[:8], 'utf-8'),
                        'RADIO_ID': config.getint(section, 'RADIO_ID').to_bytes(4, 'big'),
                        'RX_FREQ': bytes(config.get(section, 'RX_FREQ').ljust(9)[:9], 'utf-8'),
                        'TX_FREQ': bytes(config.get(section, 'TX_FREQ').ljust(9)[:9], 'utf-8'),
                        'TX_POWER': bytes(config.get(section, 'TX_POWER').rjust(2,'0'), 'utf-8'),
                        'COLORCODE': bytes(config.get(section, 'COLORCODE').rjust(2,'0'), 'utf-8'),
                        'LATITUDE': bytes(config.get(section, 'LATITUDE').ljust(8)[:8], 'utf-8'),
                        'LONGITUDE': bytes(config.get(section, 'LONGITUDE').ljust(9)[:9], 'utf-8'),
                        'HEIGHT': bytes(config.get(section, 'HEIGHT').rjust(3,'0'), 'utf-8'),
                        'LOCATION': bytes(config.get(section, 'LOCATION').ljust(20)[:20], 'utf-8'),
                        'DESCRIPTION': bytes(config.get(section, 'DESCRIPTION').ljust(19)[:19], 'utf-8'),
                        'SLOTS': bytes(config.get(section, 'SLOTS'), 'utf-8'),
                        'URL': bytes(config.get(section, 'URL').ljust(124)[:124], 'utf-8'),
                        'SOFTWARE_ID': bytes(config.get(section, 'SOFTWARE_ID').ljust(40)[:40], 'utf-8'),
                        'PACKAGE_ID': bytes(config.get(section, 'PACKAGE_ID').ljust(40)[:40], 'utf-8'),
                        'GROUP_HANGTIME': config.getint(section, 'GROUP_HANGTIME'),
                        'OPTIONS': b''.join([b'Type=HBlink;', bytes(config.get(section, 'OPTIONS'), 'utf-8')]),
                        'USE_ACL': config.getboolean(section, 'USE_ACL'),
                        'SUB_ACL': config.get(section, 'SUB_ACL'),
                        'TG1_ACL': config.get(section, 'TGID_TS1_ACL'),
                        'TG2_ACL': config.get(section, 'TGID_TS2_ACL')
                    }})
                    CONFIG['SYSTEMS'][section].update({'STATS': {
                        'CONNECTION': 'NO',             # NO, RTPL_SENT, AUTHENTICATED, CONFIG-SENT, YES 
                        'CONNECTED': None,
                        'PINGS_SENT': 0,
                        'PINGS_ACKD': 0,
                        'NUM_OUTSTANDING': 0,
                        'PING_OUTSTANDING': False,
                        'LAST_PING_TX_TIME': 0,
                        'LAST_PING_ACK_TIME': 0,
                    }})

                if config.get(section, 'MODE') == 'XLXPEER':
                    CONFIG['SYSTEMS'].update({section: {
                        'MODE': config.get(section, 'MODE'),
                        'ENABLED': config.getboolean(section, 'ENABLED'),
                        'LOOSE': config.getboolean(section, 'LOOSE'),
                        'SOCK_ADDR': (_resolve_hostname(config.get(section, 'IP'), section), config.getint(section, 'PORT')),
                        'IP': _resolve_hostname(config.get(section, 'IP'), section),
                        'PORT': config.getint(section, 'PORT'),
                        'MASTER_SOCKADDR': (_resolve_hostname(config.get(section, 'MASTER_IP'), section), config.getint(section, 'MASTER_PORT')),
                        'MASTER_IP': _resolve_hostname(config.get(section, 'MASTER_IP'), section),
                        'MASTER_PORT': config.getint(section, 'MASTER_PORT'),
                        'PASSPHRASE': bytes(config.get(section, 'PASSPHRASE'), 'utf-8'),
                        'CALLSIGN': bytes(config.get(section, 'CALLSIGN').ljust(8)[:8], 'utf-8'),
                        'RADIO_ID': config.getint(section, 'RADIO_ID').to_bytes(4, 'big'),
                        'RX_FREQ': bytes(config.get(section, 'RX_FREQ').ljust(9)[:9], 'utf-8'),
                        'TX_FREQ': bytes(config.get(section, 'TX_FREQ').ljust(9)[:9], 'utf-8'),
                        'TX_POWER': bytes(config.get(section, 'TX_POWER').rjust(2,'0'), 'utf-8'),
                        'COLORCODE': bytes(config.get(section, 'COLORCODE').rjust(2,'0'), 'utf-8'),
                        'LATITUDE': bytes(config.get(section, 'LATITUDE').ljust(8)[:8], 'utf-8'),
                        'LONGITUDE': bytes(config.get(section, 'LONGITUDE').ljust(9)[:9], 'utf-8'),
                        'HEIGHT': bytes(config.get(section, 'HEIGHT').rjust(3,'0'), 'utf-8'),
                        'LOCATION': bytes(config.get(section, 'LOCATION').ljust(20)[:20], 'utf-8'),
                        'DESCRIPTION': bytes(config.get(section, 'DESCRIPTION').ljust(19)[:19], 'utf-8'),
                        'SLOTS': bytes(config.get(section, 'SLOTS'), 'utf-8'),
                        'URL': bytes(config.get(section, 'URL').ljust(124)[:124], 'utf-8'),
                        'SOFTWARE_ID': bytes(config.get(section, 'SOFTWARE_ID').ljust(40)[:40], 'utf-8'),
                        'PACKAGE_ID': bytes(config.get(section, 'PACKAGE_ID').ljust(40)[:40], 'utf-8'),
                        'GROUP_HANGTIME': config.getint(section, 'GROUP_HANGTIME'),
                        'XLXMODULE': config.getint(section, 'XLXMODULE'),
                        'OPTIONS': '',
                        'USE_ACL': config.getboolean(section, 'USE_ACL'),
                        'SUB_ACL': config.get(section, 'SUB_ACL'),
                        'TG1_ACL': config.get(section, 'TGID_TS1_ACL'),
                        'TG2_ACL': config.get(section, 'TGID_TS2_ACL')
                    }})
                    CONFIG['SYSTEMS'][section].update({'XLXSTATS': {
                        'CONNECTION': 'NO',             # NO, RTPL_SENT, AUTHENTICATED, CONFIG-SENT, YES 
                        'CONNECTED': None,
                        'PINGS_SENT': 0,
                        'PINGS_ACKD': 0,
                        'NUM_OUTSTANDING': 0,
                        'PING_OUTSTANDING': False,
                        'LAST_PING_TX_TIME': 0,
                        'LAST_PING_ACK_TIME': 0,
                    }})

                elif config.get(section, 'MODE') == 'MASTER':
                    CONFIG['SYSTEMS'].update({section: {
                        'MODE': config.get(section, 'MODE'),
                        'ENABLED': config.getboolean(section, 'ENABLED'),
                        'REPEAT': config.getboolean(section, 'REPEAT'),
                        'MAX_PEERS': config.getint(section, 'MAX_PEERS'),
                        'IP': _resolve_hostname(config.get(section, 'IP'), section),
                        'PORT': config.getint(section, 'PORT'),
                        'PASSPHRASE': bytes(config.get(section, 'PASSPHRASE'), 'utf-8'),
                        'GROUP_HANGTIME': config.getint(section, 'GROUP_HANGTIME'),
                        'USE_ACL': config.getboolean(section, 'USE_ACL'),
                        'REG_ACL': config.get(section, 'REG_ACL'),
                        'SUB_ACL': config.get(section, 'SUB_ACL'),
                        'TG1_ACL': config.get(section, 'TGID_TS1_ACL'),
                        'TG2_ACL': config.get(section, 'TGID_TS2_ACL')
                    }})
                    CONFIG['SYSTEMS'][section].update({'PEERS': {}})
                    
                elif config.get(section, 'MODE') == 'OPENBRIDGE':
                    CONFIG['SYSTEMS'].update({section: {
                        'MODE': config.get(section, 'MODE'),
                        'ENABLED': config.getboolean(section, 'ENABLED'),
                        'NETWORK_ID': config.getint(section, 'NETWORK_ID').to_bytes(4, 'big'),
                        'IP': _resolve_hostname(config.get(section, 'IP'), section),
                        'PORT': config.getint(section, 'PORT'),
                        'PASSPHRASE': bytes(config.get(section, 'PASSPHRASE').ljust(20,'\x00')[:20], 'utf-8'),
                        'TARGET_SOCK': (_resolve_hostname(config.get(section, 'TARGET_IP'), section), config.getint(section, 'TARGET_PORT')),
                        'TARGET_IP': _resolve_hostname(config.get(section, 'TARGET_IP'), section),
                        'TARGET_PORT': config.getint(section, 'TARGET_PORT'),
                        'BOTH_SLOTS': config.getboolean(section, 'BOTH_SLOTS'),
                        'USE_ACL': config.getboolean(section, 'USE_ACL'),
                        'SUB_ACL': config.get(section, 'SUB_ACL'),
                        'TG1_ACL': config.get(section, 'TGID_ACL'),
                        'TG2_ACL': 'PERMIT:ALL'
                    }})
                    
    
    except configparser.Error as err:
        sys.exit('Error processing configuration file -- {}'.format(err))

    # Validate critical configuration values
    _validate_log_path(CONFIG['LOGGER'].get('LOG_FILE', ''))

    if 'REPORTS' in CONFIG and CONFIG['REPORTS'].get('REPORT'):
        _validate_port(CONFIG['REPORTS']['REPORT_PORT'], 'REPORTS')

    for system in CONFIG['SYSTEMS']:
        _sys = CONFIG['SYSTEMS'][system]
        _validate_port(_sys['PORT'], system)
        if _sys['MODE'] in ('PEER', 'XLXPEER'):
            _validate_port(_sys['MASTER_PORT'], system)
            _validate_radio_id(int.from_bytes(_sys['RADIO_ID'], 'big'), system)
        elif _sys['MODE'] == 'OPENBRIDGE':
            _validate_port(_sys['TARGET_PORT'], system)

    process_acls(CONFIG)
    
    return CONFIG

# Used to run this file direclty and print the config,
# which might be useful for debugging
if __name__ == '__main__':
    import sys
    import os
    import argparse
    from pprint import pprint
    from dmr_utils3.utils import int_id
    
    # Change the current directory to the location of the application
    os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))

    # CLI argument parser - handles picking up the config file from the command line, and sending a "help" message
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', action='store', dest='CONFIG_FILE', help='/full/path/to/config.file (usually hblink.cfg)')
    cli_args = parser.parse_args()


    # Ensure we have a path for the config file, if one wasn't specified, then use the execution directory
    if not cli_args.CONFIG_FILE:
        cli_args.CONFIG_FILE = os.path.dirname(os.path.abspath(__file__))+'/hblink.cfg'
    
    CONFIG = build_config(cli_args.CONFIG_FILE)
    pprint(CONFIG)
    
    def acl_check(_id, _acl):
        id = int_id(_id)
        for entry in _acl[1]:
            if entry[0] <= id <= entry[1]:
                return _acl[0]
        return not _acl[0]
        
    print(acl_check(b'\x00\x01\x37', CONFIG['GLOBAL']['TG1_ACL']))

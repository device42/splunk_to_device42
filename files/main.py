#! /usr/bin/env python

import ConfigParser
import os
import sys

import splunklib.client as client
import splunklib.results as results

from util_uploader import Rest


class Device42():
    """
    Wrapper around util_uploader.py (code that actually uploads data to Device42).
    """
    def __init__(self, url, user, pwd, debug, verbose, dry_run, logger):
        self.rest   = Rest(url, user, pwd, debug, verbose, dry_run, logger)
        self.debug  = debug
        self.logger = logger

    def upload_device(self, data):
        try:
            self.rest.post_device(data)
        except Exception as e:
            if self.debug:
                self.logger.exception(e)

    def upload_ip(self, data):
        try:
            self.rest.post_ip(data)
        except Exception as e:
            if self.debug:
                self.logger.exception(e)

    def upload_mac(self, data):
        try:
            self.rest.post_mac(data)
        except Exception as e:
            if self.debug:
                self.logger.exception(e)


class Mapper():
    """
    Read app_mapper.cfg file, clean up data obtained from Splunk, map parameter names to Device42 parameter names,
    format the data as Device42 likes it.
    """
    def __init__(self, APP_MAPPER):
        """
        init
        :return:
        """
        self.config     = APP_MAPPER
        self.mapping    = {}
        self.d42_params = []
        self.data       = {}

    def populate_map(self):
        """
        Read app_mapper.cfg and create mapping (dict) between custom Splunk params and Device42 params
        :return:
        """
        with open(self.config)  as f:
            raw = f.readlines()
        for word in raw:
            word = word.strip()
            if word and not word.startswith('#'):
                d42, splunk = word.split()
                self.mapping.update({splunk:d42})
                self.d42_params.append(d42)

    def set_data(self, **kwargs):
        """
        Read kwargs from Splunk and if they exist in Splunk to Device42 mapping created in populate_map(),
        convert Splunk custom param into Device42 parameter.
        :param kwargs: Custom Splunk params
        :return:
        """
        self.data.clear()
        for key, value in kwargs.iteritems():
            if key in self.mapping:
                d42_key = self.mapping[key]
                value = self.clean_data(d42_key, value)
                self.data.update({d42_key:value})
            elif key in self.d42_params:
                d42_key = key
                value = self.clean_data(d42_key, value)
                self.data.update({d42_key:value})


    def clean_data(self, key, value):
        """
        Remove alpha from values that should be int or float
        :param key: parameter name
        :param value: parameter value
        :return: int or float
        """
        int_params = ['cpupower', 'hddsize', 'cpucount', 'memory', 'cpucore', 'hddcount']
        if not key in int_params:
            return value
        else:
            if (isinstance(value, int)):
                return value
            elif (isinstance(value, float)):
                return value
            else:
                word  = []
                list_ = list(value)
                for char in list_:
                    if char == '.':
                        word.append(char)
                    else:
                        try:
                            int(char)
                            word.append(char)
                        except:
                            pass
                if '.' in word:
                    return int(float(''.join(word)) * 1000)
                else:
                    if word:
                        return int(''.join(word))

    def d42_formatter(self):
        """
        Format data to be compliant with Device42 API
        :return: dict containing dev, ip and mac params and values
        """
        all_data = {}
        dev_data = {}
        ip_data  = {}
        mac_data = {}
        ip_params  = ['name', 'ipaddress', 'macaddress', 'label']
        mac_params = ['name', 'macaddress']
        dev_params = ['name', 'macaddress', 'serial_no', 'os', 'os_ver', 'memory',
                      'cpucount', 'cpupower', 'cpucore', 'hddcount', 'hddsize']

        for key, value in self.data.items():
            if key in ip_params:
                ip_data.update({key:value})
            if key in mac_params:
                mac_data.update({key:value})
            if key in dev_params:
                dev_data.update({key:value})

        if 'name' in self.data and self.data['name']:
            all_data.update({'dev_data':dev_data})
        else:
            all_data.update({'dev_data':{}})

        if 'ipaddress' in self.data and self.data['ipaddress']:
            all_data.update({'ip_data':ip_data})
        else:
            all_data.update({'ip_data':{}})

        if 'macaddress' in self.data and self.data['macaddress']:
            all_data.update({'mac_data':mac_data})
        else:
            all_data.update({'mac_data':{}})

        return all_data


class Splunker(object):
    """
    Obtain host names from Splunk. Device42 is based on concept that every device must have the name.
    """
    def __init__(self, host, port, username, password, timeframe, debug, verbose, logger):
        """
        init
        :param host:
        :param port:
        :param username:
        :param password:
        :param timeframe:
        :param debug:
        :param verbose:
        :param logger:
        :return:
        """
        self.host       = host
        self.port       = port
        self.user       = username
        self.pasw       = password
        self.debug      = debug
        self.verbose    = verbose
        self.logger     = logger
        self.hosts      = []
        self.service    = None
        self.kwargs     = {"earliest_time": timeframe, "latest_time": "now", "search_mode": "normal"}

    def connect(self):
        """
        Connect to Splunk
        :return:
        """
        try:
            self.service = client.connect(host=self.host, port=self.port, username=self.user, password=self.pasw)
        except Exception as e:
            msg  =  '[!] Error: %s' % str(e)
            if self.verbose:
                print msg
            if self.debug:
                self.logger.exception(msg)

    def get_host_names(self):
        """
        Get host names from Splunk
        :return:
        """
        searchx = "search host| dedup host | table host"
        res_ex  = self.service.jobs.export(searchx, **self.kwargs)
        reader  = results.ResultsReader(res_ex)
        for result in reader:
            if isinstance(result, dict):
                if 'host' in result:
                    self.hosts.append(result['host'])


class DataParser():
    """
    Actually, we do not parse Splunk data here. You do that in your recipe_*.py.
    This class sends data obtained from Splunk to Mapper class for mapping and formatting.
    Then, we send nicely formatted data to Device42 class which uploads it to ...well...Device42 of course :)
    """
    def __init__(self, mapper, device42):
        """
        init
        :param mapper:
        :param device42:
        :return:
        """
        self.mapper   = mapper
        self.device42 = device42

    def parser(self, data):
        """
        Splunk data to Device42 format
        :param data: Data obtained from Splunk
        :return:
        """
        if isinstance(data, dict):
            self.mapper.set_data(**data)

            all_data = self.mapper.d42_formatter()
            dev_data = all_data['dev_data']
            ip_data  = all_data['ip_data']
            mac_data = all_data['mac_data']

            if dev_data:
                self.device42.upload_device(dev_data)
            if ip_data:
                self.device42.upload_ip(ip_data)
            if mac_data:
                self.device42.upload_mac(mac_data)


def get_config(CONFIGFILE):
    cc = ConfigParser.RawConfigParser()
    if os.path.isfile(CONFIGFILE):
        cc.readfp(open(CONFIGFILE,"r"))
    else:
        print '\n[!] Cannot find config file. Exiting...'
        sys.exit()

    # splunk
    HOST        = cc.get('splunk', 'HOST')
    PORT        = cc.get('splunk', 'PORT')
    USERNAME    = cc.get('splunk', 'USERNAME')
    PASSWORD    = cc.get('splunk', 'PASSWORD')
    TIME_FRAME  = cc.get('splunk', 'TIME_FRAME')

    # device42
    D42_URL     = cc.get('device42', 'D42_URL')
    D42_USER    = cc.get('device42', 'D42_USER')
    D42_PASS    = cc.get('device42', 'D42_PASS')
    DRY_RUN     = cc.getboolean('device42', 'DRY_RUN')

    # other
    DEBUG_FILE  = cc.get('other', 'DEBUG_FILE')
    DEBUG       = cc.getboolean('other', 'DEBUG')
    VERBOSE     = cc.getboolean('other', 'VERBOSE')

    TIME_FRAME  = "-"+TIME_FRAME+"h"
    return HOST, int(PORT), USERNAME, PASSWORD, TIME_FRAME, D42_URL, D42_USER, D42_PASS, DRY_RUN, DEBUG, DEBUG_FILE, VERBOSE



#! /usr/bin/env python

import json

import splunklib.client as client
import splunklib.results as results

from util_uploader import Rest

HOST        = "splunk.levaja.lab"
PORT        = 8089
USERNAME    = "admin"
PASSWORD    = "P@ssw0rd"
TIME_FRAME  = "-24h"
DEBUG       = True
VERBOSE     = True

D42_URL     = 'https://192.168.3.30'
D42_USER    = 'admin'
D42_PASS    = 'adm!nd42'

class Device42():
    def __init__(self, url, user, pwd, debug):
        self.rest = Rest(url, user, pwd, debug)

    def upload_device(self, data):
        self.rest.post_device(data)


class Splunker():
    def __init__(self,host, port, username, password, timeframe, debug, verbose):
        self.host       = host
        self.port       = port
        self.user       = username
        self.pasw       = password
        self.debug      = debug
        self.verbose    = verbose
        self.hosts      = []
        self.service    = None
        self.kwargs     = {"earliest_time": timeframe, "latest_time": "now", "search_mode": "normal"}

    def connect(self):
        try:
            self.service = client.connect(host=self.host, port=self.port, username=self.user, password=self.pasw)
        except Exception as e:
            msg = str(e)
            if self.verbose:
                print '[!] Error: %s' % msg

    def get_host_names(self):
        searchx = "search host| dedup host | table host"
        res_ex  = self.service.jobs.export(searchx, **self.kwargs)
        reader  = results.ResultsReader(res_ex)
        for result in reader:
            if isinstance(result, dict):
                if 'host' in result:
                    self.hosts.append(result['host'])

    def get_data(self):
        if self.hosts:
            for host_name in self.hosts:
                host_data  = {}
                search  = "search host=%s  sourcetype=hardware | dedup host " % host_name
                res_ex  = self.service.jobs.export(search, **self.kwargs)
                reader  = results.ResultsReader(res_ex)
                for result in reader:
                    if isinstance(result, dict):
                        device_name = result['host']
                        host_data.update({'name':device_name})
                        raw =  result['_raw']
                        if self.verbose:
                            print '\n\n'+'='*80
                        raw_data = self.process_raw_data(raw)
                        if raw_data:
                            host_data.update(raw_data)
                nic_data = self.get_nic_data(host_name)
                if nic_data:
                    host_data.update(nic_data)
                os_name  = self.get_os_data(host_name)
                if os_name:
                    host_data.update(os_name)

                if self.verbose:
                    print '\n' + '-' * 30
                    print json.dumps(host_data, indent=4 , sort_keys=True)
                if host_data:
                    d42.upload_device(host_data)

    def process_raw_data(self, raw):
        hw_data = {}
        for rec in raw.split('\n')[1:]:
            splitted = rec.split('  ')
            key = splitted[0].lower()
            value = ' '.join(splitted[1:]).strip()
            if self.verbose:
                print '{0:21} {1}'.format(key,value.strip())
            if key == 'cpu_type':
                try:
                    cpupower = int(float(value.split('@')[1].lower().strip('ghz').strip()) * 1024)
                    hw_data.update({'cpupower':cpupower})
                    hw_data.update({'cpucount':1})
                except Exception as e:
                    pass
            if key == 'cpu_count':
                cpucore = int(value.strip())
                hw_data.update({'cpucore':cpucore})
            if key == 'memory_real':
                try:
                    memory = int(value.split()[0].strip()) /1024
                    hw_data.update({'memory':memory})
                except:
                    pass
            if key == 'hard_drives':
                hdds_raw = [ x for x in value.split(';') if x]
                hddcount = len(hdds_raw)
                sizemax = 0
                for hdd in hdds_raw:
                    size = hdd.split()[-2]
                    if size > sizemax:
                        sizemax = size
                hw_data.update({'hddcount':hddcount})
                hw_data.update({'hddsize':sizemax})
        return hw_data

    def get_nic_data(self, host_name):
        nic_data= {}
        search  = "search host=%s  sourcetype=interfaces | dedup host " % host_name
        res_ex  = self.service.jobs.export(search, **self.kwargs)
        reader  = results.ResultsReader(res_ex)
        for result in reader:
            if isinstance(result, dict):
                try:
                    nic_name,nic_mac, nic_ipv6, nic_ipv6 = result['_raw'].split()[0:4]
                    if self.verbose:
                        print result['_raw'].split()[0:4]
                    nic_data.update({'macaddress':nic_mac})
                except:
                    pass
        return nic_data

    def get_os_data(self, host_name):
        search  = "search index=_internal fwdType=\"*\" hostname=%s | dedup hostname | table hostname, os" % host_name
        res_ex  = self.service.jobs.export(search, **self.kwargs)
        reader  = results.ResultsReader(res_ex)
        for result in reader:
            if isinstance(result, dict):
                if 'os' in result:
                    if self.verbose:
                        print {'os': result['os']}
                    return {'os': result['os']}


if __name__ == '__main__':
    sp = Splunker(HOST, PORT, USERNAME, PASSWORD, TIME_FRAME, DEBUG, VERBOSE)
    d42 = Device42(D42_URL, D42_USER, D42_PASS, DEBUG)
    sp.connect()
    if sp.service:
        sp.get_host_names()
        sp.get_data()

# -*- coding: utf-8 -*-
import sys
import base64
import requests


try:
    requests.packages.urllib3.disable_warnings()
except AttributeError:
    pass


class Rest():
    def __init__(self, BASE_URL, USERNAME, SECRET, DEBUG, VERBOSE, DRY_RUN, LOGGER):
        self.base_url   = BASE_URL
        self.username   = USERNAME
        self.password   = SECRET
        self.debug      = DEBUG
        self.verbose    = VERBOSE
        self.dry_run    = DRY_RUN
        self.logger     = LOGGER

    def uploader(self, data, url):
            payload = data
            headers = {
                'Authorization': 'Basic ' + base64.b64encode(self.username + ':' + self.password),
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            try:
                r = requests.post(url, data=payload, headers=headers, verify=False)
            except Exception as e:
                self.logger.exception(e)
                sys.exit()

            else:
                msg =  unicode(payload)
                if self.verbose:
                    print msg
                msg = 'Status code: %s' % str(r.status_code)
                if self.verbose:
                    print msg
                msg = str(r.text)
                if self.verbose:
                    print msg
                return r.json()
        
    def post_device(self, data):
        if self.dry_run == False:
            url = self.base_url+'/api/device/'
            msg =  '\r\nPosting data to %s ' % url
            if self.verbose:
                print msg
            result = self.uploader(data, url)
            return result

    def post_ip(self, data):
        if self.dry_run == False:
            url = self.base_url+'/api/ip/'
            msg =  '\r\nPosting IP data to %s ' % url
            if self.verbose:
                print msg
            self.uploader(data, url)

    def post_mac(self, data):
        if self.dry_run == False:
            url = self.base_url+'/api/1.0/macs/'
            msg = '\r\nPosting MAC data to %s ' % url
            if self.verbose:
                print msg
            self.uploader(data, url)

    def post_parts(self, data):
        if self.dry_run == False:
            url = self.base_url+'/api/1.0/parts/'
            msg = '\r\nPosting HDD parts to %s ' % url
            if self.verbose:
                print msg
            self.uploader(data, url)



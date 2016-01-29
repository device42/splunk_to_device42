import json

class Mapper():
    def __init__(self):
        """
        init
        :return:
        """
        self.mapping = {}
        self.data    = {}

    def populate_map(self):
        """
        Read app_mapper.cfg and create mapping (dict) between custom Splunk params and Device42 params
        :return:
        """
        with open('app_mapper.cfg')  as f:
            raw = f.readlines()
        for word in raw:
            word = word.strip()
            if word and not word.startswith('#'):
                d42, splunk = word.split()
                self.mapping.update({splunk:d42})

    def set_data(self, **kwargs):
        """
        Read kwargs from Splunk and if they exist in Splunk to Device42 mapping created in populate_map(),
        convert Splunk custom param into Device42 parameter.
        :param kwargs: Custom Splunk params
        :return:
        """
        for key, value in kwargs.iteritems():
            if key in self.mapping:
                d42_key = self.mapping[key]
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
                    return float(''.join(word))
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



def main():
    m = Mapper()
    m.populate_map()

    m.set_data (device_name='linux01',
                serial='123456789',
                os='Linux Mint',
                version='17.2',
                ram='16 Gb',
                cpunum='1',
                cpuspeed='4.7Mhz',
                num_of_cores='8',
                num_of_hdds='1',
                hdd_size='1TB',
                mac='06:86:a6:18:8a:0e',
                ip='192.168.3.30',
                nic_name = 'eth2')

    all_data =  m.d42_formatter()
    dev_data = all_data['dev_data']
    ip_data  = all_data['ip_data']
    mac_data = all_data['mac_data']

    if dev_data:
        print json.dumps(dev_data, indent=4)
    if ip_data:
        print json.dumps(ip_data, indent=4)
    if mac_data:
        print json.dumps(mac_data, indent=4)


if __name__ == '__main__':
    main()



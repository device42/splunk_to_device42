[Device42](http://www.device42.com/) is a IT asset management software system that helps IT personnel manage their complex IT infrastructure.  The software autodiscovers server and IP asset data from physical, virtual, and cloud devices and network components as well as services and service dependencies.  It monitors power and environmental sensors and it captures a wide range of other IT asset data via spreadsheets imports and a robust set of [RESTful APIs](http://api.device42.com/).  Visualizations provided include room and rack layouts, the power chain, IP connectivity, cabling, and application dependencies.  Software license management and password management are also included in the software.

This repository contains a sample script to take inventory data from a Splunk installation and send it to a Device42 appliance using the REST APIs.

## Getting started with the Splunk to Device42 script.

The sample script provided is named starter.py.  Before you can run the script, you need to do 4 things:

1.	 Enter IP and authorization information into a config file.  The sample script assumes the config file is named main.cfg and is located in the same directory as the starter.py file.  The main.cfg file contains IP information and credentials for both the Splunk and Device42 instances and a few other parameters.  See main.cfg for definitions of the required parameters.

2.	Create a Splunk recipe that accesses Splunk data and returns a python dict structure.  A sample recipe is provided (recipe_nix_add_on.py in the recipes folder) that uses the Splunk ["Add-on for Unix and Linux"](https://splunkbase.splunk.com/app/833/).  This recipe will fetch Linux/Unix hardware info from Splunk and return a python dict.


```
#!python

		data = {'device_name':'linux01',
				'serial':'123456789',
				'os':'Linux Mint',
				'version':'17.2',
				'ram':'16 Gb',
				'cpunum':'1',
				'cpuspeed':'4.7Mhz',
				'num_of_cores':'8',
				'num_of_hdds':'1',
				'hdd_size':'1TB',
				'mac':'06:86:a6:18:8a:0e',
				'ip':'192.168.3.30',
				'nic_name' : 'eth2'}

```

The provided recipe consumes the parameters found in the [splunk] section of the main.cfg file shown above but this is not a requirement.  If you wish to hard-code these parameters in your recipe file, that will work fine also.  However, please be aware that the parameters in the other sections (e.g. Device42 credentials) must still be supplied.				

3.	Provide a mapping file (app_mapper.cfg in the same directory as starter.py) that specifies how your python dict keys (see above) map to Device42 field names.  A sample app_mapper.cfg is provided.  The contents of app_mapper.cfg are:

		name		device_name
		serial_no	serial
		os			os
		osver		version
		memory		ram
		cpucount	cpunum
		cpupower	cpuspeed
		cpucore		num_of_cores
		hddcount	num_of_hdds
		hddsize		hdd_size
		macaddress	mac
		ipaddress	ip
		label		nic_name

This is one-to-one mapping between Device42 parameter names (left column) and the keys from your python dict (right column).  The keys must not contain spaces. Either spaces or tabs can be used to separate the left and right columns.

4.  Modify the provided starter.py.  All you need to do is replace the recipe import with your own recipe import.  (Look for -----YOUR CODE STARTS HERE------).

You're ready to go.  Run the starter.py script and you should see your data appear in Device42!


### Requirements
-----------------------------
    * Python 2.7.x
    * Splunk SDK for python (you can install it with sudo pip install splunk-sdk)
    * Requests (you can install it with sudo pip install requests or sudo apt-get install python-requests)

    
### Compatibility
-----------------------------
    * Script runs on Linux (It might run on Windows as well, but it wasn't tested)


### Gotchas
-----------------------------
    * In order to upload a device to Device42, device must have a name. Devices without names are not uploaded.
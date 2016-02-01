[Device42](http://www.device42.com/) is a comprehensive data center inventory management and IP Address management software 
that integrates centralized password management, impact charts and applications mappings with IT asset management.

This repository contains sample script to take Inventory information from a RackTables install and send it to Device42 appliance using the REST APIs.


## Getting started with the Splunk to Device42 script.

This script consists of 3 main components:
1. script itself
2. application mapper and
3. Splunk data parser 

Device42 has an extensive [API ](http://api.device42.com/). In order to help our customers, we have created an interface between Splunk data provided by you and the code that formats and uploads data to Device42. That would be the #1 - script itself (starter.py and what's in ./files subfolder)

Splunk can consume and store data in almost any format you can imagine and on the other hand, Device42 as a hardware inventory software, must have a strict data format. Some kind of mapping between those two different formats must be provided. That would be the #2 - application mapper (app_mapper.cfg)

Since you are the one that understands the custom formatted data stored in Splunk, and we do not,  there is a need that you write a small script that queries the Splunk and extracts important data. That data should be formatted as Python dict. Keys must match what you have entered in app_mapper.cfg. That querying/parsing part is #3 - Splunk data parser 


### Application mapper
---------------------------------
File "app_mapper.cfg" contains two columns. Left one represents Device42 parameter names, and it should not be edited, unless you know what are you doing.
Right column should contain key names from your dict returned from parsing Splunk data.
For example, let's say that you have coded your data parser that it returns data that look like this:

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

In return, the app_mapper.cfg file should look like this:

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

This is one-to-one mapping between Device42 parameter names (left column) and keys from your dict (right column).
Keys must not contain spaces. Space between columns can be a single or multiple spaces or tabs, what ever you prefer. 
Dict must be named "data".


### Data parser (recipes)
---------------------------------
Since we do not know how your Splunk data is formatted, you must code a plug-in script (recipe) to obtain that data and output a dict that matches entries in app_mapper.cfg file. Your recipe should consume the following arguments:

- SPLUNK_HOST
- SPLUNK_PORT
- SPLUNK_USERNAME
- SPLUNK_PASSWORD
- TIME_FRAME
- VERBOSE

Please, take a look at "Configuration" section below for details on these arguments.

There is an example data parser named "recipe_nix_add_on.py" in ./recipes subfolder. If you happen to use  ["Add-on for Unix and Linux"](https://splunkbase.splunk.com/app/833/) add-on to generate and send Linux/Unix hardware info to Splunk, this recipe will fetch hardware data, format it according to app_mapper.cfg example above and upload it to Device42 server.

Basically, all you need to do in order for script to run your recipe is to add a single import line to "starter.py" file.
A function "your_code_goes_here()" looks like this:

	def your_code_goes_here():
	    # ----------------- YOUR CODE STARTS HERE ------------------------------
	    from recipes.recipe_nix_add_on import Nix_Linux_add_on as recipe
	    # ----------------- YOUR CODE ENDS HERE --------------------------------
	    rcp = recipe(SPLUNK_HOST, SPLUNK_PORT, SPLUNK_USERNAME, SPLUNK_PASSWORD, TIME_FRAME, VERBOSE)
	    for device in splunker.hosts:
	        data = rcp.get_data(device)
	        dparser.parser(data)



### Configuration
-----------------------------
Configuration is set in "main.cfg" file. It follows simple .ini syntax.

	[splunk]
	# Splunk host
	HOST        = splunk.test.lab
	# Splunk port
	PORT        = 8089
	# Splunk server username
	USERNAME    = admin
	# Splunk server password
	PASSWORD    = cant_guess
	# start search from
	TIME_FRAME  = 24
	
	[device42]
	# device42 url (url starts with HTTPS!)
	D42_URL     = https://192.168.1.100
	# Device42 server username
	D42_USER    = admin
	# Device42 server password
	D42_PASS    = adm!nd42
	# Upload to Device42 or not?
	DRY_RUN		= False
	
	[other]
	# write to debug log (True) or not (False)
	DEBUG       = True
	# name of the debug log file (no path, just file name!)
	DEBUG_FILE  = debug.log
	# write to STDOUT (True) or not (False)
	VERBOSE     = True


TIME_FRAME param sets search starting point in the past. Search is performed from: **now()-TIME_FRAME** to: **now()**.


	self.kwargs     = {"earliest_time": timeframe, "latest_time": "now", "search_mode": "normal"}



### Usage
-----------------------------
Run from starter.py



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
    * If you use customized data format to store data in Splunk, you need to write a script that can fetch, process and output that data as dict/json.
#! /usr/bin/env python

import logging
import os

from files.main import get_config, Mapper, Splunker, Device42, DataParser

APP_DIR    = os.path.abspath(os.path.dirname(__file__))
CONFIGFILE = os.path.join(APP_DIR, 'main.cfg')
APP_MAPPER = os.path.join(APP_DIR, 'app_mapper.cfg')





def your_code_goes_here():
    """
    Import your recipe as "from recipes.recipe_name import your_class"
    Create class instance and initiate it with necessary arguments (splunk host, port, username, password, timeframe, verbosity...)
    Iterate over host names and send dict formatted data to data parser.
    Enjoy.
    :return:
    """
    # ----------------- YOUR CODE STARTS HERE ------------------------------
    from recipes.recipe_nix_add_on import Nix_Linux_add_on as recipe
    # ----------------- YOUR CODE ENDS HERE --------------------------------
    rcp = recipe(SPLUNK_HOST, SPLUNK_PORT, SPLUNK_USERNAME, SPLUNK_PASSWORD, TIME_FRAME, VERBOSE)
    for device in splunker.hosts:
        data = rcp.get_data(device)
        dparser.parser(data)





if __name__ == '__main__':
    SPLUNK_HOST, SPLUNK_PORT, SPLUNK_USERNAME, SPLUNK_PASSWORD, TIME_FRAME, D42_URL, D42_USER, D42_PASS, \
    DRY_RUN, DEBUG, DEBUG_FILE, VERBOSE = get_config(CONFIGFILE)
    DEBUG_LOG = os.path.join(APP_DIR, DEBUG_FILE)

    logger = None

    if DEBUG:
        logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG, filename=DEBUG_LOG)

    mapper   = Mapper(APP_MAPPER)
    mapper.populate_map()
    splunker = Splunker(SPLUNK_HOST, SPLUNK_PORT, SPLUNK_USERNAME, SPLUNK_PASSWORD, TIME_FRAME, DEBUG, VERBOSE, logger)
    device42 = Device42(D42_URL, D42_USER, D42_PASS, DEBUG, VERBOSE, DRY_RUN, logger)
    dparser  = DataParser(mapper, device42)

    splunker.connect()
    if splunker.service:
        splunker.get_host_names()
        your_code_goes_here()

import json
import os

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import configure_firefox
from app import (
    TESTING,
    logger,
)


DEFAULT_SCREEN_RES = (1366, 768)
# TODO Work with command line argument / config file
LOG_FILE = os.environ.get('GECKODRIVER_LOG_FILE', 'geckodriver.log')


def get_driver(visit_id, crawl_id):
    root_dir = os.path.dirname(os.path.abspath(__file__))

    browser_params = json.loads(open('browser_params.json').read())

    browser_params['visit_id'] = visit_id
    browser_params['crawl_id'] = crawl_id

    # Use Options instead of FirefoxProfile to set preferences since the
    # Options method has no "frozen"/restricted options.
    # https://github.com/SeleniumHQ/selenium/issues/2106#issuecomment-320238039
    fo = Options()

    # If testing we don't want headless and we do want jsconsole
    if TESTING:
        browser_params['headless'] = False
        fo.add_argument('-jsconsole')

    # Set various prefs to improve speed and eliminate traffic to Mozilla
    configure_firefox.optimize_prefs(fo, browser_params)

    # Set custom prefs. These are set after all of the default prefs to allow
    # our defaults to be overwritten.
    for name, value in browser_params['prefs'].items():
        logger.info(f"OPENWPM: Setting custom preference: {name} = {value}")
        fo.set_preference(name, value)

    # Set the binary
    binary_path = os.path.join(root_dir, 'firefox-bin', 'firefox-bin')
    fo.binary = binary_path
    logger.info(f"OPENWPM: Browser Binary Path {binary_path}")

    # Launch the webdriver
    driver = webdriver.Firefox(options=fo, service_log_path=LOG_FILE)

    # Get profile
    profile_path = driver.capabilities['moz:profile']
    logger.info(f"OPENWPM: Browser Profile Path {profile_path}")

    # Set window size
    driver.set_window_size(*DEFAULT_SCREEN_RES)

    # Write extension config file
    extension_config = dict()
    extension_config.update(browser_params)
    extension_config['ws_address'] = ("127.0.0.1", 7799)
    extension_config['testing'] = TESTING
    ext_config_file = os.path.join(profile_path, 'browser_params.json')
    with open(ext_config_file, 'w') as f:
        json.dump(extension_config, f)

    # Load extension
    ext_loc = os.path.join(root_dir, 'openwpm.xpi')
    ext_loc = os.path.normpath(ext_loc)
    driver.install_addon(ext_loc, temporary=True)
    logger.info("OPENWPM: OpenWPM Firefox extension loaded")

    return driver

import json
import os

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options

import configure_firefox
from app import logger

# TODO
# - Work with command line argument LOG FILE
LOG_FILE = os.environ.get('GECKODRIVER_LOG_FILE', 'geckodriver.log')


def get_driver(visit_id, crawl_id):
    root_dir = os.path.dirname(os.path.abspath(__file__))

    browser_params = json.loads(open('browser_params.json').read())
    manager_params = json.loads(open('manager_params.json').read())

    browser_params['visit_id'] = visit_id
    browser_params['crawl_id'] = crawl_id

    # Use Options instead of FirefoxProfile to set preferences since the
    # Options method has no "frozen"/restricted options.
    # https://github.com/SeleniumHQ/selenium/issues/2106#issuecomment-320238039
    fo = Options()
    fo.set_preference('plugin.state.flash', 0)

    DEFAULT_SCREEN_RES = (1366, 768)

    profile_settings = dict()
    profile_settings['screen_res'] = DEFAULT_SCREEN_RES

    if browser_params['headless']:
        fo.set_headless(True)
        fo.add_argument('--width={}'.format(DEFAULT_SCREEN_RES[0]))
        fo.add_argument('--height={}'.format(DEFAULT_SCREEN_RES[1]))

    # Make profile
    fp = FirefoxProfile()
    browser_profile_path = fp.path + '/'
    logger.info(f"OPENWPM: Browser Profile Path {browser_profile_path}")

    # Configure privacy settings
    configure_firefox.privacy(browser_params, fp, fo, root_dir, browser_profile_path)

    # Set various prefs to improve speed and eliminate traffic to Mozilla
    configure_firefox.optimize_prefs(fo)

    # Set custom prefs. These are set after all of the default prefs to allow
    # our defaults to be overwritten.
    for name, value in browser_params['prefs'].items():
        logger.info(f"OPENWPM: Setting custom preference: {name} = {value}")
        fo.set_preference(name, value)

    # Launch the webdriver
    firefox_binary_path = os.path.join(root_dir, 'firefox-bin', 'firefox-bin')
    fb = FirefoxBinary(firefox_path=firefox_binary_path)
    driver = webdriver.Firefox(
        firefox_profile=fp,
        firefox_binary=fb,
        firefox_options=fo,
        service_log_path=LOG_FILE
    )

    # Set window size
    driver.set_window_size(*profile_settings['screen_res'])

    # Write extension config file
    extension_config = dict()
    extension_config.update(browser_params)
    extension_config['logger_address'] = ("127.0.0.1", 7799)
    extension_config['aggregator_address'] = ("127.0.0.1", 7799)
    extension_config['testing'] = manager_params['testing']
    ext_config_file = browser_profile_path + 'browser_params.json'
    with open(ext_config_file, 'w') as f:
        json.dump(extension_config, f)

    # Load extension
    ext_loc = os.path.join(root_dir, 'openwpm.xpi')
    ext_loc = os.path.normpath(ext_loc)
    driver.install_addon(ext_loc, temporary=True)
    logger.info("OPENWPM: OpenWPM Firefox extension loaded")

    return driver

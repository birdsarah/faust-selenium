import json
import os

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import configure_firefox
from config import get_manager_config


DEFAULT_SCREEN_RES = (1366, 768)
# TODO Work with command line argument / config file
LOG_FILE = get_manager_config('geckodriver_log_file')


def get_driver(visit_id, crawl_id, ws_port):
    logs = []

    browser_params_file = get_manager_config('browser_params_file')
    browser_params = json.loads(open(browser_params_file).read())
    browser_params['visit_id'] = visit_id
    browser_params['crawl_id'] = crawl_id

    # Use Options instead of FirefoxProfile to set preferences since the
    # Options method has no "frozen"/restricted options.
    # https://github.com/SeleniumHQ/selenium/issues/2106#issuecomment-320238039
    fo = Options()

    # If testing we don't want headless and we do want jsconsole
    if get_manager_config('testing'):
        browser_params['headless'] = False
        fo.add_argument('-jsconsole')

    # Set various prefs to improve speed and eliminate traffic to Mozilla
    configure_firefox.optimize_prefs(fo, browser_params)

    # Set custom prefs. These are set after all of the default prefs to allow
    # our defaults to be overwritten.
    for name, value in browser_params['prefs'].items():
        logs.append(f"OPENWPM: Setting custom preference: {name} = {value}")
        fo.set_preference(name, value)

    # Set the binary
    binary_path = get_manager_config('firefox_binary_path')
    assert os.path.exists(binary_path), f'Binary not found at: {binary_path}'
    fo.binary = binary_path
    print(f"OPENWPM: Browser Binary Path {binary_path}")

    # Set geckodriver
    geckodriver_executable = get_manager_config('geockodriver_executable', 'geckodriver.exe')
    fo.executable_path = geckodriver_executable

    # Launch the webdriver
    driver = webdriver.Firefox(options=fo, service_log_path=LOG_FILE)

    # Get profile
    profile_path = driver.capabilities['moz:profile']
    logs.append(f"OPENWPM: Browser Profile Path {profile_path}")

    # Set window size
    driver.set_window_size(*DEFAULT_SCREEN_RES)

    # Write extension config file
    extension_config = dict()
    extension_config.update(browser_params)
    extension_config['ws_address'] = ("127.0.0.1", ws_port)
    extension_config['testing'] = get_manager_config('testing')
    ext_config_file = os.path.join(profile_path, 'browser_params.json')
    with open(ext_config_file, 'w') as f:
        json.dump(extension_config, f)

    # Load extension
    extension_path = get_manager_config('extension_path')
    assert os.path.exists(extension_path), f'Extension not found at: {extension_path}'
    driver.install_addon(extension_path, temporary=True)
    logs.append("OPENWPM: OpenWPM Firefox extension loaded")

    return driver, logs

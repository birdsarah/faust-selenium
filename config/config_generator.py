import os
from jinja2 import Environment, FileSystemLoader

def log(path):
    return os.path.join('logs', 'crawler', path)

FIREFOX_BINARY_PATH = "/home/bird/Dev/birdsarah/faust-selenium/app/firefox-bin/firefox-bin"
EXTENSION_PATH = "/home/bird/Dev/birdsarah/faust-selenium/app/openwpm.xpi"

def render():
    e = Environment(
        loader=(FileSystemLoader('templates')),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    t = e.get_template('crawler')
    result = t.render(
        browser_params_file='config/browser_params.json',
        manager_params_file='config/manager_params.json',
        geckodriver_log_file=log('geckodriver.log'),
        firefox_binary_path=FIREFOX_BINARY_PATH,
        extension_path=EXTENSION_PATH,
        display=':99',
        n_crawlers=2,
    )
    print(result)


if __name__ == '__main__':
    render()

from jinja2 import Environment, FileSystemLoader


FIREFOX_BINARY_PATH = "/home/sbird/faust-selenium/app/firefox-bin/firefox-bin"
EXTENSION_PATH = "/home/sbird/faust-selenium/app/openwpm.xpi"


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
        firefox_binary_path=FIREFOX_BINARY_PATH,
        extension_path=EXTENSION_PATH,
        site_list='lists/alexatop1k.csv',
        crawl_name_base='gcp-parallel-whead-kafka-3',
        database_name_base='data/crawl-data',
        display=':99',
        n_crawlers=1,
        n_parallel=12,
    )
    print(result)


if __name__ == '__main__':
    render()

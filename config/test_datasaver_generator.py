from jinja2 import Environment, FileSystemLoader


FIREFOX_BINARY_PATH = "/home/sbird/faust-selenium/app/firefox-bin/firefox-bin"
EXTENSION_PATH = "/home/sbird/faust-selenium/app/openwpm.xpi"


def render():
    e = Environment(
        loader=(FileSystemLoader('templates')),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    t = e.get_template('datasaver')
    result = t.render(
        manager_params_file='config/manager_params_test.json',
        crawl_name_base='gcp-parallel-whead-kafka-test',
        database_name_base='data/crawl-data-test',
        n_crawlers=2,
        n_parallel=2,
    )
    print(result)


if __name__ == '__main__':
    render()

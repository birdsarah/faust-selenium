from jinja2 import Environment, FileSystemLoader


FIREFOX_BINARY_PATH = "C:\\Users\\Bird\\firefox-bin\\firefox.exe"
EXTENSION_PATH = "C:\\Users\\Bird\\openwpm.xpi"


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
        crawl_name_base='platform-comp-1-win-local',
        database_name_base='data/platform-1-win-local',
        n_crawlers=3,
        n_parallel=1,
    )
    print(result)


if __name__ == '__main__':
    render()

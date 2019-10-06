from jinja2 import Environment, FileSystemLoader


win_params = dict(
    firefox_binary_path="C:\\Users\\Bird\\firefox-bin\\firefox.exe",
    extension_path="C:\\Users\\Bird\\openwpm.xpi",
    crawl_name_base='platform-comp-1-win-local',
    database_name_base='data/platform-1-win-local',
)
linux_local_params = dict(
    firefox_binary_path='/home/sbird/faust-selenium/app/firefox-bin/firefox-bin',
    extension_path='/home/sbird/faust-selenium/app/openwpm.xpi',
    crawl_name_base='platform-comp-1-linux-local',
    database_name_base='data/platform-1-linux-local',
    display=':99',
)


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
        n_crawlers=3,
        n_parallel=1,
        site_list='lists/alexatop1k.csv',
        **linux_local_params
    )
    print(result)


if __name__ == '__main__':
    render()

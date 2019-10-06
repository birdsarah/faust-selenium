from jinja2 import Environment, FileSystemLoader


win_params = dict(
    firefox_binary_path="C:\\Users\\Bird\\firefox-bin\\firefox.exe",
    extension_path="C:\\Users\\Bird\\openwpm.xpi",
    crawl_name_base='platform-comp-test-win-local',
    database_name_base='data/platform-test-win-local',
)
linux_local_params = dict(
    firefox_binary_path='/home/bird/Dev/birdsarah/faust-selenium/app/firefox-bin/firefox-bin',
    extension_path='/home/bird/Dev/birdsarah/faust-selenium/app/openwpm.xpi',
    crawl_name_base='platform-comp-test-linux-local',
    database_name_base='data/platform-test-linux-local',
    display=':99',
)
linux_cloud_params = dict(
    firefox_binary_path='/home/sbird/faust-selenium/app/firefox-bin/firefox-bin',
    extension_path='/home/sbird/faust-selenium/app/openwpm.xpi',
    crawl_name_base='platform-comp-test-linux-cloud',
    database_name_base='data/platform-test-linux-cloud',
    display=':99',
)
osx_params = dict(
    firefox_binary_path='/Users/caged/Dev/birdsarah/faust-selenium/Nightly.app/Contents/MacOS/firefox-bin',
    extension_path='/Users/caged/Dev/birdsarah/faust-selenium/app/openwpm.xpi',
    crawl_name_base='platform-comp-test-osx-local',
    database_name_base='data/platform-test-osx-local',
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
        p='test',
        site_list='lists/alexatop1k.csv',
        **win_params
    )
    print(result)


if __name__ == '__main__':
    render()

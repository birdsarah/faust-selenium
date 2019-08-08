import time
import os, sys

from app import app, crawl_log_topic, CrawlLog


def follow(thefile):
    thefile.seek(0, os.SEEK_END)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line


@app.task
async def main():
    logfile = open("geckodriver.log", "r")
    loglines = follow(logfile)
    for line in loglines:
        print(line)
        await crawl_log_topic.send(value=CrawlLog(log=line))


if __name__ == '__main__':
    try:
        app.main()
    except KeyboardInterrupt:
        try:
            os.exit(0)
        except SystemExit:
            sys._exit(0)

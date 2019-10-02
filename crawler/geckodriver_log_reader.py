import asyncio
import os

from app import (
    app,
    logger,
)
from browser_setup import LOG_FILE


def tail_F(some_file):
    # Thanks Raymond Hettinger!
    # https://stackoverflow.com/questions/12523044/how-can-i-tail-a-log-file-in-python
    first_call = True
    while True:
        try:
            with open(some_file) as input:
                if first_call:
                    input.seek(0, 2)
                    first_call = False
                latest_data = input.read()
                while True:
                    if '\n' not in latest_data:
                        latest_data += input.read()
                        if '\n' not in latest_data:
                            yield ''
                            if not os.path.isfile(some_file):
                                break
                            continue
                    latest_lines = latest_data.split('\n')
                    if latest_data[-1] != '\n':
                        latest_data = latest_lines[-1]
                    else:
                        latest_data = input.read()
                    for line in latest_lines[:-1]:
                        yield line + '\n'
        except IOError:
            yield ''


@app.task
async def geckodriver_log_reader():
    # On startup start tailing the geckodriver log file and logging new lines
    for line in tail_F(LOG_FILE):
        if line != '':
            logger.debug(f'GECKODRIVER {line}')
        # Throttle the output so things don't go too fast. Seems fine.
        await asyncio.sleep(0.2)

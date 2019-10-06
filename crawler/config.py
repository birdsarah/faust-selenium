import json
import os

import os
os.environ['MANAGER_PARAMS_FILE'] = os.path.join('config', 'manager_params.json')


MANAGER_PARAMS_FILE = os.environ.get('MANAGER_PARAMS_FILE', None)
if MANAGER_PARAMS_FILE is None:
    raise RuntimeError('MANAGER_PARAMS_FILE must be in environment')

with open(MANAGER_PARAMS_FILE, 'r') as f:
    MANAGER_PARAMS = json.loads(f.read())


def get_manager_config(key, default=None):
    # First check environment
    result = os.environ.get(key.upper(), None)
    # Then manager params
    if result is None:
        result = MANAGER_PARAMS.get(key.lower(), None)
    if result is None and default is None:
        raise ValueError(f'No manager config for {key}')
    else:
        if result is None:
            result = default
        return result


#with open(get_manager_config('browser_params_file'), 'r') as f:
#    BROWSER_PARAMS = json.loads(f.read())
#
#
#def get_browser_config(key):
#    # ONLY LOOK IN BROWSER PARAMS
#    result = BROWSER_PARAMS.get(key.lower(), None)
#    if result is None:
#        raise ValueError(f'No browser config for {key}')
#    else:
#        return result

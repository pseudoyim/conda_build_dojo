'''
Utilities for dojo commands.
'''
import io
import json
import os
import pandas as pd
import requests
import sys
import yaml
from datetime import datetime
from dojo import ROOT_DIR

try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO


def get_timestamp_for_file():
    ts_format = '%Y%m%d_%H%M%S'
    now = datetime.utcnow()
    return now.strftime(ts_format)


def get_timestamp_for_action():
    ts_format = '%Y-%m-%d %H:%M:%S'
    now = datetime.utcnow()
    return now.strftime(ts_format) + ' UTC'


def get_latest():
    # Get latest lesson from history.csv
    
    df_history = pd.read_csv(f'{ROOT_DIR}/history.csv')

    # try:
    #     last_row = 
        
    #     latest_lesson_name = 

    # except: # No rows in the history.csv
    #     raise 'You have no history. Please start a lesson to create one.'

    # Get latest step from <lesson>/progress.csv
    pass


def get_repodata_snapshot(lesson_name, subdirs):
    '''
    Takes a snapshot of the current repodata.json for defaults.
    '''
    print(f'Creating repodata snapshots for {subdirs}...')

    ts = get_timestamp_for_file()
    repodata_snapshot_dir = f'{ROOT_DIR}/lessons/{lesson_name}/repodata/{ts}'

    for subdir in subdirs:
        # Create sub-directory tree.
        os.makedirs(f'{repodata_snapshot_dir}/{subdir}')
        fn = f'{repodata_snapshot_dir}/{subdir}/repodata.json'
        url = f'https://repo.anaconda.com/pkgs/main/{subdir}/repodata.json'
        print(f'Fetching {url}...')
        resp = requests.get(url)

        if resp.status_code == 200:
            response_object = resp.json()
            print('{} packages.'.format(len(response_object['packages'])))

            # Dump resp to a json file at fn.
            with open(fn, 'w') as output_file:
                json.dump(response_object, output_file) 

        else:
            print('Failed to fetch repodata.')
            sys.exit(1)

    print('...success!')


def prune_repodata():
    pass


def configure_condarc(lesson_name):
    print('Setting up repo snapshot...')
    print('Updating your .condarc to point to repodata snapshot from <TIMESTAMP> for the following subdirs:')
    # Point .condarc channel to only point at local 'lesson_name/repodata/ts/' directory.
    pass


def show_history(all_history=False):
    # Load conda_build_dojo/history.csv

    # Display table of last ten actions.

    pass


def show_lessons(all_platforms=False):
    # Load conda_build_dojo/curriculum.yaml

    # Display tree of lessons available, (title, objectives, target_package).

    pass


def get_history():
    return pd.read_csv(os.path.join(ROOT_DIR, 'history.csv'))


def update_history(lesson_name, action):
    df_history = get_history()

    ts = get_timestamp_for_action()

    if action == 'stop':
        active = False
    else:
        active = True

    new_row = {'timestamp': ts,
               'lesson_name': lesson_name,
               'action': action,
               'active': active
              }
    df_history = df_history.append(new_row, ignore_index=True)
    df_history.to_csv(os.path.join(ROOT_DIR, 'history.csv'), index=False)


def create_lesson_progress(lesson_name):
    columns = ['start_timestamp', 'lesson_index', 'note']
    ts = get_timestamp_for_action()
    row = [ts, 0, '']
    df = pd.DataFrame([row], columns=columns)
    df.to_csv(f'{ROOT_DIR}/lessons/{lesson_name}/progress.csv', index=False)


def get_lesson_progress(lesson_name):
    df_lesson_progress = pd.read_csv(f'{ROOT_DIR}/lessons/{lesson_name}/progress.csv')

    pass


def update_lesson_progress(lesson_name, step_index):
    pass

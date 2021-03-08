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
from dojo import ROOT_DIR, LESSONS_DIR
from tabulate import tabulate

try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO


PROGRESS_COLUMNS = ['lesson_name', 'start_timestamp', 'lesson_index', 'note']


def add_lesson_yaml(new_lesson_path):
    # Add lesson yaml in new lesson dir.
    save_path = os.path.join(new_lesson_path, 'lesson.yaml')
    with open(save_path, 'w') as lesson_yaml:
        lesson_yaml.write(LESSON_YAML_TEMPLATE)
    print('Created new lesson.yaml template.')


def configure_condarc(lesson_name):
    print('Setting up repo snapshot...')
    print('Updating your .condarc to point to repodata snapshot from <TIMESTAMP> for the following subdirs:')
    # Point .condarc channel to only point at local 'lesson_name/repodata/ts/' directory.
    pass


def get_latest():
    '''
    Looks at the last row in history.csv to see if there's an active lesson.
    If there is, return that lesson's name and current step index.
    Else, tell the user they need to start a lesson.
    '''
    df_history = pd.read_csv(f'{ROOT_DIR}/history.csv', index_col=False)

    if len(df_history.index) == 0:
        # i.e. there are no rows in the history.csv
        print('You have no lesson history. Please start a lesson to begin one.')
        sys.exit(1)
    
    else:
        # Get latest active lesson from history.csv
        last_row = list(df_history.tail(1).values)[0]

        # Check if the last record has "active = True".
        active_status = last_row[-1]
        if active_status is True:
            latest_lesson_name = last_row[1]
        else:
            print('No active lesson. Please start one.')
            sys.exit(1)

    # Get latest row from <lesson>/progress.csv
    # Looks like: [lesson_name, start_timestamp, lesson_index, note]
    latest_row = get_lesson_progress(latest_lesson_name)

    return latest_row[0], latest_row[2]


def get_repodata_snapshot(lesson_folder_name, subdirs):
    '''
    Takes a snapshot of the current repodata.json for defaults.
    '''
    print(f'\nCreating repodata snapshots for {subdirs}...')

    ts = get_timestamp_for_file()
    repodata_snapshot_dir = f'{LESSONS_DIR}/{lesson_folder_name}/dojo_repodata/{ts}'

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


def get_timestamp_for_file():
    ts_format = '%Y%m%d_%H%M%S'
    now = datetime.utcnow()
    return now.strftime(ts_format)


def get_timestamp_for_action():
    ts_format = '%Y-%m-%d %H:%M:%S'
    now = datetime.utcnow()
    return now.strftime(ts_format) + ' UTC'


def prune_repodata():
    pass


##############
#    TAGS    #
##############

def search_tag(search_tag):
    '''
    Searches each lesson's lesson.yaml to see if they match
    for the given tag.
    '''
    # Final list of lists that looks like:
    # Title   LessonName    Objectives    MatchingTag    
    results = []

    # Load every lesson.yaml
    from glob import glob
    all_lesson_paths = glob(os.path.join(LESSONS_DIR,'*'))
    for lesson_path in all_lesson_paths:
        lesson_name = lesson_path.split('/')[-1]
        lesson_specs = load_lesson_specs(lesson_name)
        tags = lesson_specs['tags']

        # Search for tag.
        for tag in tags:
            if search_tag.lower() in tag.lower():
                title = lesson_specs['title']
                objectives = lesson_specs['objectives']
                match = [title, lesson_name, objectives, tag]
                results.append(match)

    print(f'\nSearch results for: {search_tag}')
    # TODO: When `tabulate` project releases fix for v0.8.9 (with maxcolwidths keyword arg), use it to set max col widths.
    # print(tabulate(results, headers=['Title', 'Lesson Name', 'Objectives', 'Matching Tag'], tablefmt="grid", maxcolwidth=[None, None, 24, None]))
    print(tabulate(results, headers=['Title', 'Lesson Name', 'Objectives', 'Matching Tag'], tablefmt="grid",))


#################
#    HISTORY    #
#################

def load_history():
    return pd.read_csv(os.path.join(ROOT_DIR, 'history.csv'), index_col=False)


def show_history(all_history=False):
    # Load conda_build_dojo/history.csv

    # Show: Lesson   Last Action   Timestamp

    pass


def update_history(lesson_name, action):
    '''
    Adds a row to history.csv, recording the lesson_name
    and whether it was started, stopped, or completed 
    (and boolean of whether that lesson is active or not).
    '''
    df_history = load_history()
    ts = get_timestamp_for_action()

    if action in ['completed', 'stop']:
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


#################
#    LESSONS    #
#################

def load_lesson_specs(lesson_name):
    '''
    Gets specs from the lesson.yaml
    '''
    lesson_yaml_path = os.path.join(LESSONS_DIR, lesson_name, 'lesson.yaml')

    try:
        with open(lesson_yaml_path, mode='r') as lesson_specs:
            import yaml    # i.e. pyyaml
            return yaml.safe_load(lesson_specs)
    except FileNotFoundError:
        print(f'ERROR: lesson.yaml for {lesson_name} not found.')
        sys.exit(1)


def show_lessons(all_platforms=False):
    # Load conda_build_dojo/curriculum.yaml

    # Display:
    # topic, title, lesson_name, target_platform
    print('TODO: Show lessons here (from curriculum.yaml).')
    pass


def create_lesson_progress(lesson_name):
    ts = get_timestamp_for_action()
    row = [lesson_name, ts, 0, '']
    df = pd.DataFrame([row], columns=PROGRESS_COLUMNS)
    df.to_csv(f'{LESSONS_DIR}/{lesson_name}/progress.csv', index=False)


def get_all_lesson_progress(lesson_name):
    '''
    Returns all progress.csv as a df.
    '''
    return pd.read_csv(f'{LESSONS_DIR}/{lesson_name}/progress.csv', index_col=False)    


def get_lesson_progress(lesson_name):
    '''
    Returns only the last row of progress.csv as a list.
    '''
    df = pd.read_csv(f'{LESSONS_DIR}/{lesson_name}/progress.csv', index_col=False)
    # Return the last row.
    return df.values[-1].tolist()


def update_lesson_progress(lesson_name, step_index, note=''):
    ts = get_timestamp_for_action()
    # By 'update', we're just adding a row.
    df = pd.read_csv(f'{LESSONS_DIR}/{lesson_name}/progress.csv', index_col=False)
    new_row = [lesson_name, ts, step_index, note]
    df_new_row = pd.DataFrame([new_row], columns=PROGRESS_COLUMNS)
    df = df.append(df_new_row, ignore_index=True)
    df.to_csv(f'{LESSONS_DIR}/{lesson_name}/progress.csv', index=False)    


###################
#    TEMPLATES    #
###################

LESSON_YAML_TEMPLATE = '''# PLEASE ADD VALUES FOR ALL KEYS BELOW.

# IMPORTANT: If your lesson requires a snapshot of repodata in a certain 
# state (e.g. missing some dependencies for python-3.9), then please make
# sure the repodata is saved in the following directory structure:
#
# dojo/
#   |---- lessons/
#           |---- 001_version_bump/
#                   |---- dojo_repodata/
#                           |---- <TIMESTAMP>/
#                                   |---- linux-64/
#                                           |---- repodata.json
#                                   |---- noarch/
#                                           |---- repodata.json

# The lesson title.
# Example: "How to do a version bump"
title: 

# Learning objectives. 
# Each objective should help complete this sentence: 
# "By the end of this lesson, the learner will be able to..."
objectives: 
  - "EXAMPLE OBJECTIVE"

# Tags.
# Learners can search for this lesson using tags entered here.
tags: []

# Package name and version the learner will be attempting to build.
# Example: numpy-1.16.0
target_package:

# Target platform the package will be built for.
# Examples: linux-64, osx-64, win-64, noarch
target_platform: 

# URL to the feedstock (use HTTPS, not SSH, to avoid the need for a key).
# Example: https://github.com/AnacondaRecipes/tqdm-feedstock.git
feedstock_url: 

# The specific commit hash from the feedstock repo that should be initially 
# checked out. This acts as the starting point for the learner, a "snapshot"
# in time from which they will complete their lesson objectives.
commit: 

# Indicates whether this lesson requires a modified repodata "snapshot".
# In other words, a version of defaults that's been edited to recreate the 
# starting point for the lesson. 
# If your lesson requires the repodata snapshot, update this to be "True".
modified_repodata: False

# Lesson prompts (or steps).
# List the propmpts/steps the learner should go through.
# You can also pose questions and answers (for example, one prompt is 
# a question, and the subsequent prompt is the answer to that question).
# BONUS: Provide hints to the learner (just tell them the hint will be 
# revealed in the next step if they want it).
prompts:
  - EXAMPLE - Open the meta.yaml...
  - EXAMPLE - Increment the build number...
'''



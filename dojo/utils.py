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
from collections import Counter
from colorama import Fore, Back, Style
from datetime import datetime
from dojo import ROOT_DIR, LESSONS_DIR
from pathlib import Path
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


def download_package(url, destination_path):
    '''
    Adapted from jpmds/workflow/download.py
    '''
    # Make sure the directory path exists for each channel and subdir.
    pkg_path_parent_dir_parts = destination_path.split('/')[:-1]
    pkg_path_parent_dir = '/' + os.path.join(*pkg_path_parent_dir_parts)
    Path(pkg_path_parent_dir).mkdir(parents=True, exist_ok=True)

    path_pieces = url.split('/')
    basename = path_pieces[-1]
    channel = path_pieces[-3]

    print(f'  Downloading: {basename} from: {channel}')

    r = requests.get(url, stream=True)

    # The easiest way to notify the user that something went wrong is to 
    # terminate, loudly. this will raise an HTTPError if 
    # 400 <= status_code < 600, otherwise, no-op.
    r.raise_for_status()

    with open(destination_path, 'wb') as f:
        # Updated to follow: 
        # https://requests.readthedocs.io/en/master/user/quickstart/#raw-response-content
        # shutil.copyfileobj(r.raw, f)
        for chunk in r.iter_content(chunk_size=128):
            f.write(chunk)


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
        active_status = last_row[-2]
        if active_status is True:
            latest_lesson_name = last_row[1]
        else:
            print('No active lesson. Please start one.')
            sys.exit(1)

    # Get latest row from <lesson>/progress.csv
    # Looks like: [lesson_name, start_timestamp, lesson_index, note]
    latest_row = get_lesson_progress(latest_lesson_name)

    return latest_row[0], latest_row[2]


def get_timestamp_for_file():
    ts_format = '%Y%m%d_%H%M%S'
    now = datetime.utcnow()
    return now.strftime(ts_format)


def get_timestamp_for_action():
    ts_format = '%Y-%m-%d %H:%M:%S'
    now = datetime.utcnow()
    return now.strftime(ts_format) + ' UTC'


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
                objectives = ' * '.join(str(obj) for obj in lesson_specs['objectives'])
                match = [title, lesson_name, objectives, tag]
                results.append(match)

    if not results:
        print(f'No results for: "{search_tag}"')
        sys.exit()

    print(Fore.CYAN + f'\nSearch results for: "{search_tag}"')
    print(tabulate(sorted(results), headers=['Title', 'Lesson Name', 'Objectives', 'Matching Tag'], maxcolwidths=[30, 30, 30, 30], tablefmt="grid"))
    print(Style.RESET_ALL)    


#################
#    HISTORY    #
#################

def load_history():
    '''
    Returns the history.csv as a df.
    If it doesn't exist (e.g. following a `dojo clean`),
    then a new one shall be created and returned.
    '''
    history_path = os.path.join(ROOT_DIR, 'history.csv')
    if not os.path.exists(history_path):
        columns = ['timestamp', 'lesson_name', 'action', 'active', 'completed']
        df = pd.DataFrame(columns=columns)
        return df
    return pd.read_csv(os.path.join(ROOT_DIR, 'history.csv'), index_col=False)


def update_history(lesson_name, action):
    '''
    Adds a row to history.csv, recording the lesson_name
    and whether it was started, stopped, or completed 
    (and boolean of whether that lesson is active or not).
    '''
    df_history = load_history()
    ts = get_timestamp_for_action()

    if action == 'completed':
        active = False
        completed = True
    elif action == 'stop':
        active = False
        completed = False
    else:
        active = True
        completed = False

    new_row = {'timestamp': ts,
               'lesson_name': lesson_name,
               'action': action,
               'active': active,
               'completed': completed
              }
    df_history = df_history.append(new_row, ignore_index=True)
    df_history.to_csv(os.path.join(ROOT_DIR, 'history.csv'), index=False)


#################
#    LESSONS    #
#################

def load_curriculum_specs():
    curriculum_yaml_path = os.path.join(ROOT_DIR, 'curriculum.yaml')

    try:
        with open(curriculum_yaml_path, mode='r') as curriculum_specs:
            import yaml    # i.e. pyyaml
            return yaml.safe_load(curriculum_specs)
    except FileNotFoundError:
        print(f'ERROR: curriculum.yaml not found.')
        sys.exit(1)


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


def show_lessons(status=None):
    # Columns:
    # topic, title, lesson_name, objectives, author(s), tags
    curriculum_specs = load_curriculum_specs()

    results = []
    for topic, lessons in curriculum_specs['topics'].items():
        for lesson_name in lessons:
            lesson_specs = load_lesson_specs(lesson_name)
            title = lesson_specs['title']
            objectives = ' * '.join(str(obj) for obj in lesson_specs['objectives'])
            authors = ', '.join(str(author) for author in lesson_specs['authors'])
            tags = '; '.join(str(tag) for tag in lesson_specs['tags'])

            df_history = load_history()
            df_completed = df_history[(df_history.lesson_name == lesson_name) & (df_history.completed == True)]
            if df_completed.empty:
                completed = False
            else:
                completed = True

            result_row = [topic, title, lesson_name, objectives, authors, tags, completed]
            results.append(result_row)

    columns = ['Topic', 'Title', 'Lesson name', 'Objectives', 'Author(s)', 'Tags', 'Completed']
    df_results = pd.DataFrame(results, columns=columns)

    if status == 'authors':
        authors_column = df_results['Author(s)'].tolist()
        authors_for_lesson = [i.split(', ') for i in authors_column]
        author_instances = [name for lesson in authors_for_lesson for name in lesson]
        author_count = Counter(author_instances).most_common()
        print(Fore.YELLOW + '\nAuthors and the number of lessons they\'ve written')
        print('=================================================')
        for tally in author_count:
            print(f'{tally[0]}: {tally[1]}')
        print(Style.RESET_ALL)
        sys.exit(0)

    elif status == 'done':
        df_results_done = df_results[df_results['Completed'] == True]
        final = df_results_done.values.tolist()

    elif status == 'not_done':
        df_results_not_done = df_results[df_results['Completed'] == False]
        final = df_results_not_done.values.tolist()

    else:
        final = df_results.values.tolist()

    print(Fore.CYAN + tabulate(sorted(final), headers=columns, maxcolwidths=[30, 30, 30, 30, 30, 30, 30], tablefmt="grid"))
    print(Style.RESET_ALL)    

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

# IMPORTANT: If your lesson requires a snapshot of a channel(s) in a certain 
# state (e.g. missing some dependencies for python-3.9), then please make
# sure to add the URLs for the necessary packages in a `dojo_channels_pkgs.txt`
# file under the lesson directory. (See README for more details.) For example:
#
# dojo/
#   |---- lessons/
#           |---- 001_version_bump/
#                   |---- dojo_channels_pkgs.txt
#                   |---- lesson.yaml

# The lesson title.
# Example: "How to do a version bump"
title: 

# The person(s) who wrote this lesson.
authors: 
  - AUTHOR NAME

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

# Lesson prompts (or steps).
# List the propmpts/steps the learner should go through.
# You can also pose questions and answers (for example, one prompt is 
# a question, and the subsequent prompt is the answer to that question).
# BONUS: Provide hints to the learner (just tell them the hint will be 
# revealed in the next step if they want it).
prompts:
  - EXAMPLE - Open the meta.yaml...
  - EXAMPLE - Increment the build number...
  - |
    EXAMPLE step with multiline.

      Additional lines.

'''

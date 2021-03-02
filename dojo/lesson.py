'''
Interactions for and within a lesson.
'''
import os
import pandas as pd
import shutil
from dojo import ROOT_DIR, LESSONS_DIR, TRAINING_FEEDSTOCKS_DIR
from dojo.utils import get_latest, get_repodata_snapshot, \
    update_history, create_lesson_progress, get_lesson_progress, update_lesson_progress
from git import Repo


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
        print(f'Error: lesson.yaml for {lesson_name} not found.')
        sys.exit(1)


def clone_checkout_feedstock(feedstock_url, commit):
    '''
    Clones the lesson's feedstock and checks
    out the specified commmit.
    '''
    print('Setting up feedstock snapshot...')
    repo_name = feedstock_url.split('/')[-1].split('.git')[0]
    os.chdir(TRAINING_FEEDSTOCKS_DIR)

    print(f'Cloning {repo_name} at {commit}')
    clone_target_path = os.path.join(TRAINING_FEEDSTOCKS_DIR, repo_name)

    # Clone feedstock
    if os.path.isdir(clone_target_path):
        shutil.rmtree(clone_target_path)
    repo = Repo.clone_from(feedstock_url, clone_target_path)

    # Checkout commit
    repo.git.checkout(commit)

    os.chdir(ROOT_DIR)
    print('...success!')

    return clone_target_path


def create_lesson(lesson_name, target_platform, repodata_snapshot=False):

    subdirs = ['noarch', target_platform]

    if repodata_snapshot:
        get_repodata_snapshot(lesson_name, subdirs)

    pass


def display_prompt(contents, verbose=False):

    if verbose:
        title = contents['title']
        details = f'\nTitle: {title}'
        details += '\nObjectives:'
        for obj in contents['objectives']:
            details += f'\n  - {obj}'
        feedstock_path = contents['feedstock_path']
        details += f'\nRecipe path: {feedstock_path}/recipe'

    else:
        details = ''

    prompt_location = contents['prompt_location']
    prompt = contents['prompt']
    print('############### CONDA-BUILD DOJO ###############')
    print(details)
    print(f'\n(Step {prompt_location}) {prompt}')
    print(f'\nOPTIONS: dojo (p)revious step; (c)urrent step; (n)ext step; (a)dd note; (stop) lesson.')
    print('################################################')


def review(lesson_name):
    pass


def start(lesson_name):

    lesson_specs = load_lesson_specs(lesson_name)
    feedstock_url = lesson_specs['feedstock_url']
    commit = lesson_specs['commit']

    # Get feedstock.
    clone_target_path = clone_checkout_feedstock(feedstock_url, commit)

    # If modified_repodata == True, 
    # edit the .condarc to point to local repodata.
    if lesson_specs['modified_repodata']:
        # Alter .condarc
        pass

    # Update history.csv.
    update_history(lesson_name, 'start')

    # Create lesson progress.csv.
    create_lesson_progress(lesson_name)

    # Display lesson info and step 1. (Indicate progress, e.g. "Step 1 of 12")
    total_num_prompts = len(lesson_specs['prompts'])
    contents = {'title': lesson_specs['title'],
                'objectives': lesson_specs['objectives'],
                'target_package': lesson_specs['target_package'],
                'feedstock_path': clone_target_path,
                'prompt_location': f'1 of {total_num_prompts}',
                'prompt': lesson_specs['prompts'][0],
               }
    display_prompt(contents, verbose=True)


def step_previous(verbose=False):
    # If verbose, show all info and previously completed steps too.

    pass


def step_current(verbose=False):
    # If verbose, show all info and previously completed steps too.
    pass


def step_next(verbose=False):
    # If verbose, show all info.
    pass


def step_add_note():
    pass


def stop():
    # Update history.csv.
    update_history(lesson_name, 'stop')




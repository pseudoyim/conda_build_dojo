'''
Interactions for and within a lesson.
'''
import os
import pandas as pd
import shutil
import sys
from dojo import ROOT_DIR, LESSONS_DIR, TRAINING_FEEDSTOCKS_DIR
from dojo.utils import get_latest, get_repodata_snapshot, \
    update_history, create_lesson_progress, get_lesson_progress, update_lesson_progress
from git import Repo


def clone_checkout_feedstock(feedstock_url, commit):
    '''
    Clones the lesson's feedstock and checks
    out the specified commmit.
    '''
    print('Setting up feedstock snapshot...')
    repo_name = get_repo_name(feedstock_url)
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
    '''
    Creates a lesson directory, a lesson.yaml, and (optionally)
    a snapshot of repodata that can be edited.
    '''
    subdirs = ['noarch', target_platform]

    if repodata_snapshot:
        get_repodata_snapshot(lesson_name, subdirs)

    pass


def display_prompt(lesson_name, lesson_specs, step_index, verbose=False):

    repo_name = get_repo_name(lesson_specs['feedstock_url'])
    recipe_path = os.path.join(TRAINING_FEEDSTOCKS_DIR, repo_name, 'recipe')

    # Display lesson info and step 1. (Indicate progress, e.g. "Step 1 of 12")
    total_num_prompts = len(lesson_specs['prompts'])

    # contents = {'title': lesson_specs['title'],
    #             'objectives': lesson_specs['objectives'],
    #             'target_package': lesson_specs['target_package'],
    #             'feedstock_path': feedstock_path,
    #             'prompt_location': f'{step_index + 1} of {total_num_prompts}',
    #             'prompt': lesson_specs['prompts'][step_index],
    #            }

    if verbose:
        details = f'\nTitle: {lesson_specs["title"]}'
        details += '\nObjectives:'
        for obj in lesson_specs['objectives']:
            details += f'\n  - {obj}'
        details += f'\nRecipe path: {recipe_path}'

    else:
        details = None

    prompt_location = f'{step_index + 1} of {total_num_prompts}'
    prompt = lesson_specs['prompts'][step_index]

    print('\n=============== CONDA-BUILD DOJO ===============')
    if details:
        print(details)
    print(f'\n(Step {prompt_location}) {prompt}')
    print('\n================================================')
    print(f'OPTIONS: dojo (p)revious step; (c)urrent step; (n)ext step; (a)dd note; (stop) lesson.')


def get_repo_name(feedstock_url):
    return feedstock_url.split('/')[-1].split('.git')[0]


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


def review(lesson_name):
    print('dojo review (NOT YET IMPLEMENTED)')
    pass


def start(lesson_name):
    # Check whether a progress.csv already exists (which would mean
    # they've started this lesson before). 
    # If so, ask whether they want to resume or start over.
    if os.path.exists(os.path.join(LESSONS_DIR, lesson_name, 'progress.csv')):
        while True:
            user_response = str(input(f'You previously started "{lesson_name}". Do you wish to (c)ontinue where you left off, or (s)tart over? '))
            if user_response.lower() not in ['c', 's']:
                print('Sorry, I did not understand.')
            else:
                break
        if user_response.lower() == 'c':
            update_history(lesson_name, 'resume')
            step_current(verbose=True)
        elif user_response.lower() == 's':
            update_history(lesson_name, 'start over')
            update_lesson_progress(lesson_name, 0)
            step_current(verbose=True)

    else:
        lesson_specs = load_lesson_specs(lesson_name)
        feedstock_url = lesson_specs['feedstock_url']
        commit = lesson_specs['commit']

        # Get feedstock.
        clone_target_path = clone_checkout_feedstock(feedstock_url, commit)

        # If modified_repodata == True, 
        # edit the .condarc to point to local repodata.
        if lesson_specs['modified_repodata']:
            # Alter .condarc
            print('Modify .condarc (NOT YET IMPLEMENTED)')
            pass

        # Update history.csv.
        update_history(lesson_name, 'start')

        # Create lesson progress.csv.
        create_lesson_progress(lesson_name)

        # Start at index 0.
        step_index = 0

        display_prompt(lesson_name, lesson_specs, step_index, verbose=True)


def step_previous(verbose=False):
    # Read history.csv to lookup which lesson is active,
    
    # Go to that lesson's progress.csv to lookup
    # the current step they're on. 
    
    # Then go to previous step.

    # If verbose, show all info and previously completed steps too.
    pass


def step_current(verbose=False):
    # If verbose, show all info and previously completed steps too.
    last_move = get_latest()


def step_next(verbose=False):
    # If verbose, show all info.
    pass


def step_add_note():
    print('Add note (NOT YET IMPLEMENTED)')
    pass


def stop():
    # Update history.csv.
    update_history(lesson_name, 'stop')




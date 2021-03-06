'''
Interactions for and within a lesson.
'''
import os
import pandas as pd
import shutil
import sys
from dojo import ROOT_DIR, LESSONS_DIR, TRAINING_FEEDSTOCKS_DIR
from dojo.utils import add_lesson_yaml, get_latest, get_repodata_snapshot, \
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


def create_lesson(new_lesson_name, target_platform, repodata_snapshot=False):
    '''
    Creates a lesson directory, a lesson.yaml, and (optionally)
    a snapshot of repodata that can be edited.
    '''
    subdirs = ['noarch', target_platform]

    # Create lesson directory (increments from last lesson's number).
    last_lesson_number = get_last_lesson_number()
    new_lesson_number_str = str(last_lesson_number + 1)
    new_lesson_number_str = new_lesson_number_str.zfill(3)
    new_lesson_folder = f'{new_lesson_number_str}_{new_lesson_name}'
    new_lesson_path = os.path.join(LESSONS_DIR, new_lesson_folder)
    os.mkdir(new_lesson_path)

    # Add a lesson.yaml (will need to be edited by the lesson creator).
    add_lesson_yaml(new_lesson_path)

    # Download and save repodata snapshot, if specified.
    if repodata_snapshot:
        get_repodata_snapshot(new_lesson_folder, subdirs)

    # Show info about where to find the new directory and next steps.
    print(f'New lesson created at: {new_lesson_path}')
    print('In this directory, you will find the "lesson.yaml". Please add your lesson content in this file.')
    if repodata_snapshot:
        print(f'You also created a repodata snapshot to use in your lesson (see {new_lesson_path}/dojo_repodata).')
        print('Please use the "dojo prune_repodata" command to edit this repodata.')


def display_prompt(lesson_name, lesson_specs, step_index, verbose=False):

    repo_name = get_repo_name(lesson_specs['feedstock_url'])
    recipe_path = os.path.join(TRAINING_FEEDSTOCKS_DIR, repo_name, 'recipe')

    # Display lesson info and step 1. (Indicate progress, e.g. "Step 1 of 12")
    total_num_prompts = len(lesson_specs['prompts'])

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
    print(f'OPTIONS: dojo (p)revious; (c)urrent; (n)ext; (j)ump; (a)dd note; (stop) lesson.')


def get_last_lesson_number():
    from glob import glob
    all_lesson_dirs = glob(os.path.join(LESSONS_DIR,'*'))
    return max([int(n.split('/')[-1].split('_')[0]) for n in all_lesson_dirs])


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


def step_jump(step_number, verbose=False):
    # If verbose, show all info.
    pass


def step_add_note():
    print('Add note (NOT YET IMPLEMENTED)')
    pass


def stop():
    # Update history.csv.
    update_history(lesson_name, 'stop')




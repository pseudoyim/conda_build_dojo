'''
Interactions for and within a lesson.
'''
import os
import pandas as pd
import shutil
import sys
from dojo import ROOT_DIR, LESSONS_DIR, TRAINING_FEEDSTOCKS_DIR
from dojo.utils import add_lesson_yaml, get_latest, get_repodata_snapshot, \
    update_history, create_lesson_progress, get_all_lesson_progress, \
    get_lesson_progress, load_lesson_specs, update_lesson_progress
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

    # Create lesson directory (increments from the last lesson's number).
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
    '''
    Displays the lesson name and step info, and (if specified) additional
    details about the lesson.
    Also shows any notes entered for the step.
    '''
    if verbose:
        details = 'Objectives:'
        for obj in lesson_specs['objectives']:
            details += f'\n  - {obj}'
        repo_name = get_repo_name(lesson_specs['feedstock_url'])
        recipe_path = os.path.join(TRAINING_FEEDSTOCKS_DIR, repo_name, 'recipe')
        details += f'\nRecipe path: {recipe_path}'
    else:
        details = None

    # Step prompt.
    total_num_prompts = len(lesson_specs['prompts'])
    prompt_location = f'{step_index + 1} of {total_num_prompts}'
    prompt = lesson_specs['prompts'][step_index]

    # Get any notes that exist for current step_index.
    df_progress = get_all_lesson_progress(lesson_name)
    df_rows_with_notes = df_progress[(df_progress['lesson_index']==step_index) & (df_progress.note.notnull())]
    rows_with_notes = df_rows_with_notes.values.tolist()
    
    if rows_with_notes:
        notes = '\nMy notes:'
        for note in rows_with_notes:
            date = note[1].split(' ')[0]
            content = note[3]
            notes += f'\n  - ({date}) {content}'
    else: 
        notes = None

    print('\n=============================== CONDA-BUILD DOJO ===============================')
    print(f'\nLesson: "{lesson_specs["title"]}"')
    if details:
        print(details)
    print(f'\nStep {prompt_location}')
    print(f'\n{prompt}')
    if notes:
        print(notes)
    print('\n================================================================================')
    print(f'OPTIONS: dojo (p)revious; (c)urrent; (n)ext; (j)ump; (a)dd note; (stop) lesson.\n')


def get_last_lesson_number():
    '''
    Gets the number of the last created lesson (e.g. 001).
    To be used when running 'dojo create_lesson'.
    '''
    from glob import glob
    all_lesson_dirs = glob(os.path.join(LESSONS_DIR,'*'))
    return max([int(n.split('/')[-1].split('_')[0]) for n in all_lesson_dirs])


def get_repo_name(feedstock_url):
    '''
    Parses the repo name from the feedstock URL.
    '''
    return feedstock_url.split('/')[-1].split('.git')[0]


def setup_feedstock_and_condarc(lesson_name):
    lesson_specs = load_lesson_specs(lesson_name)
    feedstock_url = lesson_specs['feedstock_url']
    commit = lesson_specs['commit']

    # Clone feedstock and checkout to specifiec commit.
    clone_checkout_feedstock(feedstock_url, commit)

    # If modified_repodata == True,
    # edit the .condarc to point to local repodata.
    if lesson_specs['modified_repodata']:
        # Alter .condarc
        print('Modify .condarc (NOT YET IMPLEMENTED)')
        pass


def start(lesson_name):
    '''
    Starts a new lesson by setting up the feedstock and condarc.
    Also checks if a user already started the specified lesson 
    and handles accordingly.
    '''
    lesson_specs = load_lesson_specs(lesson_name)
    feedstock_url = lesson_specs['feedstock_url']
    commit = lesson_specs['commit']

    # Check whether a progress.csv already exists (which would mean
    # they've started this lesson before). 
    # If so, ask whether they want to resume or start over.
    if os.path.exists(os.path.join(LESSONS_DIR, lesson_name, 'progress.csv')):
        while True:
            user_response = str(input(f'You previously started "{lesson_name}". \nDo you wish to (r)esume, (s)tart over, or (c)ancel? '))
            if user_response.lower() not in ['c', 's']:
                print('Sorry, I did not understand.')
            else:
                break
        if user_response.lower() == 'r':
            setup_feedstock_and_condarc(lesson_name)
            update_history(lesson_name, 'resume')
            step_current(verbose=True)
        elif user_response.lower() == 's':
            setup_feedstock_and_condarc(lesson_name)
            update_history(lesson_name, 'start over')
            update_lesson_progress(lesson_name, 0)
            step_current(verbose=True)
        elif user_response.lower() == 'c':
            sys.exit(0)

    else:
        setup_feedstock_and_condarc(lesson_name)
        update_history(lesson_name, 'start')
        create_lesson_progress(lesson_name)
        display_prompt(lesson_name, lesson_specs, 0, verbose=True)


def step_previous(verbose=False):
    '''
    Show the previous step.
    '''
    lesson_name, current_step_index = get_latest()
    if current_step_index > 0:
        new_step_index = current_step_index - 1
    else:
        new_step_index = 0
    lesson_specs = load_lesson_specs(lesson_name)

    update_lesson_progress(lesson_name, new_step_index)

    display_prompt(lesson_name, lesson_specs, new_step_index, verbose=verbose)


def step_current(verbose=False):
    '''
    Show the current step.
    '''
    lesson_name, current_step_index = get_latest()
    lesson_specs = load_lesson_specs(lesson_name)
    display_prompt(lesson_name, lesson_specs, current_step_index, verbose=verbose)


def step_next(verbose=False):
    '''
    Show the next step.
    If at the end, the next step is a congratulatory message
    and advice on what to do now.
    '''
    lesson_name, current_step_index = get_latest()
    lesson_specs = load_lesson_specs(lesson_name)
    max_step_index = len(lesson_specs['prompts']) - 1

    if current_step_index == max_step_index:
        # There are no more steps, so the lesson is done.
        lesson_title = lesson_specs['title']
        update_history(lesson_name, 'completed')
        print(f'\n+ + + + Congrats! You have completed "{lesson_title}". + + + +')
        print('You can review this lesson (and any notes you added) by re-starting the lesson.')
        print('Otherwise, onward and upward to a new lesson!\n')
        sys.exit(0)

    new_step_index = current_step_index + 1
    update_lesson_progress(lesson_name, new_step_index)
    display_prompt(lesson_name, lesson_specs, new_step_index, verbose=verbose)


def step_jump(step_number, verbose=False):
    '''
    Jump to a specified step number.
    '''
    lesson_name, current_step_index = get_latest()
    lesson_specs = load_lesson_specs(lesson_name)
    max_step_number = len(lesson_specs['prompts'])

    if (int(step_number) > max_step_number) or (int(step_number) < 1):
        print('ERROR: That step number does not exist.')
        sys.exit(1)

    new_step_index = int(step_number) - 1
    update_lesson_progress(lesson_name, new_step_index)
    display_prompt(lesson_name, lesson_specs, new_step_index, verbose=verbose)


def step_add_note():
    '''
    Add a note to current step_index in the progress.csv
    '''
    lesson_name, current_step_index = get_latest()
    lesson_specs = load_lesson_specs(lesson_name)

    # Get note from the user.
    note = str(input('Please enter your note: '))

    # Record note in progress.csv.
    update_lesson_progress(lesson_name, current_step_index, note=note)

    # Display the current step with the new note.
    display_prompt(lesson_name, lesson_specs, current_step_index)

    print(f'Added note to {os.path.join(LESSONS_DIR, lesson_name, "progress.csv")}')
    print('To edit or delete the note, please do so in the csv file itself.')


def stop():
    '''
    Stop the lesson.
    '''
    lesson_name, _ = get_latest()
    
    # Update history.csv.
    update_history(lesson_name, 'stop')

    # TODO: If lesson_spec had modified_repodata=True, revert .condarc file to point to defaults.

    print(f'Stopped lesson: {lesson_name}')

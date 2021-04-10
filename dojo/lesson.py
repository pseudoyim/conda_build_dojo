'''
Interactions for and within a lesson.
'''
import os
import pandas as pd
import shutil
import sys
from dojo import ROOT_DIR, LESSONS_DIR, TRAINING_FEEDSTOCKS_DIR
from dojo.utils import add_lesson_yaml, download_package, get_latest, \
    update_history, create_lesson_progress, get_all_lesson_progress, 
    get_lesson_progress, get_timestamp_for_file, \
    load_lesson_specs, update_lesson_progress
from git import Repo


def clean_dojo_channels(lesson_name):
    # If dojo_channels directory exists, delete it.
    dojo_channels_path = os.path.join(LESSONS_DIR, lesson_name, 'dojo_channels')
    if os.path.isdir(dojo_channels_path):
        print('Removing dojo_channels directory...')
        shutil.rmtree(dojo_channels_path)
        print('...success!')


def clone_checkout_feedstock(feedstock_url, commit):
    '''
    Clones the lesson's feedstock and checks
    out the specified commmit.
    '''
    print('\nSetting up feedstock snapshot...')
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
    print('...successfully set up feedstock snapshot!')

    return clone_target_path


def create_lesson(new_lesson_name, target_platform):
    '''
    Creates a lesson directory and a lesson.yaml.
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

    # Show info about where to find the new directory and next steps.
    print(f'New lesson created at: {new_lesson_path}')
    print('In this directory, you will find the "lesson.yaml". Please add your lesson content in this file.')


def display_prompt(lesson_name, lesson_specs, step_index, verbose=False):
    '''
    Displays the lesson name and step info, and (if specified) additional
    details about the lesson.
    Also shows any notes entered for the step.
    '''
    if verbose:
        details = '  Objectives:'
        for obj in lesson_specs['objectives']:
            details += f'\n    - {obj}'
        repo_name = get_repo_name(lesson_specs['feedstock_url'])
        recipe_path = os.path.join(TRAINING_FEEDSTOCKS_DIR, repo_name, 'recipe')
        details += f'\n  Recipe path: {recipe_path}'
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
        notes = '\n  My notes:'
        for note in rows_with_notes:
            date = note[1].split(' ')[0]
            content = note[3]
            notes += f'\n    - ({date}) {content}'
    else: 
        notes = None

    print('\n=============================== CONDA-BUILD DOJO ===============================')
    print('||                                                                            ||')
    print(f'\n  Lesson: "{lesson_specs["title"]}"')
    if details:
        print(details)
    print(f'\n  Step {prompt_location}')
    print(f'\n{prompt}')
    if notes:
        print(notes)
    print('\n||                                                                            ||')
    print('================================================================================')
    print(f' OPTIONS: dojo (p)revious; (c)urrent; (n)ext; (j)ump; (a)dd note; (stop) lesson.\n')


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

    # Set up dojo_channels (only if "dojo_channels_pkgs.txt" file exists and it's not empty):
    dojo_channels_pkgs = os.path.join(LESSONS_DIR, lesson_name, 'dojo_channels_pkgs.txt')
    if os.path.exists(dojo_channels_pkgs) and os.stat(dojo_channels_pkgs).st_size > 0:
        print('\nSetting up dojo_channels...')

        # Parse each URL to get its channel, subdir, and filename. For example: 
        # {
        #  'https://repo.anaconda.com/pkgs/main/linux-64/python-3.9.2-hdb3f193_0.conda': 
        #     {
        #      'channel': 'main', 
        #      'subdir' : 'linux-64',
        #      'fn' : 'python-3.9.2-hdb3f193_0.conda'
        #     }
        # }
        url_parsed_dict = {}
        
        with open(dojo_channels_pkgs, 'r') as url_list:
            urls = url_list.read().splitlines()
            for url in urls:
                
                channel = url.split('/')[-3]
                subdir = url.split('/')[-2]
                fn = url.split('/')[-1]
                url_parsed_dict[url] = {'channel': channel, 'subdir': subdir, 'fn': fn}

        # Download each URL to the appropriate destination path.
        for pkg_url, url_parts in url_parsed_dict.items():
            destination_path = os.path.join(LESSONS_DIR, 
                                            lesson_name, 
                                            'dojo_channels', 
                                            url_parts['channel'], 
                                            url_parts['subdir'], 
                                            url_parts['fn'])
            download_package(pkg_url, destination_path)

        # Run `conda index` on each dojo channel.
        from glob import glob
        dojo_channels = glob(os.path.join(LESSONS_DIR,lesson_name, 'dojo_channels', '*'))
        for dojo_channel_path in dojo_channels:
            import subprocess
            print(f'Running "conda index" on {dojo_channel_path}')
            subprocess.run(['conda', 'index', dojo_channel_path])

        # If a .condarc exists, back it up.
        home_path = os.environ['HOME']
        condarc_path = os.path.join(home_path, '.condarc')
        if os.path.exists(condarc_path):
            ts = get_timestamp_for_file()
            renamed_condarc_path = os.path.join(home_path, f'.condarc_bak_{ts}')
            os.rename(condarc_path, renamed_condarc_path)
            print('Found an existing .condarc file.')
            print(f'Backing it up to: {renamed_condarc_path}')

        # Create a .condarc that points to the lesson's dojo_channels.
        with open(condarc_path, 'w') as new_condarc:
            new_condarc.write('channels: \n')  # Must have a space after the colon. See: https://stackoverflow.com/a/9055411
            for channel in dojo_channels:
                new_condarc.write(f'  - {channel}\n')

        print('...successfully set up dojo_channels!')


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
    # If so, ask whether they want to resume, start over, or cancel.
    if os.path.exists(os.path.join(LESSONS_DIR, lesson_name, 'progress.csv')):
        while True:
            user_response = str(input(f'You previously started "{lesson_name}". \nDo you wish to (r)esume, (s)tart over, or (c)ancel? '))
            if user_response.lower() not in ['c', 's']:
                print('Sorry, I did not understand.')
            else:
                break
        if user_response.lower() == 'r':  # Resume
            setup_feedstock_and_condarc(lesson_name)
            update_history(lesson_name, 'resume')
            step_current(verbose=True)
        elif user_response.lower() == 's':  # Start over
            setup_feedstock_and_condarc(lesson_name)
            update_history(lesson_name, 'start over')
            update_lesson_progress(lesson_name, 0)
            step_current(verbose=True)
        elif user_response.lower() == 'c':  # Cancel
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
        print(f'\nYou should now be able to:')
        for obj in lesson_specs['objectives']:
            print(f'  - {obj}')
        print('\nYou can review this lesson (and any notes you added) by re-starting the lesson.')
        print('Otherwise, onward and upward to a new lesson!\n')
        stop(completed_lesson_name=lesson_name)
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


def stop(completed_lesson_name=None):
    '''
    Stop the lesson and clean up its dojo_channels dir (if it exists).
    '''
    if completed_lesson_name:
        clean_dojo_channels(completed_lesson_name)

    else:  # User is stopping the lesson before finishing it.
        lesson_name, _ = get_latest()
        update_history(lesson_name, 'stop')
        clean_dojo_channels(lesson_name)
        print(f'Stopped lesson: {lesson_name}')


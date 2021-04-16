import argparse
import sys
from dojo.utils import search_tag, show_lessons
from dojo.lesson import start, stop, step_previous, step_current, \
    step_next, step_jump, step_add_note, create_lesson, clean_history_and_progress


def main():
    p = argparse.ArgumentParser(
            description='Conda-Build Dojo guides you through debugging scenarios encountered during package building.',
            usage='dojo'
            )
    p.add_argument(
            '-v', '--version',
            action='version',
            version='dojo 0.1.0'
            )

    subparsers = p.add_subparsers(dest='subcommand')

    # Subcommand: lessons
    help_msg_lessons = '''View all available lessons (for current platform).'''
    subcmd_lessons = subparsers.add_parser('lessons', help=help_msg_lessons)
    subcmd_lessons.add_argument(
        '--all',
        help='Show all lessons.',
        action='store_true',
        )
    subcmd_lessons.add_argument(
        '--done',
        help='Show the lessons you have completed.',
        action='store_true',
        )
    subcmd_lessons.add_argument(
        '--not-done',
        help='Show the lessons you have not yet completed.',
        action='store_true',
        )
    subcmd_lessons.add_argument(
        '--authors',
        help='Show author stats.',
        action='store_true',
        )

    # Subcommand: search
    help_msg_search = '''Search for lessons based on a tag.'''
    subcmd_search = subparsers.add_parser('search', help=help_msg_search)
    subcmd_search.add_argument(
        'tag',
        help='Search lessons for this tag.',
        )

    # Subcommand: start
    help_msg_start = '''Start a lesson.'''
    subcmd_start = subparsers.add_parser('start', help=help_msg_start)
    subcmd_start.add_argument(
        'lesson_name',
        help='Name of lesson to start.',
        )

    # Subcommand: stop
    help_msg_stop = '''Stop the current lesson.'''
    subcmd_stop = subparsers.add_parser('stop', help=help_msg_stop)

    # Subcommand: previous
    help_msg_previous = '''(p)revious: Go to previous step in current lesson.'''
    subcmd_previous = subparsers.add_parser('p', help=help_msg_previous)
    subcmd_previous.add_argument(
        '-v',
        '--verbose',
        help='Include all info about the current lesson.',
        action='store_true',
        )

    # Subcommand: current
    help_msg_current = '''(c)urrent: Go to current step in current lesson.'''
    subcmd_current = subparsers.add_parser('c', help=help_msg_current)
    subcmd_current.add_argument(
        '-v',
        '--verbose',
        help='Include all info about the current lesson.',
        action='store_true',
        )

    # Subcommand: next
    help_msg_next = '''(n)ext: Go to next step in current lesson.'''
    subcmd_next = subparsers.add_parser('n', help=help_msg_next)
    subcmd_next.add_argument(
        '-v',
        '--verbose',
        help='Include all info about the current lesson.',
        action='store_true',
        )

    # Subcommand: jump
    help_msg_jump = '''(j)ump: Jump to a specific step in the current lesson.'''
    subcmd_jump = subparsers.add_parser('j', help=help_msg_jump)
    subcmd_jump.add_argument(
        'step_number',
        help='The step number to jump to in the current lesson.',
        )
    subcmd_jump.add_argument(
        '-v',
        '--verbose',
        help='Include all info about the current lesson.',
        action='store_true',
        )

    # Subcommand: add_note
    help_msg_add_note = '''(a)dd: Add a note to the current step.'''
    subcmd_add_note = subparsers.add_parser('a', help=help_msg_add_note)

    # Subcommand: create_lesson
    help_msg_create_lesson = '''Create a new lesson.'''
    subcmd_create_lesson = subparsers.add_parser('create_lesson', help=help_msg_create_lesson)
    subcmd_create_lesson.add_argument(
        '--name',
        help='Short name of the lesson (use underscores instead of spaces). For example: "creating_a_patch".',
        )

    # Subcommand: clean
    help_msg_clean = '''(For dev only) Delete all progress.csv files and history.csv.'''
    subcmd_history = subparsers.add_parser('clean', help=help_msg_clean)

    args = p.parse_args()

    if args.subcommand == 'lessons':
        if args.all:
            status = 'all'
        elif args.done:
            status = 'done'
        elif args.not_done:
            status = 'not_done'
        elif args.authors:
            status = 'authors'
        else:
            status = 'all'
        show_lessons(status=status)

    elif args.subcommand == 'search':
        search_tag(args.tag)

    elif args.subcommand == 'start':
        start(args.lesson_name)

    elif args.subcommand == 'p':
        step_previous(verbose=args.verbose)

    elif args.subcommand == 'c':
        step_current(verbose=args.verbose)

    elif args.subcommand == 'n':
        step_next(verbose=args.verbose)

    elif args.subcommand == 'j':
        step_jump(args.step_number, verbose=args.verbose)

    elif args.subcommand == 'a':
        step_add_note()

    elif args.subcommand == 'stop':
        stop()

    elif args.subcommand == 'create_lesson':
        # Validate input.
        if ' ' in args.name:
            print(f'Invalid lesson name: "{args.name}". Please use underscores instead of spaces.')
            sys.exit(1)
        create_lesson(args.name, args.target_platform)

    elif args.subcommand == 'clean':
        clean_history_and_progress()

    else:
        print('Invalid subcommand.')
        sys.exit(1)


if __name__ == '__main__':
    main()
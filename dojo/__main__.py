import argparse
import sys
from dojo.utils import show_history, show_lessons, prune_repodata
from dojo.lesson import start, stop, step_previous, step_current, \
    step_next, step_jump, step_add_note, create_lesson


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

    # Subcommand: history
    help_msg_history = '''Shows which lessons you've started and completed.'''
    subcmd_history = subparsers.add_parser('history', help=help_msg_history)

    # Subcommand: lessons
    help_msg_lessons = '''Shows all available lessons (for current platform).'''
    subcmd_lessons = subparsers.add_parser('lessons', help=help_msg_lessons)
    subcmd_lessons.add_argument(
        '--all',
        help='Show all lessons for all platforms.',
        action='store_true',
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
        )

    # Subcommand: current
    help_msg_current = '''(c)urrent: Go to current step in current lesson.'''
    subcmd_current = subparsers.add_parser('c', help=help_msg_current)
    subcmd_current.add_argument(
        '-v',
        '--verbose',
        help='Include all info about the current lesson.',
        )

    # Subcommand: next
    help_msg_next = '''(n)ext: Go to next step in current lesson.'''
    subcmd_next = subparsers.add_parser('n', help=help_msg_next)
    subcmd_next.add_argument(
        '-v',
        '--verbose',
        help='Include all info about the current lesson.',
        )

    # Subcommand: jump
    help_msg_jump = '''(j)ump to a specific step in the current lesson.'''
    subcmd_jump = subparsers.add_parser('j', help=help_msg_jump)
    subcmd_jump.add_argument(
        'step_number',
        help='The step number to jump to in the current lesson.',
        )
    subcmd_jump.add_argument(
        '-v',
        '--verbose',
        help='Include all info about the current lesson.',
        )

    # Subcommand: add_note
    help_msg_add_note = '''(a)dd: Add a note to the current step.'''
    subcmd_add_note = subparsers.add_parser('a', help=help_msg_add_note)

    # Subcommand: create_lesson
    # (This command is not listed in --help)
    subcmd_create_lesson = subparsers.add_parser('create_lesson', help=argparse.SUPPRESS)
    subcmd_create_lesson.add_argument(
        '--name',
        help='Short name of the lesson (use underscores instead of spaces). For example: "creating_a_patch".',
        )
    subcmd_create_lesson.add_argument(
        '--repodata-snapshot',
        action='store_true',
        help='Whether to include a snapshot of the current repodata.json file from defaults.',
        )
    subcmd_create_lesson.add_argument(
        '--target-platform',
        help='(Required for repodata snapshot) Platform the lesson should be run on (options: linux-64, osx-64, and win-64).',
        )  

    # Subcommand: prune_repodata
    # (This command is not listed in --help)
    subcmd_prune_repodata = subparsers.add_parser('prune_repodata', help=argparse.SUPPRESS)

    args = p.parse_args()

    if args.subcommand == 'history':
        # run history
        show_history()

    elif args.subcommand == 'lessons':
        # run lessons
        show_lessons()

    elif args.subcommand == 'start':
        start(args.lesson_name)

    elif args.subcommand == 'p':
        # run (p)revious step
        step_previous(verbose=args.verbose)

    elif args.subcommand == 'c':
        # run (c)urrent step
        step_current(verbose=args.verbose)

    elif args.subcommand == 'n':
        # run (n)ext step
        step_next(verbose=args.verbose)

    elif args.subcommand == 'j':
        # run jump
        step_jump(args.step_number, verbose=args.verbose)

    elif args.subcommand == 'a':
        # run (a)dd note to current step
        pass

    elif args.subcommand == 'stop':
        # run stop lesson
        pass

    elif args.subcommand == 'create_lesson':
        # run create_lesson
        if ' ' in args.name:
            print(f'Invalid lesson name: "{args.name}". Please use underscores instead of spaces.')
            sys.exit(1)
        create_lesson(args.name, args.target_platform, repodata_snapshot=args.repodata_snapshot)

    elif args.subcommand == 'prune_repodata':
        # run prune_repodata
        # --lesson
        # --subdir
        # --filenames, -f
        # --namespaces, -n
        # --versions, -v
        pass

    else:
        print('Invalid subcommand.')
        sys.exit(1)


if __name__ == '__main__':
    main()
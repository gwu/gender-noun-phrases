#!/usr/bin/env python3
"""
Runs the phrase grouper (group_phrases.py) over several iterations.

The group_phrases.py script reads a reconstructed dialogs file and
produces a list of groups, each a list of phrases that appear in the
same context. It is useful to then run the group_phrases.py script
again passing in that list of groups as input so that it can consider
phrases from the same group as being the "same" when comparing word
contexts.

This script repeatedly runs the group_phrases.py script, passing in
the previous iteration's result each time. You can specify how many
iterations to run.
"""

import argparse
import subprocess


def parse_command_line_args():
  """Parse command line arguments"""
  parser = argparse.ArgumentParser(
    description='Run phrase grouper over several iterations.'
  )
  parser.add_argument(
    '--dialogs',
    default='reconstructed_dialogs.txt',
    help='path to reconstructed_dialogs.txt file'
  )
  parser.add_argument(
    '--context-size',
    type=int,
    default=3,
    help='number of words before and after each word to use as context'
  )
  parser.add_argument(
    '--phrase-size',
    type=int,
    default=1,
    help='max number of words in a phrase'
  )
  parser.add_argument(
    '--iterations',
    type=int,
    default=1,
    help='number of iterations to run'
  )
  parser.add_argument(
    '--group-name-pattern',
    default='grouped_phrases_{}.txt',
    help='patternfor the filename of each iteration of grouped phrases'
  )
  return parser.parse_args()


def main():
  """Main entry point of the app"""
  args = parse_command_line_args()

  for iteration_number in range(args.iterations):
    groups_filename = args.group_name_pattern.format(iteration_number)
    groups_file = open(groups_filename, 'w')

    # Set up the command line args to the group_phrases.py subprocess.
    subprocess_args = [
      'pipenv', 'run', 'python3', 'group_phrases.py',
      '--dialogs', args.dialogs,
      '--context-size', str(args.context_size),
      '--phrase-size', str(args.phrase_size),
    ]
    if iteration_number > 0:
      subprocess_args.extend(
        ['--groups', args.group_name_pattern.format(iteration_number - 1)]
      )

    # Call the group_phrases.py script.
    print('Starting iteration 1 with args {}'.format(subprocess_args))
    return_code = subprocess.call(
      subprocess_args,
      stdout=groups_file
    )

    # Finish writing this iteration's group file.
    groups_file.close()

    print('Iteration {} completed with return code {}'.format(iteration_number, return_code))
    print('Resulting groups written to {}'.format(groups_filename))


if __name__ == "__main__":
  """This is executed when run from the comand line"""
  main()

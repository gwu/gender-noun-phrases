#!/usr/bin/env python3
"""
Reconstruct Cornell Movie Dialog Corpus Converations

In order to accurately extract the male and female noun phrases from
the cornell movie dialog corpus, we need to reconstruct the
conversations from the movies in chronological order (and mark the
boundaries between separate conversations), so that a subsequent
parser can figure out what 'he' and 'she' refer to.

The raw dataset from the cornell movie dialog corpus has three relevant
files that we need to use. movie_lines is a list of lines from dialogs
in various movies, with IDs specifying which movie and character they
came from. movie_conversations.txt contains collections of IDs that
refer to the chronological order in which lines from movie_lines.txt
are used to reconstruct the actual conversations. Finally,
movie_characters_metadata.txt contains the list of characters and
whether they are male, female, or unknown.

The goal of this script is to produce a single file with a list of
conversations, where each conversation is a series of lines that were
uttered in chronological order.

The format should be:

f: some line that was uttered by a female character
m: some line that was uttered by a male character
?: some line that was uttered by a character of unspecified/unknown gender

f: a line from another conversation
f: yet another line from another conversation
(and so on...)

Note that conversations are separated by a blank line.

To create reconstructed_dialogs.txt using this script:

$ ./reconstruct_dialogs.py \
    --characters=cornell-movie-dialogs-corpus/movie_characters_metadata.txt \
    --lines=cornell-movie-dialogs-corpus/movie_lines.txt \
    --conversations=cornell-movie-dialogs-corpus/movie_conversations.txt \
    > reconstructed_dialogs.txt
"""

import argparse
import ast


FILE_COLUMN_SEPARATOR = ' +++$+++ '


def read_file_lines(path, line_reader):
  """Reads a file one line at a time.

  Args:
    line_reader ((str) -> None): Function called for each line in the file
  """

  with open(path, 'r', encoding='latin-1') as file_object:
    line = file_object.readline()
    while line:
      line_reader(line)
      line = file_object.readline()


def parse_characters_file_line(line):
  """Parse a line from the movie_characters_metadata.txt file

  Example line from the file:
    u0 +++$+++ BIANCA +++$+++ m0 +++$+++ 10 things i hate about you +++$+++ f +++$+++ 4

  Returns:
    (tuple of str): The character id (e.g. 'u123') and their gender (i.e. 'm'/'f'/'?')
  """

  columns = line.split(FILE_COLUMN_SEPARATOR)
  return columns[0], columns[4]


def parse_characters_file(path):
  """Parse the movie_characters_metadata.txt file

  Args:
    path (str): File path for movie_characters_metadata.txt.

  Returns:
    (dict of str: str): Map from character id (e.g. 'u123') to whether they are
      male/female/unknown ('m'/'f'/'?').
  """

  character_gender_map = {}

  def read_line(line):
    character_id, character_gender = parse_characters_file_line(line)
    character_gender_map[character_id] = character_gender
  read_file_lines(path, read_line)

  return character_gender_map


def parse_lines_file_line(line):
  """Parse a line from the movie_lines.txt file

  Example line from the file:
    L1045 +++$+++ u0 +++$+++ m0 +++$+++ BIANCA +++$+++ They do not!

  Returns:
    (tuple of str): The line id (e.g. 'L123'), character id
      (e.g. 'u123') and the actual line text.
  """

  columns = line.split(FILE_COLUMN_SEPARATOR)
  return columns[0], columns[1], columns[4].rstrip()


def parse_lines_file(path):
  """Parse the movie_lines.txt file

  Args:
    path (str): File path for movie_lines.txt.

  Returns:
    (dict of str: (str, str)): Map from line id (e.g. 'L123') to pair
      of character id and utterance text.
  """

  line_map = {}

  def read_line(line):
    line_id, character_id, line_text = parse_lines_file_line(line)
    line_map[line_id] = character_id, line_text
  read_file_lines(path, read_line)

  return line_map


def parse_conversations_file_line(line):
  """Parse a line from the movie_conversations.txt file

  Example line from the file:
    u0 +++$+++ u2 +++$+++ m0 +++$+++ ['L194', 'L195', 'L196', 'L197']

  Returns:
    (list of str): List of line ids in the converation.
  """

  columns = line.split(FILE_COLUMN_SEPARATOR)
  return ast.literal_eval(columns[3])


def parse_conversations_file(path):
  """Parse the movie_conversations.txt file

  Args:
    path (str): File path for movie_conversations.txt.

  Returns:
    (list of list of str): List of conversations, each a list of line ids (e.g. 'L123').
  """

  conversations = []

  def read_line(line):
    line_ids = parse_conversations_file_line(line)
    conversations.append(line_ids)
  read_file_lines(path, read_line)

  return conversations


def parse_command_line_args():
  """Parse command line arguments"""
  parser = argparse.ArgumentParser(description='Reconstruct movie dialogs file.')
  parser.add_argument(
    '--characters',
    default='movie_characters_metadata.txt',
    help='path to the movie_characters_metadata.txt file'
  )
  parser.add_argument(
    '--lines',
    default='movie_lines.txt',
    help='path to movie_lines.txt file'
  )
  parser.add_argument(
    '--conversations',
    default='movie_conversations.txt',
    help='path to movie_conversations.txt file'
  )
  return parser.parse_args()


def main():
  """Main entry point of the app"""
  args = parse_command_line_args()

  characters = parse_characters_file(args.characters)
  lines = parse_lines_file(args.lines)
  conversations = parse_conversations_file(args.conversations)

  for line_ids in conversations:
    for line_id in line_ids:
      character_id, line_text = lines[line_id]
      gender = characters[character_id]
      print('{}: {}'.format(gender, line_text))
    print()


if __name__ == "__main__":
  """This is executed when run from the command line"""
  main()

#!/usr/bin/env python3
"""
Groups phrases from the reconstructed movie dialog corpus conversations

This script reads text in the format output by
reconstruct_dialogs.py. It attempts to find words and phrases that are
used in the same context consistently throughout a large corpus of
text, which presumably are similar in their usage and part of speech
(nouns/verbs/adjectives), etc.

The hope is that it can be modified/improved over time to accurately
find noun phrases specific to genders that work across languages,
though for now, it is just prelimnary exploratory work.
"""

import argparse
import common
import re
import itertools
import nltk

# Download data required for ntlk tokenizer.
nltk.download('punkt')


def create_context_key(phrase_size, context_size, tokens, index):
  context_list = []
  startIndex = index - context_size
  for i in range(context_size):
    if startIndex + i >= 0:
      context_list.append(tokens[startIndex + i])
    else:
      context_list.append('###')
  context_list.append('___')
  for i in range(context_size):
    suffix_index = index + i + phrase_size
    if suffix_index < len(tokens):
      context_list.append(tokens[suffix_index])
    else:
      context_list.append('###')
  return ' '.join(context_list)


def get_word_contexts(text, phrase_size, context_size):
  tokens = nltk.word_tokenize(text)
  for i in range(len(tokens) - phrase_size + 1):
    context_key = create_context_key(phrase_size, context_size, tokens, i)
    yield ' '.join(tokens[i:i + phrase_size]), context_key


class PhraseGrouper:
  def __init__(self, phrase_size, context_size):
    self.contexts = {}
    self.phrase_size = phrase_size
    self.context_size = context_size

  def add(self, text):
    word_contexts = get_word_contexts(text, self.phrase_size, self.context_size)
    for word_context in word_contexts:
      word, context = word_context
      words = context in self.contexts and self.contexts[context] or []
      words.append(word)
      self.contexts[context] = words

  def print_groups(self):
    for context, words in self.contexts.items():
      if len(set(words)) <= 1:
        continue
      group_words = set()
      for word, group in itertools.groupby(words):
        group_words.add(word)
      print('Context: {}'.format(context))
      print('         {}'.format(', '.join(group_words)))


def parse_dialogs_file(path):
  """Parse the reconstructed_dialogs.txt file

  Args:
    path (str): File path for reconstructed_dialogs.txt.

  Returns:
    (list of list of (str, str)): List of dialogs, each of which is a
      list of tuples: first the gender of the speaker and second the
      uttered text.
  """
  dialogs = []
  dialog = []

  def read_line(line):
    if ': ' not in line:
      nonlocal dialog
      dialogs.append(dialog)
      dialog = []
      return
    gender, text = line.split(': ', 1)
    dialog.append((gender, text.rstrip()))
  common.read_file_lines(path, read_line)

  return dialogs


def parse_command_line_args():
  """Parse command line arguments"""
  parser = argparse.ArgumentParser(
    description='Group phrases from econstructed movie dialog corpus conversations.'
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
  return parser.parse_args()


def main():
  """Main entry point of the app"""
  args = parse_command_line_args()

  dialogs = parse_dialogs_file(args.dialogs)
  phrase_grouper = PhraseGrouper(args.phrase_size, args.context_size)
  for dialog in dialogs:
    for line in dialog:
      gender, text = line
      phrase_grouper.add(text)
  phrase_grouper.print_groups()


if __name__ == "__main__":
  """This is executed when run from the command line"""
  main()

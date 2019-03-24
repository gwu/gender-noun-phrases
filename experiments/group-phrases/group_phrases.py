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
import ast
import common
import re
import itertools
import nltk

# Download data required for ntlk tokenizer.
nltk.download('punkt')


def normalize(token, group_index):
  if not token in group_index:
    return token
  return group_index[token]


def create_context_key(phrase_size, context_size, tokens, index, group_index):
  # TODO: Make token normalization work for multiple-word phrases.
  # The problem now is that the group_index contains somem phrases that are
  # multiple words, but when we normalize the contexts, we only look up
  # individual tokens in the group index. Therefore, there may be cases where
  # a multiple-word phrase in the context is not being normalized.
  context_list = []
  startIndex = index - context_size
  for i in range(context_size):
    if startIndex + i >= 0:
      context_list.append(normalize(tokens[startIndex + i], group_index))
    else:
      context_list.append('###')
  context_list.append('___')
  for i in range(context_size):
    suffix_index = index + i + phrase_size
    if suffix_index < len(tokens):
      context_list.append(normalize(tokens[suffix_index], group_index))
    else:
      context_list.append('###')
  return ' '.join(context_list)


def get_word_contexts(text, phrase_size, context_size, group_index):
  tokens = nltk.word_tokenize(text)
  for i in range(len(tokens) - phrase_size + 1):
    context_key = create_context_key(phrase_size, context_size, tokens, i, group_index)
    yield ' '.join(tokens[i:i + phrase_size]), context_key


def create_group_index(groups):
  """Create an index from word to group name"""
  index = {}
  for group in groups:
    for phrase in group:
      index[phrase] = '|'.join(group)
  return index


class PhraseGrouper:
  def __init__(self, phrase_size, context_size, groups):
    self.contexts = {}
    self.phrase_frequencies = {}
    self.phrase_size = phrase_size
    self.context_size = context_size
    self.groups = create_group_index(groups or [])

  def _count_phrase(self, phrase):
    previous_count = phrase in self.phrase_frequencies and self.phrase_frequencies[phrase] or 0
    self.phrase_frequencies[phrase] = previous_count + 1

  def add(self, text):
    for phrase_size in range(1, self.phrase_size + 1):
      word_contexts = get_word_contexts(text, phrase_size, self.context_size, self.groups)
      for word_context in word_contexts:
        word, context = word_context
        self._count_phrase(word)
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
      print('         {}'.format('  '.join(['"{}"'.format(x) for x in group_words])))

  def get_groups(self):
    return self.contexts.values()


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


def parse_groups_file(path):
  """Parse the groups.txt file from a previous iteration

  Args:
    path (str): File path for groups.txt.

  Returns:
    (list of list of str): List of word groups, each of which is a
      list of strings that are assumed to be syntactically interchangeable.
  """
  groups = []

  def read_line(line):
    group, count = line.split(' +++ ', 1)
    parsed_group = list(ast.literal_eval(group))
    groups.append(parsed_group)
  common.read_file_lines(path, read_line)

  return groups


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
  parser.add_argument(
    '--groups',
    help='Output of groups from a previous iteration to use when computing contexts'
  )
  return parser.parse_args()


def main():
  """Main entry point of the app"""
  args = parse_command_line_args()

  dialogs = parse_dialogs_file(args.dialogs)
  groups = args.groups and parse_groups_file(args.groups) or None
  phrase_grouper = PhraseGrouper(args.phrase_size, args.context_size, groups)
  for dialog in dialogs:
    for line in dialog:
      gender, text = line
      phrase_grouper.add(text)
  # phrase_grouper.print_groups()

  phrase_pair_counts = {}
  for group in phrase_grouper.get_groups():
    if len(group) > 10:
      continue
    for pair in itertools.combinations(set(group), 3):
      pair = tuple(sorted(list(pair)))
      previous_count = pair in phrase_pair_counts and phrase_pair_counts[pair] or 0
      phrase_pair_counts[pair] = previous_count + 1

  sorted_pairs = [
    (pair, phrase_pair_counts[pair])
    for pair
    in sorted(phrase_pair_counts, key=phrase_pair_counts.get, reverse=True)
    if phrase_pair_counts[pair] > 1
  ]
  for pair, count in sorted_pairs:
    print('{} +++ {}'.format(pair, count))

if __name__ == "__main__":
  """This is executed when run from the command line"""
  main()

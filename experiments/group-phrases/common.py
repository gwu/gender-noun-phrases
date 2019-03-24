"""
Module of common utilities used

Common utilities used when doing experiments over the cornell movie
dialog corpus conversations.
"""

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

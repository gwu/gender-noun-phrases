group-phrases
-------------

Data files:

  * [cornell-movie-dialogs-corpus](http://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html)

Scripts:

  * `reconstruct_dialogs.py`: Reconstructs the dialogs in
    chronological order from the cornell-movie-dialogs-corpus raw
    files.
  * `group_phrases.py`: Groups words from the dialogs based on the
    common contexts in which they appear. This script uses pipenv to
    manage python package dependencies, to run use something like
    `pipenv run python3 group_phrases.py`.

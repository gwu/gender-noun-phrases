nlp-parse
---------

This directory contains code for experimenting with the Stanford NLP
Parser in attempts to detect the noun phrases in English text (and
hopefully which happen to be used to describe males vs females).

* [Stanford Parser](https://nlp.stanford.edu/software/lex-parser.html)
* [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/index.html)

My idea is to use the parser to identify:

* Noun phrases. All of the things we are considering comparing are
  noun phrases used to describe males vs females. If we can extract
  all noun phrases, we are one step closer to our goal.
* Gender pronouns (he, she, him, her). For gender pronounced use as a
  subject where the verb is "to be" we can assume that the adjective
  or noun phrase in the verb phrase is associated with that gender.
* Noun phrases that end in a gender specific noun (e.g. man, woman,
  girl, boy, male, female). These can be assumed to be gender specific
  as well.

We can probably just print a sample of a bunch of noun phrases to see
if there are any exceptions to the rules laid out above.

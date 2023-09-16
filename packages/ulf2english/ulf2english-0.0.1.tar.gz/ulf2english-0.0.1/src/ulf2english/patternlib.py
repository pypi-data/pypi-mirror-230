from pattern.en import conjugate as pen_conjugate
from pattern.en import pluralize as pen_pluralize
from pattern.en import superlative as pen_superlative
from pattern.en import comparative as pen_comparative

ULF2PEN_TENSE_MAPPINGS = {
  'pres' : 'present',
  'past' : 'past',
  'cf' : 'past'
}

def ulf2pen_tense(tense):
  if tense in ULF2PEN_TENSE_MAPPINGS:
    return ULF2PEN_TENSE_MAPPINGS[tense]
  else:
    raise Exception(f'{tense} is not a valid ULF tense.')
  

def try_twice(func, *args, **kwargs):
  """Attempts to call a function twice in the case of exception.
  
  This is necessary due to an unresolved bug with generators in pattern for Python >3.6.
  """
  try:
    ret = func(*args, **kwargs)
  except:
    ret = func(*args, **kwargs)
  return ret


CONJUGATE_PARAMS = {
  'tense' : ['infinitive', 'present', 'past', 'future'],
  'person' : [1, 2, 3, None],
  'number' : ['sg', 'pl'],
  'mood' : ['indicative', 'imperative', 'conditional', 'subjunctive'],
  'aspect' : ['imperfective', 'perfective', 'progressive'],
  'negated' : [True, False],
  'parse' : [True, False]
}

def conjugate(verb,
              tense='present',
              person=3,
              number='sg',
              mood='indicative',
              aspect='imperfective',
              negated=False,
              parse=True):
  """Take an input verb string and conjugation parameters and return a conjugated verb string."""
  for kwarg, kwval in zip(['tense', 'person', 'number', 'mood', 'aspect', 'negated', 'parse'],
                          [tense, person, number, mood, aspect, negated, parse]):
    if not kwval in CONJUGATE_PARAMS[kwarg]:
      raise Exception(f'Invalid value {kwval} for argument {kwarg}')
    return try_twice(pen_conjugate, verb,
                     tense=tense,
                     person=person,
                     number=number,
                     mood=mood,
                     aspect=aspect,
                     negated=negated,
                     parse=parse)


def pluralize(noun):
  """Take an input noun string and pluralize it.
  
  Notes
  -----
  The pattern.en function has some additional parameters, but they don't seem
  useful for the ULF project so they're not supported currently.
  """
  return pen_pluralize(noun)


def superlative(adj):
  """Take an adjective string and convert it to superlative form."""
  return pen_superlative(adj)


def comparative(adj):
  """Take an input adjective string and convert it to comparative form."""
  return pen_comparative(adj)
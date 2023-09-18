"""Functions for generating English strings from ULF expressions."""

import re
from ulflib import ulflib
from transduction import tt
from memoization import cached

from ulf2english.util import atom, listp, cons, subst, replaceall, flatten
import ulf2english.file as file
import ulf2english.sexpr as sexpr
import ulf2english.patternlib as patternlib

# ``````````````````````````````````````
# Supporting TT predicates
# ``````````````````````````````````````



def unrel_noun(ulf):
  """Take a relational noun in ULF and transform it into a bare noun form."""
  word, suffix = ulflib.split_by_suffix(ulf)
  return word[:-3] + '.' + suffix


def prog2be(proginst):
  return subst('be.v', 'prog', proginst)


def perf2have(perfinst):
  return subst('have.v', 'perf', perfinst)


def infinitive_p(verb):
  return verb == conjugate_infinitive(verb)


def verb_to_participle(verb, part_type='present', force=False):
  """Convert the given verb symbol to the participle form of the given type.
  
  E.g., if `part_type` is 'present', then run.v -> running.v, be.v -> being.v, etc.
  If `part_type` is 'past', then run.v -> ran.v, confuse.v -> confused.v, etc.

  The parameter `force` forces the participle generation even if this word is
  not in infinitive form.
  """
  if part_type not in ['present', 'past']:
    part_type = 'present'

  if atom(verb) and ulflib.verb_p(verb) and (force or infinitive_p(verb)):
    word, suffix = ulflib.split_by_suffix(verb)
    # Some ad hoc corrections
    if word == 'forsee' and part_type == 'past':
      word1 = 'forseen'
    elif word == 'leave' and part_type == 'past':
      word1 = 'left'
    else:
      word1 = patternlib.conjugate(word, tense=part_type, aspect='progressive')
    return ulflib.add_suffix(word1, suffix)
  else:
    return verb
  

def verb_to_past_participle(verb):
  return verb_to_participle(verb, part_type='past')
  

def verb_to_present_participle(verb):
  return verb_to_participle(verb, part_type='present')


def vp_to_participle(vp, part_type=None):
  """Convert a VP so that the main verb is in participle form.
  
  If `part_type` is not given, it is assumed that it's a present participle
  except in the presence of a 'pasv' operator.
  """
  if part_type not in ['present', 'past', None]:
    part_type = None

  if ulflib.verb_p(vp):
    head_verb = ulflib.find_vp_head(vp)
    if part_type == 'present':
      participle = verb_to_present_participle(head_verb)
    elif part_type == 'past' and atom(head_verb):
      participle = verb_to_past_participle(head_verb)
    elif part_type == 'past' and ulflib.pasv_lex_verb_p(head_verb):
      participle = verb_to_past_participle(head_verb[1])
    elif part_type == 'past':
      raise Exception(f'Verb {head_verb} is not a form that can become a past participle')
    elif atom(head_verb):
      participle = verb_to_present_participle(head_verb)
    elif ulflib.pasv_lex_verb_p(head_verb):
      participle = verb_to_past_participle(head_verb[1])
    else:
      raise Exception(f'Verb {head_verb} is not a form that can become a past participle')
    
    return ulflib.replace_vp_head(vp, participle)
  
  # If not a verb phrase, just return
  else:
    return vp


def vp_to_past_participle(vp):
  return vp_to_participle(vp, part_type='past')


def vp_to_present_participle(vp):
  return vp_to_participle(vp, part_type='present')


def adverbialize_adj_head(ap):
  """Adverbializes the head adjective of an adjective phrase."""
  ha = ulflib.find_ap_head(ap)
  word, suffix = ulflib.split_by_suffix(ha)
  wordstr = word.replace('_', ' ')
  advdstr = adj2adv(wordstr).replace(' ', '_')
  advd = ulflib.add_suffix(advdstr, suffix)
  return ulflib.replace_ap_head(ap, advd)


def pasv2surface(ulf):
  """Convert the given ULF to the pasv form if the input is of form (pasv ulf).
  
  E.g.,
  
    - (pasv hit.v) -> (be.v hit.v)
    - (pasv confuse.v) -> (be.v confused.v)
    - (pres (pasv confuse.v)) -> ((pres be.v) confused.v)
  """
  if not listp(ulf) or not len(ulf) == 2:
    return ulf
  elif ulf[0] == 'pasv' and ulflib.verb_p(ulf[1]):
    return ['be.v', verb_to_past_participle(ulf[1])]
  elif ulflib.lex_tense_p(ulf[0]):
    tenseless = pasv2surface(ulf[1])
    return [[ulf[0], tenseless[0]], tenseless[1]]
  else:
    return ulf
  

PERSON1PRONS = ['i.pro', 'me.pro', 'we.pro', 'us.pro']
PERSON2PRONS = ['you.pro', 'ye.pro']

def subj2person(subj):
  if atom(subj):
    subj1 = ulflib.make_explicit(subj)
    # ULF doesn't actually care about the i/me distinction in its symbols,
    # so we allow both and determine if subject based on position in the ULF.
    if subj1 in PERSON1PRONS:
      return 1
    elif subj1 in PERSON2PRONS:
      return 2
    else:
      return 3
  else:
    return 3
  

def conjugate_vp_head(vp, subj):
  """Conjugate the head of `vp` according to the tense attached to it and the number of `subj`.
  
  Assumes there's no passive operator on the verb, since this should be applied after
  (tense (pasv <verb>)) is expanded to ((tense be.v) (<past part verb> ...))
  """
  # Recurse if a conjoined verb phrase
  if listp(vp) and any([ulflib.lex_coord_p(v) for v in vp]):
    return [v if ulflib.lex_coord_p(v) else conjugate_vp_head(v, subj) for v in vp]
  
  num = 'pl' if ulflib.plur_term_p(subj) else 'sg'
  pers = subj2person(subj)
  hv = ulflib.find_vp_head(vp)
  tense = hv[0] if (ulflib.tensed_verb_p(hv) or ulflib.tensed_aux_p(hv)) else None
  lex_verb = hv[1] if tense else hv
  conjugated = ''

  if lex_verb:
    word, suffix = ulflib.split_by_suffix(lex_verb)

    conjugated = conjugate_verb_special(word, tense, suffix, lex_verb)

    if not conjugated:
      if tense:
        conjugated = patternlib.conjugate(word, tense=patternlib.ulf2pen_tense(tense), number=num, person=pers)
      else:
        conjugated = patternlib.conjugate(word, number=num, person=pers)

    # Special suffix so we don't recurse
    conjugated = ulflib.add_suffix(conjugated, 'vp-head')

  return ulflib.replace_vp_head(vp, conjugated)


TERM_TO_SUBJ = {
  'me.pro' : 'i.pro',
  'us.pro' : 'we.pro',
  'her.pro' : 'she.pro',
  'him.pro' : 'he.pro',
  'them.pro' : 'they.pro',
  'whom.pro' : 'who.pro'
}

TERM_TO_OBJ = {v:k for k,v in TERM_TO_SUBJ.items()}


def term_to_subj(term):
  if atom(term) and term in TERM_TO_SUBJ:
    return TERM_TO_SUBJ[term]
  else:
    return term


def term_to_obj(term):
  if atom(term) and term in TERM_TO_OBJ:
    return TERM_TO_OBJ[term]
  else:
    return term
  

def add_tense(ulf):
  """Convert the given ULF to the tensed form if input is of the form (tense ulf).
  
  E.g.,

    - (past run.v) -> ran.vp-head
    - (pres sleep.v) -> sleep.vp-head
  """
  # Simple case when there's tense and a simple verb
  if (listp(ulf) and len(ulf) == 2 and ulflib.lex_tense_p(ulf[0]) and
      (ulflib.verb_p(ulf[1]) or ulflib.aux_p(ulf[1]))):
    tense = ulf[0]
    verb = ulf[1]
    word, suffix = ulflib.split_by_suffix(verb)

    conjugated = conjugate_verb_special(word, tense, suffix, verb)

    if not conjugated:
      conjugated = patternlib.conjugate(word, tense=patternlib.ulf2pen_tense(tense))

    conjugated = ulflib.add_suffix(conjugated, 'vp-head' if suffix == 'v' else suffix)
    return conjugated
  
  # Ignore all other cases for now
  else:
    return ulf
  

def pluralize(ulf):
  """Convert the given ULF noun phrase to the plural version of the surface form.
  
  For complex noun phrases, this amounts to pluralizing the head of the noun phrase.
  """
  if not ulf:
    return []
  elif atom(ulf) and ulflib.lex_elided_p(ulf):
    return ulf
  # Atomic case
  elif atom(ulf):
    word, suffix = ulflib.split_by_suffix(ulf)
    return ulflib.add_suffix(patternlib.pluralize(word), suffix)
  # NP case
  else:
    hn = ulflib.find_np_head(ulf)
    plurhn = pluralize(hn)
    return ulflib.replace_np_head(ulf, plurhn)
  

SUPERLATIVE_SPECIAL_CASES = {
  'left.a' : 'leftmost.a',
  'right.a' : 'rightmost.a',
  'upper.a' : 'uppermost.a',
  'lower.a' : 'lowermost.a'
}

def lex_superlative(ulf):
  """Convert the given adjective to superlative form.
  
  E.g.,

    - bad.a -> worst.a
    - left.a -> leftmost.a
  """
  if atom(ulf) and ulf in SUPERLATIVE_SPECIAL_CASES:
    return SUPERLATIVE_SPECIAL_CASES[ulf]
  elif ulflib.lex_adjective_p(ulf):
    word, suffix = ulflib.split_by_suffix(ulf)
    return ulflib.add_suffix(patternlib.superlative(word), suffix)
  else:
    return ulf


def ap_superlative(apulf):
  """Convert the given adjective phrase to superlative form.
  
  This amounts to finding the head adjective and making it superlative most
  of the time. If the head isn't found, we just wrap 'most' around the whole thing.
  """
  ha, found, _ = ulflib.search_ap_head(apulf)
  if found:
    return ulflib.replace_ap_head(apulf, lex_superlative(ha))
  else:
    return ['most', apulf]
  

def non_comma_list_p(ulf):
  return not atom(ulf) and not ',' in ulf


def comma_needing_large_coord_p(ulf):
  """Check whether this is a coordination that requires the insertion of commas."""
  return listp(ulf) and len(ulf) > 3 and ulflib.lex_coord_p(ulf[-2]) and not ',' in ulf


def comma_needing_small_coord_p(ulf):
  """Check whether this is a coordination with only two elements that needs commas."""
  if not (listp(ulf) and len(ulf) == 3 and ulflib.lex_coord_p(ulf[1]) and not ',' in ulf):
    return False
  un_vp_head = vp_head_to_v(ulf)
  return ulflib.sent_p(un_vp_head[0]) and ulflib.sent_p(un_vp_head[2])


def add_comma_to_coord(ulf):
  def rec(ulf, acc):
    if not ulf:
      return acc[::-1]
    elif ulflib.lex_coord_p(ulf[0]):
      acc = [ulf[1], ulf[0], ','] + acc
      return rec(ulf[2:], acc)
    else:
      acc = [ulf[0], ','] + acc
      return rec(ulf[1:], acc)
  return cons(ulf[0], rec(ulf[1:], []))


def ulf_quote_p(ulf):
  return listp(ulf) and len(ulf) == 3 and ulf[0] == '"' and ulf[2] == '"'


def quote2surface(ulf):
  if ulf_quote_p(ulf):
    return '"'+convert(ulf[1], add_punct=False, capitalize_front=False)+'"'
  else:
    return ulf


def post_poss_p(ulf):
  return listp(ulf) and len(ulf) == 2 and ulf[0] == "'" and ulf[1] == 's'


def post_poss2surface(ulf):
  return "'s"


def ds_p(ulf):
  return listp(ulf) and len(ulf) == 3 and ulf[0] == 'ds'


def ds2surface(ulf):
  if ds_p(ulf):
    return ulf[2][1:-1]
  else:
    return ulf


PREDS = [
  unrel_noun,
  prog2be,
  perf2have,
  infinitive_p,
  verb_to_participle,
  verb_to_past_participle,
  verb_to_present_participle,
  vp_to_participle,
  vp_to_past_participle,
  vp_to_present_participle,
  adverbialize_adj_head,
  pasv2surface,
  subj2person,
  conjugate_vp_head,
  term_to_subj,
  term_to_obj,
  add_tense,
  pluralize,
  lex_superlative,
  ap_superlative,
  non_comma_list_p,
  comma_needing_large_coord_p,
  comma_needing_small_coord_p,
  add_comma_to_coord,
  ulf_quote_p,
  quote2surface,
  post_poss_p,
  post_poss2surface,
  ds_p,
  ds2surface
]

for pred in PREDS:
  tt.register_pred(pred)



# ``````````````````````````````````````
# Supporting functions
# ``````````````````````````````````````



def relational_nouns_to_surface(ulf):
  """Convert relational nouns to versions closer to surface form.
  
  Implicit referents lead to a deletion of the preposition, e.g.,
  (on.p ({the}.d (top-of.n *ref))) => (on.p ({the}.d top.n))
  """
  return tt.apply_rules([(
    ['!lex-rel-noun-p', '!lex-macro-rel-hole-p'],
    ['unrel-noun!', '1'])],
  ulf, max_n=500, rule_order='slow-forward')


def conjugate_infinitive(verb):
  if not atom(verb):
    return verb
  
  word, suffix = ulflib.split_by_suffix(verb)
  return ulflib.add_suffix(patternlib.conjugate(word, tense='infinitive'), suffix)


ADVERBS = file.load_json('resources/wordnet.adv')

@cached
def adj2adv(adj):
  """Take an adjective string and return the corresponding adverb string."""
  # Ends in -ly, no change
  if adj.endswith('ly'):
    guess = adj
  # Ends in -y, replace -y with -ily
  elif adj.endswith('y'):
    guess = adj[:-1] + 'ily'
  # Otherwise, append -ly
  else:
    guess = adj + 'ly'
  
  # Check if modification is in the ADVERBS data; if not, return original string
  return guess if guess in ADVERBS else adj


def conjugate_verb_special(word, tense, suffix, lex_verb):
  """Check for a few special verb conjugation cases, otherwise return None."""
  if word in ['be-to', 'be-destined']:
    return 'be'
  elif word in ['were', 'would', 'could', 'should']:
    return word
  elif word == 'will' and tense in ['past', 'cf'] and suffix in ['aux', 'aux-s', 'aux-v']:
    return 'would'
  elif word == 'forsee' and tense == 'past':
    return 'forsaw'
  elif word == 'leave' and tense == 'past':
    return 'left'
  elif not ulflib.surface_token_p(lex_verb): # {be}.v -> {be}.v
    return word
  else:
    return None
  

def vp_head_to_v(ulf):
  """Return ULF with all vp-head converted to .v"""
  def rec(ulf):
    if atom(ulf):
      word, suffix = ulflib.split_by_suffix(ulf)
      return ulflib.add_suffix(word, 'v') if suffix == 'vp-head' else ulf
    else:
      return [rec(x) for x in ulf]
  return rec(ulf)



# ``````````````````````````````````````
# Supporting rules
# ``````````````````````````````````````



PROG2SURFACE = (
  ['!prog-marker-p', '*phrasal-sent-op-p', '!verb-p', '*expr'],
  [['prog2be!', '1'], '2', ['vp-to-present-participle!', '3'], '4']
)

INV_PROG2SURFACE = (
  ['!prog-marker-p', '*phrasal-sent-op-p', '!term-p', '*phrasal-sent-op-p', '!verb-p', '*expr'],
  [['prog2be!', '1'], '2', '3', '4', ['vp-to-present-participle!', '5'], '6']
)

PERF2SURFACE = (
  ['!perf-marker-p', '*phrasal-sent-op-p', '!verb-p', '*expr'],
  [['perf2have!', '1'], '2', ['vp-to-past-participle!', '3'], '4']
)
  
INV_PERF2SURFACE = (
  ['!perf-marker-p', '*phrasal-sent-op-p', '!term-p', '*phrasal-sent-op-p', '!verb-p', '*expr'],
  [['perf2have!', '1'], '2', '3', '4', ['vp-to-past-participle!', '5'], '6']
)

PARTICIPLE_FOR_POST_MODIFYING_VERBS = (
  ['!lex-noun-or-np-postmod-macro-p', '!expr', '*expr', '!verb-or-tensed-verb-p', '*expr'],
  ['1', '2', '3', ['vp-to-participle!', '4'], '5']
)

PARTICIPLE_FOR_ADV_A = (
  ['adv-a', '!verb-p'],
  ['adv-a', ['vp-to-participle!', '2']]
)
  
PARTICIPLE_FOR_MOD_X = (
  ['!lex-mod-p', '!verb-p'],
  ['1', ['vp-to-participle!', '2']]
)
  
PARTICIPLE_FOR_IMPLICIT_MOD_X = (
  ['+not-aux-or-head-verb-p', ['!verb-p', '!noun-or-adj-p'], '*expr'],
  ['1', [['vp-to-participle!', '2.1'], '2.2'], '3']
)

PRES_PART_FOR_KA = (
  ['ka', '!verb-p'],
  ['ka', ['vp-to-present-participle!', '2']]
)  

ADJ2ADV = (
  ['!advformer-p', '!adj-p'],
  ['1', ['adverbialize-adj-head!', '2']]
)
  
TENSED_PASV2SURFACE = (
  ['!lex-tense-p', ['pasv', '!expr']],
  ['pasv2surface!', ['1', '2']]
)
  
PASV2SURFACE = (
  ['pasv', '!expr'],
  ['pasv2surface!', ['1', '2']]
)

SIMPLE_WHAT_IS_TENSE_N_NUMBER2SURFACE = (
  ['what.pro', '*phrasal-sent-op-p', [['!lex-tense-p', 'be.v'], '*phrasal-sent-op-p', ['=', '!term-p']]],
  ['what.pro', '2', [['conjugate-vp-head!', '3.1', '3.3.2'], '3.2', ['=', '3.3.2']]]
)
"""This is dealing with the oversimplification of "what is/are" questions, which we allow to be uninverted."""

TENSE_N_NUMBER2SURFACE = (
  ['!term-p', '*phrasal-sent-op-p', '!pred-p', '*phrasal-sent-op-p'],
  [['term-to-subj!', '1'], '2', ['conjugate-vp-head!', '3', '1'], '4']
)

INV_COPULA_TENSE_N_NUMBER2SURFACE = (
  [['!lex-tense-p', 'be.v'], '*phrasal-sent-op-p', '!term-p',
      '*phrasal-sent-op-p', '!pred-p', '*phrasal-sent-op-p'],
  [['conjugate-vp-head!', '1', '3'], '2', ['term-to-subj!', '3'], '4', '5', '6']
)
  
INV_AUX_TENSE_N_NUMBER2SURFACE = (
  [['!lex-tense-p', '!invertible-verb-or-aux-p'], '*phrasal-sent-op-p',
      '!term-p', '*phrasal-sent-op-p', '!verb-p', '*phrasal-sent-op-p'],
  [['conjugate-vp-head!', '1', '3'], '2', ['term-to-subj!', '3'], '4', '5', '6']
)
  
EXIST_THERE_TENSE_N_NUMBER2SURFACE = (
  ['there.pro', [['!lex-tense-p', '!lex-verb-p'], '*phrasal-sent-op-p', '!term-p', '*phrasal-sent-op-p']],
  ['there.pro', [['conjugate-vp-head!', '2.1', '2.3'], '2.2', '2.3', '2.4']]
)
  
INV_EXIST_THERE_TENSE_N_NUMBER2SURFACE = (
  [['!lex-tense-p', '!lex-verb-p'], 'there.pro', '*phrasal-sent-op-p', '!term-p', '*phrasal-sent-op-p'],
  [['conjugate-vp-head!', '1', '4'], 'there.pro', '3', '4', '5']
)
  
TENSE2SURFACE = (
  ['!lex-tense-p', '!expr'],
  ['add-tense!', ['1', '2']]
)
  
PLUR2SURFACE = (
  ['plur', '!expr'],
  ['pluralize!', '2']
)
  
MOST_N_MORPH = (
  ['most-n', '!lex-adjective-p', '!noun-p'],
  [['lex-superlative!', '2'], '3']
)
  
MOST_MORPH = (
  ['most', '!adj-p', '*phrasal-sent-op-p'],
  [['ap-superlative!', '2'], '3']
)

MORPHOLOGY_RULES = [
  # Initial interactive changes
  PROG2SURFACE,
  INV_PROG2SURFACE,
  PERF2SURFACE,
  INV_PERF2SURFACE,
  # Various participles
  PARTICIPLE_FOR_POST_MODIFYING_VERBS,
  PARTICIPLE_FOR_ADV_A,
  PARTICIPLE_FOR_MOD_X,
  PARTICIPLE_FOR_IMPLICIT_MOD_X,
  PRES_PART_FOR_KA,
  # Core non_interactive pieces.
  ADJ2ADV,
  TENSED_PASV2SURFACE,
  PASV2SURFACE,
  SIMPLE_WHAT_IS_TENSE_N_NUMBER2SURFACE,
  TENSE_N_NUMBER2SURFACE,
  INV_COPULA_TENSE_N_NUMBER2SURFACE,
  INV_AUX_TENSE_N_NUMBER2SURFACE,
  EXIST_THERE_TENSE_N_NUMBER2SURFACE,
  INV_EXIST_THERE_TENSE_N_NUMBER2SURFACE,
  TENSE2SURFACE, # default tense if above didn't work.
  PLUR2SURFACE,
  MOST_N_MORPH,
  MOST_MORPH,
]


INSERT_COMMA_RULES = [
  # flat ps
  (['!lex-ps-p', '!non-comma-list-p', '!non-comma-list-p'],
   ['1', '2', ',', '3']),
  # ps first
  ([['!lex-ps-p', '!expr'], '!expr'],
   [['1.1', '1.2'], ',', '2']),
  # ps second
  (['!expr', '*not-lex-comma-p', ['!lex-ps-p', '!expr']],
   ['1', '2', ',', ['3.1', '3.2']]),
  # interleaved ps
  (['!expr', '*not-lex-comma-p', ['!lex-ps-p', '!expr'], '+expr'],
   ['1', '2', ',', ['3.1', '3.2'], ',', '4']),
  # coordination
  ('!comma-needing-large-coord-p',
   ['add-comma-to-coord!', '0']),
  ('!comma-needing-small-coord-p',
   ['add-comma-to-coord!', '0'])
]


QUOTES2SURFACE_RULE = (
  '!ulf-quote-p',
  ['quote2surface!', '0']
)


POST_POSS2SURFACE_RULE = (
  '!post-poss-p',
  ['post-poss2surface!', '0']
)


DS2SURFACE_RULE = (
  '!ds-p',
  ['ds2surface!', '0']
)



# ``````````````````````````````````````
# Pipeline functions
# ``````````````````````````````````````



def extract_punctuation(ulf):
  """Extract the terminating punctuation from a given ULF."""
  if listp(ulf):
    if len(ulf) > 1 and ulf[0] == 'sub':
      return extract_punctuation(ulf[2])
    elif len(ulf) > 1 and ulf[0] == 'rep':
      return extract_punctuation(ulf[1])
    elif len(ulf) == 2 and ulf[1] in ['?', '!']:
      return ulf[1]
    elif len(ulf) == 2 and ulf[1] == '.?':
      return '?'
  return '.'


def set_of_to_and(ulf):
  return tt.apply_rule(
    (['set-of', '+expr', '!expr'],
     ['2', 'and.cc', '3']),
    ulf)


def add_info_to_sub_vars(ulf):
  return ulflib.add_info_to_sub_vars(ulf)


def add_info_to_relativizers(ulf):
  return ulflib.add_info_to_relativizers(ulf)


CONTEXTUAL_PREPROCESS_FNS = [
  relational_nouns_to_surface
]

def contextual_preprocess(ulf):
  """Preprocess the ULF according to contextual cues, which are separate from morphological modifications."""
  for fn in CONTEXTUAL_PREPROCESS_FNS:
    ulf = fn(ulf)
  return ulf


def add_morphology(ulf):
  """Make transformations to ULF to add morphology.
  
  Notes
  -----
  The order here matters: many stages rely on perf and prog having already
  been processed. Some rules apply to the same things, but the more specific
  ones are done first.
  """
  return tt.apply_rules(MORPHOLOGY_RULES, ulf, rule_order='slow-forward')


def add_commas(ulf):
  return tt.apply_rules(INSERT_COMMA_RULES, ulf, rule_order='slow-forward')


def quotes2surface(ulf):
  return tt.apply_rule(QUOTES2SURFACE_RULE, ulf)


def post_possess2surface(ulf):
  return tt.apply_rule(POST_POSS2SURFACE_RULE, ulf)


def ds2surface(ulf):
  return tt.apply_rule(DS2SURFACE_RULE, ulf)


def flatten_ulf(ulf):
  return flatten(ulf)


def remove_non_surface_tokens(lst):
  return [x for x in lst if ulflib.surface_token_p(x)]


def process_voc_o(lst):
  return ['O' if x=='voc-o' else x for x in lst]


def join_post_possess(lst):
  if not lst:
    return []
  else:
    rec = join_post_possess(lst[1:])
    cur = lst[0]
    toprec = rec[0] if rec else []
    if toprec == "'s":
      return cons(cur+toprec, rec[1:])
    else:
      return cons(cur, rec)


def strip_suffixes(lst):
  return [ulflib.strip_suffix(x) for x in lst]


def post_format_ulf_string(lst):
  """Post-format a ULF-to-string mapping by replacing dashes and underscores with spaces."""
  return [x.replace('-', ' ').replace('_', ' ') for x in lst]


def merge_det_thing_combos(lst):
  """Merge certain determiner-"thing"/"one" combinations.
  
  E.g.,

    - "any" "one" -> "anyone"
    - "every" "thing" -> "everything"
  """
  if not lst:
    return []
  else:
    rec = merge_det_thing_combos(lst[1:])
    cur = lst[0]
    toprec = rec[0] if rec else []
    if cur in ['any', 'no', 'every'] and toprec in ['one', 'thing']:
      return cons(cur+toprec, rec[1:])
    else:
      return cons(cur, rec)


def remove_precomma_spaces(lst):
  """Merge commas with prior words."""
  if not lst:
    return []
  else:
    rec = remove_precomma_spaces(lst[1:])
    cur = lst[0]
    toprec = rec[0] if rec else []
    if toprec == ',':
      return cons(cur+toprec, rec[1:])
    else:
      return cons(cur, rec)


def glue(lst):
  return ' '.join(lst)


def add_punct(str, punct):
  return str + punct


def capitalize_front(str):
  return str[0].upper() + str[1:]


def capitalize_i(str):
  return re.sub(r'\bi\b', 'I', str)


POST_PROCESSED_EQUIVALENCIES = [
  # Prepositional wh-relative clauses
  (r'(?i)at which', 'when', True),
  (r'(?i)at time which', 'when', True),
  (r'(?i)on which', 'where', True),
  (r'(?i)at what place', 'where', True),
  (r'(?i)at which place', 'where', True),
  (r'(?i)at loc which', 'where', True),
  (r'(?i)at what time', 'when', True),
  (r'(?i)at which time', 'when', True),
  (r'(?i)in what way', 'how', True),
  (r'(?i)in which way', 'how', True),
  (r'(?i)on what place', 'whereon', True),
  (r'(?i)on which place', 'whereon', True),
  (r'(?i)on loc which', 'whereon', True),
  # Emphatic wh-words
  (r'(?i)what em', 'what', True),
  (r'(?i)how em', 'how', True),
  # whoever, whatever, wherever
  ('any person', 'whoever', False),
  ('any one', 'whoever', False),
  ('any thing', 'whatever', False),
  ('any place', 'wherever', False)
]

def apply_post_processed_equivalencies(str):
  return replaceall(str, POST_PROCESSED_EQUIVALENCIES)


def standardize(str):
	"""Standardize a string by applying a series of transformations.
	
	Specifically:
		1. Replace -- with -, and _ with whitespace.
		2. Remove parenthetical content (i.e., [...] or *...*).
		3. Add whitespace around all punctuation.
		4. Collapse all whitespace to a single space.
		5. Convert to lowercase.
	"""
	str = str.replace('--', '-').replace('_', ' ')
	str = re.sub(r'\[[a-zA-Z0-9\s]*\]', '', str)
	str = re.sub(r'\*[a-zA-Z0-9\s]*\*', '', str)
	str = re.sub(r'([.|,|!|?|:|;|-])', r' \1 ', str)
	str = re.sub(r'[\s]+', ' ', str)
	return str.lower().strip()


ULF2ENGLISH_STAGES = [
  (set_of_to_and, "'set-of' to 'and.cc'"),
  (add_info_to_sub_vars, "Add type/plurality info to 'sub' variables"),
  (add_info_to_relativizers, "Add info to relativizers"),
  (contextual_preprocess, "Contextual preprocess"),
  (add_morphology, "Adding morphology"),
  (add_commas, "Insert commas"),
  (quotes2surface, "Handle quotes"),
  (post_possess2surface, "Handle post-nominal possessive (i.e. 's)"),
  (ds2surface, "Handle domain-specific ULFs"),
  (flatten_ulf, "Flatten ULF into list"),
  (process_voc_o, "Process voc-o"),
  (join_post_possess, "Join post-posessive (i.e. 's) with previous word"),
  (remove_non_surface_tokens, "Only retaining surface symbols"),
  # (stringify_symbols, "Stringify symbols"),
  (strip_suffixes, 'Strip suffixes'),
  (post_format_ulf_string, "Post-format strings"),
  (merge_det_thing_combos, "Merge special determiner-noun combinations"),
  (remove_precomma_spaces, "Merge commas with previous word"),
  (glue, "Glue together"),
  (add_punct, "Add ending punctuation"),
  (apply_post_processed_equivalencies, "Substitute some equivalent expressions"),
  (capitalize_front, "Capitalize the first word"),
  (capitalize_i, "Capitalize 'i'"),
  (standardize, "Standardize the final string")
]


def convert(ulf,
            add_punct=True,
            capitalize_front=True,
            add_commas=False,
            standardize=False,
            verbose=False):
  """Convert the given ULF to an English string.
  
  Parameters
  ----------
  ulf : str or s-expr
    The ULF formula (or a LISP-formatted string thereof) to convert.
  add_punct : bool, default=True
    Whether to add punctuation to the generated string.
  capitalize_front : bool, default=True
    Whether to capitalize the first word in the generated string.
  add_commas : bool, default=False
    Whether to add commas to the generated string.
  standardize : bool, default=False
    Whether to standardize the generated string, i.e., ensuring that
    it is fully lowercase and that punctuation is split off from words.
  verbose : bool, default=False
    Whether to print information on each stage.

  Returns
  -------
  str
  """
  if isinstance(ulf, str):
    ulf = sexpr.parse_s_expr(ulf)

  punct = extract_punctuation(ulf)

  staged = ulf
  for fn, desc in ULF2ENGLISH_STAGES:
    if ((fn.__name__ == 'add_commas' and not add_commas) or
        (fn.__name__ == 'add_punct' and not add_punct) or
        (fn.__name__ == 'capitalize_front' and not capitalize_front) or
        (fn.__name__ == 'standardize' and not standardize)):
      continue
    if fn.__name__ == 'add_punct':
      staged = fn(staged, punct)
    else:
      staged = fn(staged)
    if verbose:
      print(f'{desc}: {staged}')
  
  return staged if isinstance(staged, str) else ''
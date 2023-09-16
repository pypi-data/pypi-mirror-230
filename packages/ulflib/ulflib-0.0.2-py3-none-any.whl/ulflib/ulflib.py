"""ULF library functions."""

from transduction import tt

from ulflib.util import atom, listp, cons, subst, rec_find_if

# ``````````````````````````````````````
# TT Lexical Patterns
# ``````````````````````````````````````



TENSE = ['past', 'pres', 'cf']
ASPECT = ['perf', 'prog']
PASSIVIZER = ['pasv']
PLURALIZER = ['plur']
NEGATION = ['not']
COORDINATOR = ['and', 'or', 'but', 'because']
ADVFORMER = ['adv-a', 'adv-e', 'adv-s', 'adv-f']
DETFORMER = ['nquan', 'fquan']
MODFORMER = ['mod-a', 'mod-n']
NOUN_REIFIER = ['k']
VERB_REIFIER = ['ka', 'to', 'gd']
SENT_REIFIER = ['ke']
TENSED_SENT_REIFIER = ['that', 'tht', 'whether', 'ans-to']
REIFIER = NOUN_REIFIER + VERB_REIFIER + SENT_REIFIER + TENSED_SENT_REIFIER
PUNCT = ['!', '?', '.?']
OPERATORS = (TENSE
             + ASPECT
             + PLURALIZER
             + COORDINATOR
             + ADVFORMER
             + DETFORMER
             + MODFORMER
             + NEGATION
             + PASSIVIZER
             + REIFIER
             + PUNCT
             + ['nmod', 'amod', 'set-of', "'s", 'poss-by', '=', 'ds', 'pu', 'most-n', 'poss-ques', 'poss-ans'])

NOUN_POSTMOD_MACRO = ['n+preds', 'n+post']
NP_POSTMOD_MACRO = ['np+preds']
VOC_MACRO = ['voc', 'voc-O']
SUB_MACRO = ['sub', 'rep', 'qt-attr']
MACROS = (NOUN_POSTMOD_MACRO
          + NP_POSTMOD_MACRO
          + VOC_MACRO
          + SUB_MACRO)
          
REL_VAR = ['*s', '*ref']
SUB_VAR = ['*h', '*p', '*qt']
HOLE_VARS = REL_VAR + SUB_VAR

KEYWORDS = OPERATORS + MACROS + HOLE_VARS
SURFACE_KEYWORDS = ['that', 'not', 'and', 'or', 'to', 'most', 'some', 'all', 'every', 'whether', 'if']


def lex_noun_p(x):
  return suffix_check(x, 'N')

def lex_rel_noun_p(x):
  if not atom(x):
    return False
  word, suffix = split_by_suffix(x)
  return lex_noun_p(x) and len(word) > 3 and word[-3:] == '-of'

def lex_function_p(x):
  return suffix_check(x, 'F')

def lex_pronoun_p(x):
  return suffix_check(x, 'PRO')

def lex_verb_p(x):
  return suffix_check(x, 'V')

def lex_adjective_p(x):
  return suffix_check(x, 'A')

def lex_p_p(x):
  return suffix_check(x, 'P')

def lex_p_arg_p(x):
  return suffix_check(x, 'P-ARG')

def lex_ps_p(x):
  return suffix_check(x, 'PS')

def lex_pq_p(x):
  return suffix_check(x, 'PQ')

def lex_prep_p(x):
  return lex_p_p(x) or lex_ps_p(x) or lex_pq_p(x)

def lex_pp_p(x):
  return suffix_check(x, 'PP')

def lex_mod_a_p(x):
  return suffix_check(x, 'MOD-A')

def lex_mod_n_p(x):
  return suffix_check(x, 'MOD-N') or x in PLURALIZER

def lex_mod_p(x):
  return lex_mod_a_p(x) or lex_mod_n_p(x)

def lex_rel_p(x):
  return suffix_check(x, 'REL')

def lex_det_p(x):
  return suffix_check(x, 'D')

def lex_coord_p(x):
  return suffix_check(x, 'CC') or x in COORDINATOR

def lex_aux_s_p(x):
  return suffix_check(x, 'AUX-S')

def lex_aux_v_p(x):
  return suffix_check(x, 'AUX-V')

def lex_aux_p(x):
  return lex_aux_s_p(x) or lex_aux_v_p(x)

def lex_number_p(x):
  return isinstance(x, int) or (isinstance(x, str) and x.isdigit())

def lex_name_p(x):
  return suffix_check(x, 'NAME') or (not has_suffix(x) and not x in KEYWORDS)

def lex_adv_a_p(x):
  return suffix_check(x, 'ADV-A')

def lex_adv_s_p(x):
  return suffix_check(x, 'ADV-S') or x in NEGATION

def lex_adv_e_p(x):
  return suffix_check(x, 'ADV-E')

def lex_adv_f_p(x):
  return suffix_check(x, 'ADV-F')

def lex_adv_formula_p(x):
  return lex_adv_s_p(x) or lex_adv_e_p(x) or lex_adv_f_p(x)

def lex_adv_p(x):
  return lex_adv_a_p(x) or lex_adv_formula_p(x)

def lex_x_p(x):
  return suffix_check(x, 'X')

def lex_yn_p(x):
  return suffix_check(x, 'YN')

def lex_gr_p(x):
  return suffix_check(x, 'GR')

def lex_sent_p(x):
  return suffix_check(x, 'SENT')

def lex_tense_p(x):
  return x in TENSE

def lex_aspect_p(x):
  return x in ASPECT

def lex_detformer_p(x):
  return x in DETFORMER

def litstring_p(x):
  return isinstance(x, str) and len(x) >= 3 and x[0] == '"' and x[-1] == '"'

def lex_equal_p(x):
  return x == '='

def lex_set_of_p(x):
  return x == 'set-of'

def lex_noun_postmod_macro_p(x):
  return x in NOUN_POSTMOD_MACRO

def lex_np_postmod_macro_p(x):
  return x in NP_POSTMOD_MACRO

def lex_noun_or_np_postmod_macro_p(x):
  return x in (NOUN_POSTMOD_MACRO + NP_POSTMOD_MACRO)

def lex_macro_p(x):
  return x in MACROS

def lex_macro_rel_hole_p(x):
  return x in REL_VAR

def lex_macro_sub_hole_p(x):
  return x in SUB_VAR

def lex_macro_hole_p(x):
  return x in HOLE_VARS

def lex_hole_variable_p(x):
  return isinstance(x, str) and len(x) > 1 and x[0] == '*'

def lex_verbaux_p(x):
  return lex_verb_p(x) or aux_p(x)

def lex_pasv_p(x):
  return x in PASSIVIZER

def lex_possessive_s_p(x):
  return x == "'s"

def lex_invertible_verb_p(x):
  return x in ['make.v', 'have.v']

def lex_comma_p(x):
  return x == ','

def lex_elided_p(x):
  if not atom(x):
    return False
  word, suffix = split_by_suffix(x)
  return (word[0]=='{' and word[-1]=='}') or (word[0]=='{' and x[-1]=='}')

def surface_token_p(x):
  return (not atom(x)
          or (has_suffix(x) and not lex_elided_p(x) and not lex_hole_variable_p(x))
          or lex_name_p(x)
          or x in SURFACE_KEYWORDS)


LEX_PREDS = [
  lex_noun_p,
  lex_rel_noun_p,
  lex_function_p,
  lex_pronoun_p,
  lex_verb_p,
  lex_adjective_p,
  lex_p_p,
  lex_p_arg_p,
  lex_ps_p,
  lex_pq_p,
  lex_prep_p,
  lex_pp_p,
  lex_mod_a_p,
  lex_mod_n_p,
  lex_mod_p,
  lex_rel_p,
  lex_det_p,
  lex_coord_p,
  lex_aux_s_p,
  lex_aux_v_p,
  lex_aux_p,
  lex_number_p,
  lex_name_p,
  lex_adv_a_p,
  lex_adv_s_p,
  lex_adv_e_p,
  lex_adv_f_p,
  lex_adv_formula_p,
  lex_adv_p,
  lex_x_p,
  lex_yn_p,
  lex_gr_p,
  lex_sent_p,
  lex_tense_p,
  lex_aspect_p,
  lex_detformer_p,
  litstring_p,
  lex_equal_p,
  lex_set_of_p,
  lex_noun_postmod_macro_p,
  lex_np_postmod_macro_p,
  lex_noun_or_np_postmod_macro_p,
  lex_macro_p,
  lex_macro_rel_hole_p,
  lex_macro_sub_hole_p,
  lex_macro_hole_p,
  lex_hole_variable_p,
  lex_verbaux_p,
  lex_pasv_p,
  lex_possessive_s_p,
  lex_invertible_verb_p,
  lex_comma_p,
  lex_elided_p,
  surface_token_p,
]

for pred in LEX_PREDS:
  tt.register_pred(pred, include_neg=True)


# ``````````````````````````````````````
# TT Phrasal Patterns
# ``````````````````````````````````````



TT_NOUN = [
  '!lex-noun-p',
  ['plur', '!noun-p'],
  # Explicit predicate modifiers
  ['!mod-n-p', '!noun-p'],
  ['!noun-p', '!mod-n-p'],
  # Implicit predicate modifiers
  ['!adj-p', '!noun-p'],
  ['!noun-p', '!noun-p'],
  ['!lex-name-p', '!noun-p'],
  ['!term-p', '!noun-p'],
  ['!lex-rel-noun-p', '!term-p'], # (mother-of.n |John|)
  ['!noun-p', '!p-arg-p'],
  ['!lex-function-p', '!term-p'],
  ['n+preds', '!noun-p', '+pred-p'],
  ['+noun-p', '!lex-coord-p', '!noun-p'],
  ['!phrasal-sent-op-p', '!noun-p'],
  ['n+post', '!noun-p', '+postmod-p'],
  ['=', '!term-p'],
  # Fall back if arguments not correctly analyzed
  ['n+preds', '+expr']
]

TT_ADJ = [
  '!lex-adjective-p',
  # Implicit predicate modification
  ['!adj-p', '!adj-p'],
  ['!noun-p', '!adj-p'],
  # Explicit predicate modification
  ['!adv-a-p', '!adj-p'],
  ['!adj-p', '!adv-a-p'],
  ['!mod-a-p', '!adj-p'],
  ['!adj-p', '!mod-a-p'],
  ['poss-by', '!term-p'],
  # Some adjectives take infinitives
  ['!adj-p', ['to', '!verb-p']],
  # Some adjectives take two arguments ("jewelry worth $400")
  ['!lex-adjective-p', '!term-p'],
  # Some adjectives take arguments with prepositions
  ['!adj-p', '!p-arg-p'],
  # A single argument with unlimited additional  modifiers
  ['*mod-a-p', '!adj-p', '*mod-a-p', '!adj-postmod-p', '*mod-a-p'],
  ['*mod-a-p', '!lex-adjective-p', '*mod-a-p', '!term-p', '*mod-a-p'],
  ['*mod-a-p', '!adj-p', '+mod-a-p'],
  ['+mod-a-p', '!adj-p', '*mod-a-p'],
  # Coordination
  ['+adj-p', '!lex-coord-p', '+adj-p'],
  ['!phrasal-sent-op-p', '!adj-p'],
  # Equal sign with term
  ['=', '!term-p']
]

TT_ADJ_PREMOD = [
  '!mod-a-p',
  '!adj-p',
  '!noun-p'
]

TT_ADJ_POSTMOD = [
  '!mod-a-p',
  '!term-p',
  '!p-arg-p',
  '!phrasal-sent-op-p'
]

TT_ADV_A = [
  '!lex-adv-a-p',
  ['adv-a', '!pred-p'],
  # Below is not quite correct since some *.pq map to (adv-e ...), but for the sake
  # of syntax checking it doesn't matter.
  '!lex-pq-p',
  ['+adv-a-p', '!lex-coord-p', '+adv-a-p']
]

TT_ADV_E = [
  '!lex-adv-e-p',
  ['adv-e', '!pred-p'],
  ['+adv-e-p', '!lex-coord-p', '+adv-e-p']
]

TT_ADV_S = [
  '!lex-adv-s-p',
  ['adv-s', '!pred-p'],
  ['+adv-s-p', '!lex-coord-p', '+adv-s-p'],
  ['(', '+expr', ')']
]

TT_ADV_F = [
  '!lex-adv-f-p',
  ['adv-f', '!pred-p'],
  ['+adv-f-p', '!lex-coord-p', '+adv-f-p']
]

TT_MOD_A = [
  '!lex-mod-a-p',
  ['mod-a', '!pred-p']
]

TT_MOD_N = [
  '!lex-mod-n-p',
  ['mod-n', '!pred-p'],
  ['nnp', '!term-p']
]

TT_PP = [
  '!lex-pp-p',
  ['!lex-p-p', '!term-p'],
  ['+pp-p', '!lex-coord-p', '+pp-p'],
  ['!phrasal-sent-op-p', '!pp-p'],
  # "just outside Boston" -- (just.mod-a (outside.p |Boston|))
  ['!mod-a-p', '!pp-p'],
  ['!pp-p', '!mod-a-p'],
  # Fall back, anything starting with *.p
  ['!lex-p-p', '+expr']
]

TT_P_ARG = [
  ['!lex-p-arg-p', '!term-p'],
  ['!lex-p-arg-p', '!pred-p'],
  ['!adv-s-p', '!p-arg-p']
]
  
TT_TERM = [
  '!lex-pronoun-p',
  '!lex-name-p',
  '!lex-number-p',
  '!lex-rel-p',
  ['!det-p', '!noun-p'],
  ['!lex-set-of-p', '+term-p'],
  ['+term-p', '!lex-coord-p', '+term-p'],
  # Reified
  ['!noun-reifier-p', '!noun-p'],
  ['!verb-reifier-p', '!verb-p'],
  ['!sent-reifier-p', '!sent-p'],
  ['!tensed-sent-reifier-p', '!tensed-sent-p'],
  # Domain specific syntax
  ['ds', '!expr', '!litstring-p'],
  # Possessive macro
  ['!preposs-macro-p', '!noun-p'],
  # np+preds
  ['np+preds', '!term-p', '+pred-p'],
  # Object quoted expression
  ['"', '+expr', '"'],
  # Fall back analysis for np+preds
  ['np+preds', '+expr'],
  [['!expr', "'s"], '!expr'],
  # Fall back for reifiers
  ['!noun-reifier-p', '+expr'],
  ['!verb-reifier-p', '+expr'],
  ['!sent-reifier-p', '+expr'],
  ['!tensed-sent-reifier-p', '+expr'],
  # Fall back on determiners and set-of generating terms
  ['!lex-set-of-p', '+expr'],
  ['!det-p', '+expr'],
  # Internal plurality representation
  ['plur-term', '!term-p'],
]

TT_VERB = [
  '!lex-verb-p',
  ['pasv', '!lex-verb-p'],
  ['*adv-a-p', '!verb-p', '+verb-arg-p'],
  ['!adv-a-p', '*phrasal-sent-op-p', '!verb-p'],
  ['!aux-p', '*phrasal-sent-op-p', '!verb-p'],
  ['*verb-p', '!lex-coord-p', '+verb-p'],
  ['!phrasal-sent-op-p', '!verb-p'],
  # Fall back analysis
  ['!verb-p', '!expr']
]

TT_PRED = [
  '!verb-p',
  '!noun-p',
  '!adj-p',
  '!tensed-verb-p',
  '!pp-p',
  ['!lex-rel-p', '!pred-p'],
  '!relativized-sent-p',
  # Fall back analysis
  ['!lex-rel-p', '!expr'],
  ['!phrasal-sent-op-p', '!pred-p']
]

TT_AUX = [
  '!lex-aux-p',
  'perf',
  'prog'
]

TT_TENSED_AUX = [
  ['!lex-tense-p', '!aux-p']
]

TT_TENSED_VERB = [
  ['!lex-tense-p', '!verb-p'],
  ['*adv-a-p', '!tensed-verb-p', '+verb-arg-p'],
  ['!tensed-aux-p', '*phrasal-sent-op-p', '!verb-p'],
  ['!adv-a-p', '*phrasal-sent-op-p', '!tensed-verb-p'],
  ['*tensed-verb-p', '!lex-coord-p', '+tensed-verb-p'],
  ['!phrasal-sent-op-p', '!tensed-verb-p']
]

TT_DET = [
  '!lex-det-p',
  ['!lex-detformer-p', '!adj-p'],
  ['*det-p', '!lex-coord-p', '+det-p']
]

TT_SENT = [
  ['!term-p', '!verb-p'],
  ['+sent-p', '!lex-coord-p', '+sent-p'],
  ['!sent-mod-p', '!sent-p'],
  ['!sent-p', '!sent-mod-p'],
  ['!adv-a-p', '!term-p', '!verb-p'],
  ['!sent-p', '!sent-punct-p'],
  ['!term-p', '=', '!term-p'],
  ['!term-p', '!adj-p'],
  ['!term-p', '!noun-p'],
  '!lex-sent-p',
  ['?sent-mod-p', '!sent-p', '+sent-or-sent-mod-p'],
  ['!sent-mod-p', '!sent-p'],
  '!lex-x-p',
]

TT_TENSED_SENT = [
  # Simple sentence
  ['!term-p', '!tensed-verb-p'],
  # Coordinated sentence
  ['+tensed-sent-p', '!lex-coord-p', '+tensed-sent-p'],
  ['!lex-coord-p', '!tensed-sent-p', '+tensed-sent-p'],
  # Modified sentence (e.g. curried coordination)
  ['!sent-mod-p', '!tensed-sent-p'],
  # Postfixed sentence modification
  ['!tensed-sent-p', '!sent-mod-p'],
  # Backwards sentence
  ['!tensed-verb-p', '!adv-a-p', '!term-p'],
  # Punctuated sentence
  ['!tensed-sent-p', '!sent-punct-p'],
  # Prepositionally coordinated sentences
  ['!ps-p', '!tensed-sent-p'],
  ['!tensed-sent-p', '!ps-p'],
  # Inverted auxiliary sentence
  [['!lex-tense-p', '!aux-p'], '!term-p', '!verb-p'],
  # Inverted verb sentence
  [['!lex-tense-p', '!lex-invertible-verb-p'], '!term-p', '!term-p'],
  [['!lex-tense-p', 'be.v'], '!term-p', '!pred-p'],
  # Phrasal utterances
  ['pu', '!not-sent-or-tensed-sent-p'],
  # Multiple sentences stuck together
  ['!tensed-sent-p', '+tensed-sent-p'],
  # Expletives, yes/no expressions, and greetings
  '!lex-x-p',
  '!lex-yn-p',
  ['gr', '!expr'],
  # Implicit sentence marked by single extension
  '!lex-sent-p'
]
  
TT_SENT_MOD = [
  ['!lex-coord-p', '!sent-or-tensed-sent-p'],
  '!ps-p',
  '!adv-e-p',
  '!adv-s-p',
  '!adv-f-p'
]

TT_PS = [
  ['!lex-ps-p', '!tensed-sent-p'],
  ['!mod-a-p', '!ps-p']
]

TT_PREPOSS_MACRO = [
  ['!term-p', "'s"]
]

TT_VOC = [
  ['voc', '!term-p'],
  ['voc-0', '!term-p'],
  # Fall back
  ['voc', '!expr'],
  ['voc-0', '!expr']
]


def match_any(x, pas, apply_sub=True):
  if apply_sub:
    x = apply_substitution_macros(x)
  for pa in pas:
    if tt.match(pa, x):
      return True
  return False


def contains_relativizer(x):
  def rec(x):
    if lex_rel_p(x):
      return True
    elif atom(x):
      return False
    else:
      return any([rec(y) for y in x])
  return rec(x)


def noun_p(x):
  return match_any(x, TT_NOUN)

def adj_p(x):
  return match_any(x, TT_ADJ)

def adj_premod_p(x):
  return match_any(x, TT_ADJ_PREMOD)

def adj_postmod_p(x):
  return match_any(x, TT_ADJ_POSTMOD)

def adv_a_p(x):
  return match_any(x, TT_ADV_A)

def adv_e_p(x):
  return match_any(x, TT_ADV_E)

def adv_s_p(x):
  return match_any(x, TT_ADV_S)

def adv_f_p(x):
  return match_any(x, TT_ADV_F)

def adv_p(x):
  return adv_a_p(x) or adv_e_p(x) or adv_s_p(x) or adv_f_p(x)

def mod_a_p(x):
  return match_any(x, TT_MOD_A)

def mod_n_p(x):
  return match_any(x, TT_MOD_N)

def mod_a_former_p(x):
  return x in ['mod-a']

def mod_n_former_p(x):
  return x in ['mod-n']

def pp_p(x):
  return match_any(x, TT_PP)

def term_p(x):
  return match_any(x, TT_TERM)

def verb_p(x):
  return match_any(x, TT_VERB)

def pred_p(x):
  return match_any(x, TT_PRED)

def det_p(x):
  return match_any(x, TT_DET)

def aux_p(x):
  return match_any(x, TT_AUX)

def tensed_aux_p(x):
  return match_any(x, TT_TENSED_AUX)

def tensed_verb_p(x):
  return match_any(x, TT_TENSED_VERB)

def sent_p(x):
  return match_any(x, TT_SENT)

def tensed_sent_p(x):
  return match_any(x, TT_TENSED_SENT)

def sent_punct_p(x):
  return x in PUNCT or x in [[p] for p in PUNCT]

def sent_mod_p(x):
  return match_any(x, TT_SENT_MOD)

def ps_p(x):
  return match_any(x, TT_PS)

def noun_reifier_p(x):
  return x in NOUN_REIFIER

def verb_reifier_p(x):
  return x in VERB_REIFIER

def sent_reifier_p(x):
  return x in SENT_REIFIER

def tensed_sent_reifier_p(x):
  return x in TENSED_SENT_REIFIER

def advformer_p(x):
  return x in ADVFORMER

def detformer_p(x):
  return x in DETFORMER

def modformer_p(x):
  return x in MODFORMER

def preposs_macro_p(x):
  return match_any(x, TT_PREPOSS_MACRO)

def relativized_sent_p(x):
  return tensed_sent_p(x) and contains_relativizer(x)

def p_arg_p(x):
  return match_any(x, TT_P_ARG)

def voc_p(x):
  return match_any(x, TT_VOC)


TYPE_ID_FNS = [
  (noun_p, 'noun'),
  (adj_p, 'adj'),
  (adj_premod_p, 'adj-premodifier'),
  (adj_postmod_p, 'adj-postmodifier'),
  (lex_p_p, 'prep'),
  (adv_a_p, 'adv-a'),
  (adv_e_p, 'adv-e'),
  (adv_s_p, 'adv-s'),
  (adv_f_p, 'adv-f'),
  (adv_p, 'adv'),
  (mod_a_p, 'mod-a'),
  (mod_n_p, 'mod-n'),
  (mod_a_former_p, 'mod-a-former'),
  (mod_n_former_p, 'mod-n-former'),
  (pp_p, 'pp'),
  (term_p, 'term'),
  (verb_p, 'verb'),
  (pred_p, 'pred'),
  (det_p, 'det'),
  (aux_p, 'aux'),
  (tensed_aux_p, 'tensed-aux'),
  (tensed_verb_p, 'tensed-verb'),
  (sent_p, 'sent'),
  (tensed_sent_p, 'tensed-sent'),
  (lex_tense_p, 'tense'),
  (sent_punct_p, 'sent-punct'),
  (sent_mod_p, 'sent-mod'),
  (ps_p, 'ps'),
  (noun_reifier_p, 'noun-reifier'),
  (verb_reifier_p, 'verb-reifier'),
  (sent_reifier_p, 'sent-reifier'),
  (tensed_sent_reifier_p, 'tensed-sent-reifier'),
  (advformer_p, 'advformer'),
  (detformer_p, 'detformer'),
  (modformer_p, 'modformer'),
  (preposs_macro_p, 'preposs-macro'),
  (relativized_sent_p, 'rel-sent'),
  (p_arg_p, 'p-arg'),
  (voc_p, 'voc'),
  # Purely lexical types.
  (lex_equal_p, 'equal-sign'),
  (lex_set_of_p, 'set-of-op'),
  (lex_macro_p, 'macro-symbol'),
  (lex_ps_p, 'sent-prep'),
  (lex_coord_p, 'coordinator'),
  (lex_pasv_p, 'pasv'),
  (lex_possessive_s_p, 'possessive-s'),
]


def phrasal_ulf_type(x):
  """Hypothesizes the type of the given ULF formula."""
  matched = [pair[1] for pair in TYPE_ID_FNS if pair[0]([x])]
  return matched if matched else ['unknown']


PHRASE_PREDS = ([x[0] for x in TYPE_ID_FNS if x[0] not in LEX_PREDS])

for pred in PHRASE_PREDS:
  tt.register_pred(pred, include_neg=True)



# ``````````````````````````````````````
# General Phrasal Patterns
# ``````````````````````````````````````



PLUR_PRONOUNS = [
  'they.pro', 'them.pro', 'we.pro', 'us.pro', 'you.pro', 'these.pro', 'those.pro',
  'both.pro', 'few.pro', 'many.pro', 'several.pro', 'all.pro', 'any.pro', 'most.pro',
  'none.pro', 'some.pro', 'ours.pro', 'yours.pro', 'theirs.pro']

PLUR_DETS = ['these.d', 'those.d', 'both.d', 'few.d', 'many.d', 'several.d']


def plur_term_p(x):
  """Return True if the argument is a plural term.

  Examples:
  
    - (the.d (plur *.n))
    - (the.d (.... (plur *.n)))
    - they.pro
    - them.pro
    - we.pro
  """
  # If an atom, just check whether one of selected pronouns
  # TODO: deal with "ours is better"
  if atom(x):
    return x in PLUR_PRONOUNS
  # For terms from nouns, either the quantifier forces a plural reading
  # (e.g., many), or we check the head noun for a plural operator
  # TODO: deal with examples like "all water is wet"
  elif (listp(x) and term_p(x) and len(x) == 2
        and (det_p(x[0]) or noun_reifier_p(x[0]))
        and (noun_p(x[1]) or pp_p(x[1]))):
    return x[0] in PLUR_DETS or plur_noun_p(x[1]) or plur_partitive_p(x[1])
  # Coordinated nouns and sets of terms are plural
  elif listp(x) and term_p(x) and len(x) > 2:
    return lex_set_of_p(x[0]) or lex_coord_p(x[1]) or lex_coord_p(x[-2])
  # Term marked with 'plur-term' (an internal computational marker)
  elif listp(x) and len(x) == 2 and x[0] == 'plur-term' and term_p(x[1]):
    return True
  # Otherwise, singular
  else:
    return False
  

def plur_partitive_p(x):
  return listp(x) and len(x) == 2 and lex_p_p(x[0]) and plur_term_p(x[1])


def plur_noun_p(x):
  """True if `x` is a plural noun phrase, i.e., if the NP head is plural."""
  if listp(x) and len(x) == 2 and x[0] == 'plur' and noun_p(x[1]):
    return True
  else:
    hn = find_np_head(x)
    return plur_lex_noun_p(hn)
  

def plur_lex_noun_p(x):
  """True if `x` is of the form (plur <lexical noun>)."""
  return listp(x) and len(x) == 2 and x[0] == 'plur' and lex_noun_p(x[1])


def pasv_lex_verb_p(x):
  """True if arg is of the form (pasv <lexical verb>); False otherwise."""
  return listp(x) and len(x) == 2 and x[0] in PASSIVIZER and lex_verb_p(x[1])


def unknown_p(x):
  return ['unknown'] == phrasal_ulf_type(x)


def postmod_p(x):
  return pred_p(x) or term_p(x) or adv_p(x) or p_arg_p(x) or unknown_p(x)


def postmod_adj_p(x):
  return p_arg_p(x) or (listp(x) and len(x) == 2 and x[0] == 'to' and verb_p(x[1]))


def verb_arg_p(x):
  return term_p(x) or pred_p(x) or adv_a_p(x) or p_arg_p(x) or phrasal_sent_op_p(x)


def verb_or_tensed_verb_p(x):
  return verb_p(x) or tensed_verb_p(x)


def sent_or_sent_mod_p(x):
  return sent_p(x) or sent_mod_p(x)


def sent_or_tensed_sent_p(x):
  return sent_p(x) or tensed_sent_p(x)


def phrasal_sent_op_p(x):
  """Condition to check if an element is a filtered sentence-level operator.
  
  I.e., basically all sentence-level operators that are written within the phrase in the surface form.
  """
  return (adv_e_p(x) or adv_s_p(x) or adv_f_p(x)
          or x in ['not', 'not.adv-e', 'not.adv-s']
          or ps_p(x)
          or (listp(x) and len(x) > 1 and lex_ps_p(x[0])))


def type_shifter_p(x):
  return (noun_reifier_p(x)
          or verb_reifier_p(x)
          or sent_reifier_p(x)
          or tensed_sent_reifier_p(x)
          or mod_n_former_p(x)
          or mod_a_former_p(x)
          or advformer_p(x)
          or detformer_p(x))


def prog_marker_p(x):
  return x == 'prog' or (listp(x) and len(x) == 2 and lex_tense_p(x[0]) and x[1] == 'prog')


def perf_marker_p(x):
  return x == 'perf' or (listp(x) and len(x) == 2 and lex_tense_p(x[0]) and x[1] == 'perf')


def aux_or_head_verb_p(x):
  return (aux_p(x) or tensed_aux_p(x) or suffix_check(x, 'vp-head')
          or (listp(x) and len(x) == 2 and lex_tense_p(x[0]) and suffix_check(x[1], 'vp-head')))


def noun_or_adj_p(x):
  return noun_p(x) or adj_p(x)


def invertible_verb_or_aux_p(x):
  return lex_invertible_verb_p(x) or aux_p(x)


GEN_PREDS = [
  plur_term_p,
  plur_partitive_p,
  plur_noun_p,
  plur_lex_noun_p,
  pasv_lex_verb_p,
  unknown_p,
  postmod_p,
  postmod_adj_p,
  verb_arg_p,
  verb_or_tensed_verb_p,
  sent_or_sent_mod_p,
  sent_or_tensed_sent_p,
  phrasal_sent_op_p,
  type_shifter_p,
  prog_marker_p,
  perf_marker_p,
  aux_or_head_verb_p,
  noun_or_adj_p,
  invertible_verb_or_aux_p
]

for pred in GEN_PREDS:
  tt.register_pred(pred, include_neg=True)



# ``````````````````````````````````````
# Search
# ``````````````````````````````````````



def marked_conjugated_vp_head_p(x):
  if isinstance(x, str):
    _, suffix = split_by_suffix(x)
    return suffix == 'conjugated-vp-head'
  elif listp(x):
    return len(x) == 2 and lex_tense_p(x[0]) and marked_conjugated_vp_head_p(x[1])
  return False


TT_VP_HEAD = [
  '!lex-verbaux-p',
  '!pasv-lex-verb-p',
  ['!lex-tense-p', '!vp-head-p']
]


def vp_head_p(x):
  return match_any(x, TT_VP_HEAD, apply_sub=False)


def search_vp_head(vp, sub=None):
  """Search a ULF verb phrase for the head, which is either the main verb or auxiliary/perf/prog over the VP.
  
  Parameters
  ----------
  vp : s-expr
    The ULF to search.
  sub : s-expr, optional
    A ULF to substitute for the head (if any).

  Returns
  -------
  head : s-expr
    The VP head.
  head_found : bool
    Whether a head was found.
  new_vp : s-expr
    The new verb phrase (if `sub` is given).
  """
  def rec(vp, sub):
    # Already marked conjugated VP head
    if marked_conjugated_vp_head_p(vp):
      return vp, True, (sub if sub else vp)
    # Simple tensed or not, lexical or passivized verb
    elif vp_head_p(vp):
      return vp, True, (sub if sub else vp)
    # Starts with a verb or auxiliary -- recurse into it
    elif listp(vp) and (verb_p(vp[0]) or tensed_verb_p(vp[0]) or tensed_aux_p(vp[0])):
      hv, found, new_carvp = rec(vp[0], sub)
      return hv, found, cons(new_carvp, vp[1:])
    # Starts with adv-a or phrasal sentence operator -- recurse into cdr
    elif listp(vp) and (adv_a_p(vp[0]) or phrasal_sent_op_p(vp[0])):
      hv, found, new_cdrvp = rec(vp[1:], sub)
      return hv, found, cons(vp[0], new_cdrvp)
    # Otherwise, it's not found
    return [], False, vp
  return rec(vp, sub)


def find_vp_head(vp):
  head, _, _ = search_vp_head(vp)
  return head
  

def replace_vp_head(vp, sub):
  """Find the main verb and return a new VP with the substitute value."""
  _, _, new_vp = search_vp_head(vp, sub=sub)
  return new_vp


TT_NP_POSTMOD_HEAD = [
  ['!lex-noun-postmod-macro-p', '!noun-p', '+expr']
]
  
def np_postmodification_head_p(x):
  return match_any(x, TT_NP_POSTMOD_HEAD, apply_sub=False)
  

def search_np_head(np, sub=None):
  """Search a ULF noun phrase for the head noun.
  
  Parameters
  ----------
  np : s-expr
    The ULF to search.
  sub : s-expr, optional
    A ULF to substitute for the head (if any).

  Returns
  -------
  head : s-expr
    The NP head.
  head_found : bool
    Whether a head was found.
  new_np : s-expr
    The new noun phrase (if `sub` is given).
  """
  def rec(np, sub):
    # Simple lexical or plural case
    if lex_noun_p(np) or lex_name_p(np):
      return np, True, (sub if sub else np)
    # Basic pluralized case
    elif (listp(np) and len(np) == 2 and np[0] == 'plur' and
          (lex_noun_p(np[1]) or lex_name_p(np[1]))):
      return np, True, (sub if sub else np)
    # Pluralized relational noun case
    elif listp(np) and len(np) == 2 and np[0] == 'plur' and listp(np[1]):
      return ['plur', np[1][0]], True, ([sub, np[1][1:]] if sub else np)
    # Noun post-modification
    elif np_postmodification_head_p(np):
      macro = np[0]
      inner_np = np[1]
      post = np[2:]
      hn, found, new_inner_np = rec(inner_np, sub)
      return hn, found, cons(macro, cons(new_inner_np, post))
    # Noun premodification or phrasal sent op
    elif (listp(np) and len(np) == 2
          and (mod_n_p(np[0]) or noun_p(np[0]) or adj_p(np[0]) or
               term_p(np[0]) or phrasal_sent_op_p(np[0]))
          and noun_p(np[1])):
      modifier = np[0]
      inner_np = np[1]
      hn, found, new_inner_np = rec(inner_np, sub)
      return hn, found, [modifier, new_inner_np]
    # Otherwise, noun followed by other stuff
    elif listp(np) and noun_p(np[0]):
      hn, found, new_inner_np = rec(np[0], sub)
      return hn, found, cons(new_inner_np, np[1:])
    # most-n
    elif listp(np) and len(np) == 3 and np[0] == 'most-n':
      hn, found, new_inner_np = rec(np[2], sub)
      return hn, found, [np[0], np[1], new_inner_np]
    # If none of these, can't find it
    else:
      return [], False, np
  return rec(np, sub)


def find_np_head(np):
  head, _, _ = search_np_head(np)
  return head
  

def replace_np_head(np, sub):
  """Find the main noun and return a new NP with the substitute value."""
  _, _, new_np = search_np_head(np, sub=sub)
  return new_np


TT_AP_PREMOD_HEAD = [
  ['!adj-premod-p', '*phrasal-sent-op-p', '!adj-p']
]


def ap_premodification_head_p(x):
  return match_any(x, TT_AP_PREMOD_HEAD, apply_sub=False)
  

TT_AP_POSTMOD_HEAD = [
  ['!adj-p', '+postmod-adj-p']
]


def ap_postmodification_head_p(x):
  return match_any(x, TT_AP_POSTMOD_HEAD, apply_sub=False)


def search_ap_head(ap, sub=None):
  """Search a ULF adjective phrase for the head adjective.
  
  Parameters
  ----------
  ap : s-expr
    The ULF to search.
  sub : s-expr, optional
    A ULF to substitute for the head (if any).

  Returns
  -------
  head : s-expr
    The AP head.
  head_found : bool
    Whether a head was found.
  new_np : s-expr
    The new adjective phrase (if `sub` is given).
  """
  def rec(ap, sub):
    # Simple lexical case
    if lex_adjective_p(ap):
      return ap, True, (sub if sub else ap)
    # Adjective premodification
    elif ap_premodification_head_p(ap):
      mods = ap[:-1]
      inner_ap = ap[-1]
      ha, found, new_inner_ap = rec(inner_ap, sub)
      return ha, found, mods+[new_inner_ap]
    # Adjective postmodification/arguments
    elif ap_postmodification_head_p(ap):
      inner_ap = ap[0]
      modargs = ap[1:]
      ha, found, new_inner_ap = rec(inner_ap, sub)
      return ha, found, cons(new_inner_ap, modargs)
    # Starting with phrasal sent ops
    elif listp(ap) and phrasal_sent_op_p(ap[0]):
      ha, found, new_cdrap = rec(ap[1:], sub)
      return ha, found, cons(ap[0], new_cdrap)
    # Starts with an adjective
    elif listp(ap) and adj_p(ap[0]):
      ha, found, new_carap = rec(ap[0], sub)
      return ha, found, cons(new_carap, ap[1:])
    # Otherwise, not found
    else:
      return [], False, ap
  return rec(ap, sub)


def find_ap_head(ap):
  head, _, _ = search_ap_head(ap)
  return head
  

def replace_ap_head(ap, sub):
  """Find the main adjective and return a new AP with the substitute value."""
  _, _, new_ap = search_ap_head(ap, sub=sub)
  return new_ap


SEARCH_PREDS = [
  marked_conjugated_vp_head_p,
  vp_head_p,
  np_postmodification_head_p,
  ap_premodification_head_p,
  ap_postmodification_head_p
]

for pred in SEARCH_PREDS:
  tt.register_pred(pred, include_neg=True)



# ``````````````````````````````````````
# Suffix
# ``````````````````````````````````````



SUFFIX_DICT = {
  'name' : 'name',
  'noun' : 'n',
  'adj' : 'a',
  'adv-a' : 'adv-a',
  'adv-e' : 'adv-e',
  'adv-s' : 'adv-s',
  'adv-f' : 'adv-f',
  'mod-a' : 'mod-a',
  'mod-n' : 'mod-n',
  'pp' : 'pp',
  'term' : 'pro',
  'verb' : 'v',
  'pred' : 'pred',
  'det' : 'd',
  'aux-v' : 'aux-v',
  'aux-s' : 'aux-s',
  'sent' : 'sent',
  'funct' : 'f'
}
"""A dict mapping ULF types to suffix extensions.

Notes
-----
TODO: complete type suffix list.
TODO: unify this system so all the lex-X? are defined from the list:
``(defun lex-[type]? (x) (in-ulf-lib-suffix-check x [suffix]))``

Also, make a hierarchy of types so we can choose the most specific, e.g.
pred : (verb, noun, adjective, preposition)
"""


def suffix_for_type(x):
  """Return the suffix for the type. If none found, return the type."""
  if x in SUFFIX_DICT:
    return SUFFIX_DICT[x]
  else:
    return x


def add_suffix(word, suffix):
  """Take a word string and a suffix and merge them together."""
  if not suffix:
    return word
  return f'{word}.{suffix}'


def suffix_check(x, suffix):
  """Check if a symbol has the given suffix."""
  if not isinstance(x, str):
    return False
  word, s = split_by_suffix(x)
  return s == suffix.lower()


def split_by_suffix(x):
  """Split a symbol by its suffix."""
  if not isinstance(x, str):
    return x
  if not '.' in x:
    return x, ''
  else:
    return x.split('.')


def has_suffix(x):
  """Check if a symbol has a suffix."""
  if not isinstance(x, str):
    return False
  else:
    return len(x.split('.')) == 2


def strip_suffix(str):
  """Strips the suffix, marked with '.', from a string.
  
  E.g., man.n -> man

  If there are multiple periods in a string, only the substring after the last
  period is stripped.
  """
  split = str.split('.')
  if len(split) == 1:
    return str
  base_ret = '.'.join(split[:-1])
  suffix = split[-1]
  # If space in suffix, then don't strip
  if ' ' in suffix:
    return str
  # If the suffix is completely numerical, then don't strip
  elif suffix.isdigit():
    return str
  else:
    return base_ret



# ``````````````````````````````````````
# Macro
# ``````````````````````````````````````



def contains_hole(ulf, holevar='*h'):
  """Return True if `ulf` contains `holevar`, False otherwise."""
  if atom(ulf) and ulf == holevar:
    return True
  elif atom(ulf):
    return False
  elif not ulf:
    return False
  else:
    return contains_hole(ulf[0], holevar=holevar) or contains_hole(ulf[1:], holevar=holevar)


def add_info_to_var(curulf, var, srculf):
  """Add types, pluralization, etc. to a given variable.
  
  Assumes there's at most one occurrence of `var` in `curulf`.

  Notes
  -----
  TODO: For now just take the first type (we should use a hierarchy
  of types to select the most specific one.
  """
  typ = phrasal_ulf_type(srculf)[0]
  typeadded = add_suffix(var, suffix_for_type(typ))
  if plur_noun_p(srculf):
    replacement = ['plur', typeadded]
  elif plur_term_p(srculf):
    replacement = ['plur-term', typeadded]
  else:
    replacement = typeadded
  return subst(replacement, var, curulf)


def add_info_to_sub_vars(ulf):
  """Add types, pluralization, etc. to the variables *h for sub macros."""
  def rec(ulf):
    if atom(ulf):
      return ulf
    elif ulf[0] == 'sub' and len(ulf) < 3:
      return rec(ulf[1])
    elif ulf[0] == 'sub':
      left = rec(ulf[1])
      right = rec(ulf[2])
      return ['sub', left, add_info_to_var(right, '*h', left)]
    else:
      return [rec(x) for x in ulf]
  return rec(ulf)


def add_info_to_relativizer(curulf, srculf):
  """Add types, pluralization, etc. to a given relativizer.
  
  Assumes there's at most one relativizer in `curulf`.
  """
  origrel = rec_find_if(curulf, lex_rel_p)[0]
  # Right now, all we care about is plurality
  if plur_term_p(srculf) or plur_noun_p(srculf):
    replacement = ['plur-term', origrel]
  else:
    replacement = origrel
  if origrel:
    return subst(replacement, origrel, curulf)
  else:
    return curulf
  

def add_info_to_relativizers(ulf):
  """Add pluralization, etc. to the relativizers in relative clauses."""
  def rec(ulf):
    if atom(ulf):
      return ulf
    # If n+preds, n+post, np+preds, recurse into elements and apply info of first arg to others
    elif lex_noun_or_np_postmod_macro_p(ulf[0]) and len(ulf) > 2:
      recvals = [rec(x) for x in ulf]
      macro = recvals[0]
      headexpr = recvals[1]
      postmods = recvals[2:]
      return cons(macro, cons(headexpr, [add_info_to_relativizer(expr, headexpr) for expr in postmods]))
    # Otherwise, just recurse
    else:
      return [rec(x) for x in ulf]
  return rec(ulf)


def var_insertion_macro(name, var,
                        context_selector_fn,
                        insertion_selector_fn,
                        bad_use_fn):
  """General function for variable insertion macros.
  
  Given a macro name, variable symbol, a context selector function, and insertion selector function,
  returns a function that applies this macro to a given ulf.
  
  For example:

    - `name`: ``'sub'``
    - `var`: ``'*h'``
    - `context_selector_fn: ``lambda x: x[2]``
    - `insertion_selector_fn`: ``lambda x: x[1]``
    - `bad_use_fn`: ``lambda x: not (listp(x) and x[0] == 'sub' and len(x) == 3)``
  
  Returns a function that applies all macros.
  """
  def macro_expand_fn(ulf, fail_on_bad_use):
    nonlocal name, var, context_selector_fn, insertion_selector_fn, bad_use_fn
    
    if atom(ulf):
      return True, ulf
    # If name and not the right use arguments, fail
    elif ulf[0] == name and (len(ulf) < 3 or (fail_on_bad_use and bad_use_fn(ulf))):
      return False, ulf
    # Otherwise if name, apply macro
    elif ulf[0] == name:
      recres = [macro_expand_fn(x, fail_on_bad_use) for x in ulf]
      sucs = [r[0] for r in recres]
      ress = [r[1] for r in recres]
      # If recursion failed, propagate results
      if not all(sucs):
        return False, ress
      # If recursive result doesn't have a hole, return with failure
      elif fail_on_bad_use and len([x for x in ress if contains_hole(x, holevar=var)]) == 0:
        return False, ress
      # Apply substitution and return result
      else:
        return True, subst(insertion_selector_fn(ress), var, context_selector_fn(ress))
    # Otherwise, just recurse into all. If failure, return it, otherwise merge together.
    else:
      recres = [macro_expand_fn(x, fail_on_bad_use) for x in ulf]
      sucs = [r[0] for r in recres]
      ress = [r[1] for r in recres]
      # If recursion succeeded, return the results
      if all(sucs):
        return True, ress
      # Otherwise, return the first one that failed
      else:
        return False, ress[sucs.index(False)]
      
  return lambda ulf, fail_on_bad_use: macro_expand_fn(ulf, fail_on_bad_use)[1]


def apply_sub_macro(ulf, fail_on_bad_use=False):
  """Apply a sub macro."""
  sub_fn = var_insertion_macro('sub', '*h',
                               lambda x: x[2],
                               lambda x: x[1],
                               lambda x: not (listp(x) and (x[0] == 'sub') and len(x) == 3))
  return sub_fn(ulf, fail_on_bad_use)


def apply_rep_macro(ulf, fail_on_bad_use=False):
  """Apply a rep macro."""
  rep_fn = var_insertion_macro('rep', '*p',
                               lambda x: x[1],
                               lambda x: x[2],
                               lambda x: not (listp(x) and (x[0] == 'rep') and len(x) == 3))
  return rep_fn(ulf, fail_on_bad_use)


def apply_qt_attr_macro(ulf):
  """Apply a qt_attr macro."""
  def rec(ulf):
    if atom(ulf):
      return True, ulf, []
    # If possible to apply (\" (.. (qt-attr (.. *qt ..)) ..) \"), recurse and try to apply.
    elif len(ulf) >= 3 and ulf[0] == '"' and ulf[-1] == '"':
      part = ulf[1] if len(ulf) == 3 else ulf[1:-1]
      suc, res, qt_attr = rec(part)
      if qt_attr:
        return True, subst(['"', res, '"'], '*qt', qt_attr), []
      else:
        return suc, ['"', res, '"'], qt_attr
    # If starting with 'qt-attr, recurse, but then return recursive result
    # in the last slot and return nil for the main clause.
    elif len(ulf) == 2 and ulf[0] == 'qt-attr' and contains_hole(ulf[1], holevar='*qt'):
      suc, res, _ = rec(ulf[1])
      return suc, [], res
    # TODO: handle malformed cases (e.g. (\" ... \") is more than length 3 (qt-attr ..) is more than length 2)
    # Otherwise just recursive into everything, filter nil in recursive result.
    else:
      recres = [rec(x) for x in ulf]
      sucs = [r[0] for r in recres]
      ress = [r[1] for r in recres if r[1]]
      qt_attrs = [r[2] for r in recres if r[2]]
      qt_attr = qt_attrs[0] if qt_attrs else []
      return all(sucs), ress, qt_attr
  
  suc, res, qt_attr = rec(ulf)
  if not suc or qt_attr:
    return ulf
  else:
    return res


def apply_substitution_macros(ulf):
  """Apply all substitution macros: sub, rep, qt-attr."""
  return apply_qt_attr_macro(apply_rep_macro(apply_sub_macro(ulf)))



# ``````````````````````````````````````
# Util
# ``````````````````````````````````````



def make_explicit(token):
  """Make an elided ULF token explicit, e.g., {he}.pro -> he.pro."""
  if not atom(token):
    return token
  
  return token.replace('{', '').replace('}', '')
# Python ULF Library

Python library for interfacing with and manipulating unscoped episodic logical forms (ULF), based on the [original Common Lisp implementation](https://github.com/genelkim/ulf-lib) by Gene Kim.

Additional information can be found at the [ULF project page](https://www.cs.rochester.edu/u/gkim21/ulf/).

## Dependencies

* [transduction](https://pypi.org/project/transduction/)
* [memoization](https://pypi.org/project/memoization/)

## Summary

Install the package using `pip install ulflib`.

Import the package using the following line.

```python
from ulflib import ulflib
```

## Documentation

### Lexical match predicates

The following match functions are made available for matching individual lexical items (intended for use with the [transduction](https://pypi.org/project/transduction/) package). Refer to the [ULF annotation guidelines](https://www.cs.rochester.edu/u/gkim21/ulf/assets/doc/ulf_annotation_guideline_v1.pdf) for additional details on the ULF lexical categories.

Upon importing this package, each lexical match function is registered with the transduction package and can be accessed in transduction rules using the corresponding predicates, e.g., `!lex-noun-p` or `*lex-noun-p`. The negated versions of the predicates are also registered, e.g., `!not-lex-noun-p`.

```python
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
```


### Phrasal match predicates

The following match functions are made available for matching phrasal ULF categories:

```python
PHRASE_PREDS = [
  noun_p,
  adj_p,
  adj_premod_p,
  adj_postmod_p,
  adv_a_p,
  adv_e_p,
  adv_s_p,
  adv_f_p,
  adv_p,
  mod_a_p,
  mod_n_p,
  mod_a_former_p,
  mod_n_former_p,
  pp_p,
  term_p,
  verb_p,
  pred_p,
  det_p,
  aux_p,
  tensed_aux_p,
  tensed_verb_p,
  sent_p,
  tensed_sent_p,
  sent_punct_p,
  sent_mod_p,
  ps_p,
  noun_reifier_p,
  verb_reifier_p,
  sent_reifier_p,
  tensed_sent_reifier_p,
  advformer_p,
  detformer_p,
  modformer_p,
  preposs_macro_p,
  relativized_sent_p,
  p_arg_p,
  voc_p,
]
```


### General match predicates

The following additional (uncategorized) match predicates are also defined:

```python
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
```


### Search

The following functions can be used to search for the heads of verb phrases, noun phrases, and adjective phrases within a ULF, respectively:

```python
find_vp_head(vp)
find_np_head(np)
find_ap_head(ap)
```

Additionally, the following functions find and replace the heads with some given value `sub`:

```python
replace_vp_head(vp, sub)
replace_np_head(np, sub)
replace_ap_head(ap, sub)
```

The following match functions are also defined (mostly used internally by the above functions):

```python
SEARCH_PREDS = [
  marked_conjugated_vp_head_p,
  vp_head_p,
  np_postmodification_head_p,
  ap_premodification_head_p,
  ap_postmodification_head_p
]
```


### Suffix

The following functions are defined for manipulating the suffix of a ULF lexical item:

```python
suffix_for_type(x)
"""Return the suffix for the type. If none found, return the type."""

add_suffix(word, suffix)
"""Take a word string and a suffix and merge them together."""

suffix_check(x, suffix)
"""Check if a symbol has the given suffix."""

split_by_suffix(x)
"""Split a symbol by its suffix."""

has_suffix(x)
"""Check if a symbol has a suffix."""

strip_suffix(str)
"""Strips the suffix, marked with '.', from a string, e.g., man.n -> man."""
```


### Macro

The following top-level functions are defined for processing macros in ULFs:

```python
add_info_to_sub_vars(ulf)
"""Add types, pluralization, etc. to the variables *h for sub macros."""

add_info_to_relativizers(ulf)
"""Add pluralization, etc. to the relativizers in relative clauses."""

apply_sub_macro(ulf, fail_on_bad_use=False)
"""Apply a sub macro."""

apply_rep_macro(ulf, fail_on_bad_use=False)
"""Apply a rep macro."""

apply_qt_attr_macro(ulf)
"""Apply a qt_attr macro."""

apply_substitution_macros(ulf)
"""Apply all substitution macros: sub, rep, qt-attr."""
```
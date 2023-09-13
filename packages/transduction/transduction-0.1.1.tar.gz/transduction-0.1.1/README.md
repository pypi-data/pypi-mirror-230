# Python Tree Transduction (TT)

This package implements a "minimal" pattern-based tree transduction language for Python. This is originally based on the [TTT tree transduction language](https://www.cs.rochester.edu/~schubert/papers/ttt-atanlp12.pdf) and [Common Lisp implementation](https://github.com/genelkim/ttt); however, it employs a less powerful, but simpler, pattern-matching syntax.

Tree transduction allows for mapping any "S-Expression" (i.e., a recursively nested list of lists, where non-lists are atoms) to another S-Expression using a set of rules, where each rule consists of a *match pattern* and a *fill template*. The match pattern specifies a (sub-)expression to match, and the fill template provides a (sub-)expression to replace the matched expression with. 

Patterns can contain custom regex-like predicates as well as tokens matching arbitrary spans of atoms, or features assigned to atoms. Templates can have indices that refer to positions within the matched expression, as well as custom computable predicates. The syntax for patterns and templates is detailed below.

## Summary

Install the package using `pip install transduction`.

Import the package using the following line. No dependencies are required.

```python
from transduction import tt
```

The package exports the following functions (see the below sections for additional details on the parameters):

### match

```python
tt.match(pa, ex, feats={}, preds={})
```

Where `pa` is a match pattern, `ex` is an expression to match, `feats` is an optional dict of feature lists assigned to symbols, and `preds` is an optional dict mapping custom match predicate names to functions.

If a match is obtained, the function returns an S-Expression resembling the matched expression, except using `[:seq, ...]` to wrap sequences that were matched to a sequence-variable in the pattern. If no match is obtained, the empty list `[]` is returned.

Examples:

```python
pa = ['a', '.testfeat', ['x', 2, 'z'], '?expr']
ex = ['a', 'b', ['x', 'y', 'z'], 'x']
feats = {'b':['testfeat']}
print(tt.match(pa, ex, feats=feats))
# -> ['a', 'b', ['x', [':seq', 'y'], 'z'], [':seq', 'x']]
```

```python
pa = ['a', '.testfeat', ['x', 2, 'z'], '?expr']
ex = ['a', 'c', ['x', 'y', 'y', 'y', 'z'], 'x', 'z']
feats = {'b':['testfeat']}
print(tt.match(pa, ex, feats=feats))
# -> []
```

### fill_template

```python
tt.fill_template(template, match_result, preds={})
```

Where `template` is a fill template, `match_result` is a result from a match, and `preds` is an optional dict mapping custom match predicate names to functions.

The function returns an S-Expression resembling the template, with indices in the template filled with the corresponding sequences from the match results.

Example:

```python
template = [['testpred!', '1', '2'], '3.1', 'test', '3.3', '4']
match_result = ['a', 'b', ['x', [':seq', 'y'], 'z'], [':seq', 'x']]
def testpred(*args):
  return '-'.join(args)
preds={'testpred':testpred}
print(tt.fill_template(template, match_result, preds=preds))
# -> ['a-b', 'x', 'test', 'z', 'x']
```

### apply_rules

```python
tt.apply_rules(rules, expr, feats={}, preds={}, rule_order='slow-forward', shallow=False, max_n=1000)
```

Where `rules` is a list of rules to apply to `expr`, and `feats` and `preds` are dicts of custom symbol features and custom predicates (as above).

Each rule is a tuple `(pattern, template)`, where a successful application of the rule matches a (sub-)expression and replaces it with the filled template. If `shallow=True` is given as an argument, the rule will only be applied to the root expression; otherwise it will be applied to the first matching sub-expression in a recursive traversal of the root expression.

The following `rule_order` modes are supported:

* `slow-forward` - apply each rule until that rule no longer applies, possibly repeating the entire sequence.
* `earliest-first` - always apply the first rule in the list that is applicable, repeat until no rules are applicable (the rule list may be processed multiple times).
* `fast-forward` - apply each rule at most once, in order, repeating the list until convergence.

The parameter `max_n` can be used to set a limit on the number of rule applications.

The function returns the final S-Expression after applying each rule to `expr` until convergence.

Examples:

```python
rules = [
  (['c', 'd'], 'z')
]
expr = ['c', 'd']
print(tt.apply_rules(rules, expr, shallow=True))
# -> z
```

```python
rules = [
  (['c', 'd'], 'z'),
  ('e', ['c', 'd']),
  ('e', 'x'),
  (['c', 'd'], 'y')
]
expr = ['a', ['b', [['c', 'd'], 'e', ['q', ['e', ['c', 'd']]]], 'f', 'g'], 'h']

print(tt.apply_rules(rules, expr, rule_order='slow-forward'))
# -> ['a', ['b', ['z', 'y', ['q', ['y', 'z']]], 'f', 'g'], 'h']

print(tt.apply_rules(rules, expr, rule_order='earliest-first'))
# -> ['a', ['b', ['z', 'z', ['q', ['z', 'z']]], 'f', 'g'], 'h']

print(tt.apply_rules(rules, expr, rule_order='fast-forward'))
# -> ['a', ['b', ['z', 'y', ['q', ['x', 'z']]], 'f', 'g'], 'h']
```

### apply_rule

```python
tt.apply_rule(rule, expr, feats={}, preds={}, shallow=False, max_n=1000):
```

This is identical to `apply_rules`, except only applies a single rule (hence, the rule order modes are unnecessary).

Example:

```python
rule = (
  [1, '*is-a', 'test', 0],
  ['1', ['testpred!', '2', '3'], '4']
)
expr = ['z', 'a', 'a', 'a', 'test', 'x']
def is_a(x):
  return x == 'a'
def testpred(*args):
  return '-'.join(args)
preds={'is-a':is_a, 'testpred':testpred}
print(tt.apply_rule(rule, expr, preds=preds))
# -> ['z', 'a-a-a-test', 'x']
```


## Pattern syntax

A pattern is an S-Expression where each atom may be:

* A custom predicate of form `!<pred>`, `?<pred>`, `*<pred>`, or `+<pred>`, interpreted as matching exactly one expression, 0 or 1 expression, 0 or more expressions, or 1 or more expressions, respectively (i.e., the same meanings that these symbols carry in regex). The following basic predicates are supported by default: `expr`, `atom`, and `lst`, being true respectively of any expression, an atom, or a list. Additional custom match predicates may be defined (see below).
* An integer >= 0, where 0, 1, 2, ... respectively mean "zero or more expressions", "at most one expression", "at most 2 expressions", at most 3 expressions", etc.
* A dotted atom, such as `.verb` or `.branch-of-math`, i.e., starting with a dot and denoting features of symbols, as defined by the `feats` argument. These are matched by checking whether a given expression is connected to the feature through a chain of "is-a" connections.
* Any other atom, which simply matches an identical atom in the expression.


## Template syntax

A template is an S-Expression containing:

* Positional indicators such as 3, 3.2, 3.3.2, etc., where pieces of the match result are to be placed. E.g., here, the references are to the 3rd element of the match result, the 2nd element of the 3rd element of the match result, etc. The index 0 is special, as it refers to the (flattened) match result as a whole.
* Evaluable predicates ending in '!' applied to some arguments, e.g., ``[lex-ulf!, v, 3.2]``, in which case the result of the predicate called on the given arguments will filled in place. Custom predicates must be defined (see below), and their argument signatures must match the arguments provided in the template.


## Defining custom word features

Custom word features can be provided to allow dotted atoms such as `.verb` or `.branch-of-math` in match patterns. These should be provided to the above functions as a dict mapping symbols to lists of features. Note that features may be connected to symbols indirectly, i.e., a dotted atom may correspond to a feature in the feature list of another feature, which in turn is a feature of the word in the given expression.

Example:

```python
feats = {
  'can' : ['modal-verb', 'noun'],
  'should' : ['modal-verb'],
  'might' : ['modal-verb'],
  'modal-verb' : ['verb'],
  'go' : ['verb'],
  'calculus' : ['branch-of-math'],
  'algebra' : ['branch-of-math']
}
```


## Defining custom predicates

There are two types of custom predicates: those used in matching (indicated by a `!`, `?`, `*`, or `+` prefix), and evaluable predicates used in filling templates (indicated by a `!` suffix). Both predicates are defined in the same way. However, the former type of predicate should take a single variable as an argument and return a boolean value, whereas the latter type of predicate should have a specific argument signature, and return a single value.

Examples:

```python
def custom_match_pred(x):
  return isinstance(x, list) and x[0] == 'test'

def custom_eval_pred(arg1, arg2, arg3):
  return f'{arg1}: {int(arg2)+int(arg3)}'
```

Note that predicate names should always replace underscores in the function names with `-`. So the predicates for the above would be `!custom-match-pred` and `custom-eval-pred!`, respectively.

Custom predicates can be supplied in two different ways. First, they can be added directly to the list of supported predicates using the following function:

```python
tt.register_pred(custom_match_pred)
tt.register_pred(custom_eval_pred)
```

If the optional argument `include_neg` is given as `True`, the negated version of the predicate will also be added (i.e., one that will return true in cases where the original pred turns false). This will have the name `not-<original_pred>`.

```python
tt.register_pred(custom_match_pred, include_neg=True)
```

Second, they can be supplied as a dict argument to the above functions:

```python
preds = {
  'custom-match-pred' : custom_match_pred,
  'custom-eval-pred' : custom_eval_pred
}
```
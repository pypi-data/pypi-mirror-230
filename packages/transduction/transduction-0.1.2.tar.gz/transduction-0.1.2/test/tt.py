import sys
sys.path.append("src/")

from transduction import tt

def is_a(x):
  return True if x=='a' else False

def testpred(*args):
  return '-'.join(args)

tt.register_pred(is_a, include_neg=True)

pa = ['a', '.testfeat', ['x', 2, 'z'], '?expr']
ex = ['a', 'b', ['x', 'y', 'z'], 'x']
feats = {'b':['testfeat']}
print(tt.match(pa, ex, feats=feats))
# -> ['a', 'b', ['x', [':seq', 'y'], 'z'], [':seq', 'x']]

pa = ['a', '.testfeat', ['x', 2, 'z'], '?expr']
ex = ['a', 'c', ['x', 'y', 'y', 'y', 'z'], 'x', 'z']
feats = {'b':['testfeat']}
print(tt.match(pa, ex, feats=feats))
# -> []

template = [['testpred!', '1', '2'], '3.1', 'test', '3.3', '4']
match_result = ['a', 'b', ['x', [':seq', 'y'], 'z'], [':seq', 'x']]
def testpred(*args):
  return '-'.join(args)
preds={'testpred':testpred}
print(tt.fill_template(template, match_result, preds=preds))
# -> ['a-b', 'x', 'test', 'z', 'x']

print(tt.apply_rule(
  ([1, '*is-a', 'test', 0],
   ['1', ['testpred!', '2', '3'], '4']),
  ['z', 'a', 'a', 'a', 'test', 'x'],
  preds={'testpred':testpred}))
# -> ['z', 'a-a-a-test', 'x']

print(tt.apply_rule(
  ([1, '*not-is-a', 'test', 0],
   ['1', ['testpred!', '2', '3'], '4']),
  ['z', 'b', 'c', 'b', 'test', 'x'],
  preds={'testpred':testpred}))
# -> ['z-b-c-b-test', 'x']

print(tt.apply_rule(
  ([1, '*not-is-a', 'test', 0],
   ['1', ['testpred!', '2', '3'], '4']),
  ['z', 'b', 'a', 'b', 'test', 'x'],
  preds={'testpred':testpred}))
# -> ['z', 'b', 'a', 'b', 'test', 'x']

print(tt.apply_rules(
  [
    (['c', 'd'], 'z')
  ],
  ['c', 'd'],
  shallow=True
  ))
# -> z

print(tt.apply_rules(
  [
    (['c', 'd'], 'z'),
    ('z', ['c', 'd'])
  ],
  ['a', ['b', [['c', 'd'], 'e', ['q', ['e', ['c', 'd']]]], 'f', 'g'], 'h'],
  shallow=False,
  rule_order='slow-forward'
  ))
# -> ['a', ['b', [['c', 'd'], 'e', ['q', ['e', ['c', 'd']]]], 'f', 'g'], 'h']


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
"""Methods for matching a TT pattern to an S-expression and filling in a corresponding template."""

from transduction.util import expr, listp, atom, cons

DEFAULT_PREDS = {
  'expr' : expr,
  'atom' : atom,
  'lst'  : listp,
  'list' : listp
}

def register_pred(f, include_neg=False):
  global DEFAULT_PREDS
  pred = f.__name__.replace('_', '-')
  if pred in DEFAULT_PREDS:
    raise Exception(f'Predicate {pred} is already registered')
  DEFAULT_PREDS[pred] = f

  if include_neg:
    pred_neg = 'not-'+pred
    if pred_neg in DEFAULT_PREDS:
      raise Exception(f'Predicate {pred_neg} is already registered')
    DEFAULT_PREDS[pred_neg] = lambda x: not f(x)



def ok(x):
  return x != ':nil'

def dot_atom(x):
  return isinstance(x, str) and x != '.' and x[0] == '.'

def q_var(x):
  return isinstance(x, str) and x != '?' and x[0] == '?'

def e_var(x):
  return isinstance(x, str) and x != '!' and x[0] == '!'

def s_var(x):
  return isinstance(x, str) and x != '*' and x[0] == '*'

def p_var(x):
  return isinstance(x, str) and x != '+' and x[0] == '+'

def pred_var_any(x):
  chrs = ['!', '?', '*', '+']
  return isinstance(x, str) and x not in chrs and x[0] in chrs

def num_var(x):
  return (isinstance(x, int) or (isinstance(x, str) and x.isdigit())) and int(x) >= 0

def dec_num_var(x):
  if isinstance(x, int):
    return x-1
  else:
    return str(int(x)-1)
  
def match_var(x):
  return num_var(x) or pred_var_any(x)

def seq_var(x):
  return num_var(x) or (match_var(x) and not e_var(x))

def soft_var(x):
  if num_var(x):
    return x
  elif match_var(x) and x[0] in ['?', '*']:
    return x
  else:
    return None

def hard_atom(x):
  return isinstance(x, str) and not soft_var(x)

def underlying_feat(x):
  return x[1:] if isinstance(x, str) else ''


def flatten_sequences(expr):
  """Flatten lists marked as sequences, i.e., of the form ``[:seq, ...]``.
  
  ``[:seq, ...]`` expressions are not allowed to contain such expressions as sequence elements (i.e., these
  would not be flattened. It would be easy to allow them, but for the pattern transductions here no such
  embeddings occur, because sequence expressions are match-values of single sequence variables, like *atom
  or +expr, and these are matched only against input expressions free of sequence expressions.)

  A top-level expr like ``[:seq, a]`` or ``[:seq, []]`` or ``[:seq, [a, b]]`` becomes ``a``, ``[]``, or ``[a, b]`` respectively,
  i.e., a 1-element sequence is turned into that one element. However, an empty sequence ``[:seq]`` or longer
  sequence like ``[:seq, a, b]`` is left unchanged, since removing ``[:seq, ...]`` doesn't leave a single valid expression.
  """
  if atom(expr):
    return expr
  elif expr[0] == ':seq':
    return expr[1] if len(expr) == 2 else expr
  elif atom(expr[0]):
    return cons(expr[0], flatten_sequences(expr[1:]))
  elif expr[0][0] == ':seq':
    return expr[0][1:] + flatten_sequences(expr[1:])
  else:
    return cons(flatten_sequences(expr[0]), flatten_sequences(expr[1:]))


def indexed_element_of(expr, index):
  """Obtains the element of an expression located at a nested index (an integer or list of integers)."""
  if index == 0:
    return flatten_sequences(expr)
  elif not listp(expr):
    raise Exception(f'Bad first argument in indexed_element_of({expr}, {index})')
  elif isinstance(index, int):
    return expr[index-1]
  elif not index or not all([isinstance(i, int) for i in index]):
    raise Exception(f'Bad second argument in indexed_element_of({expr}, {index})')
  else:
    result = expr
    for i in index:
      result = result[i-1]
    return result


def s_variant_of_p_var(p_var):
  """Return the *-variant of the given +-var."""
  return '*' + p_var[1:]


def val(var, expr, preds={}):
  """Determine whether a predicate is true of a given expression.
  
  If `var` is a multi-character atom starting with '!', then it's expected
  to have a function definition corresponding to the string following the '!'.
  If it starts with ?/*/+ then the corresponding !-predicate must be obtained
  through string manipulation. If `var` is a nonnegative integer then the
  corresponding predicate is !expr, which is true of any expression.

  Parameters
  ----------
  var : str
    Either a non-negative integer or a match variable with {!,?,*,+} as a prefix.
  expr : s-expr
    An S-expression to check.
  preds : dict, optional
    A dict mapping predicate names to functions implementing those predicates.
  
  Returns
  -------
  bool
  """
  if num_var(var):
    return True
  elif var in ['!', '?', '*', '+']:
    raise Exception(f'{var} is not allowed as a variable')
  else:
    fname = var[1:]
    if fname in DEFAULT_PREDS:
      f = DEFAULT_PREDS[fname]
    elif fname in preds:
      f = preds[fname]
    else:
      raise Exception(f'Predicate {fname} does not exist')
    return f(expr)
  

def isa(x, feat, feats):
  """Determine whether a given word has a given feature.

  NB: an atom is always assumed to have itself as a feature. If this is
  not desired, define it as a custom !predicate rather than a feature.

  Parameters
  ----------
  x : str
    A word (e.g., ``surgeon`` or ``doctor``).
  feat : str
    A feature string (e.g., ``professional``).
  feats : dict
    A dict mapping words to feature lists.

  Returns
  -------
  bool
  """
  # Base cases: feat is a direct match
  if x == feat:
    return True
  if dot_atom(x):
    x = x[1:]
  if dot_atom(feat):
    feat = feat[1:]
  if x == feat:
    return True
  
  ff = feats[x].copy() if x in feats else []
  # Frequent case: feat is a member of the feature list of x
  if feat in ff:
    return True
  if not ff:
    return False
  
  # Otherwise, perform a BFS to see if any feature in the feature
  # list of x has feat, etc.
  closed = [x, feat]
  while ff:
    f = ff.pop()
    if f not in closed:
      fff = feats[f] if f in feats else []
      if fff:
        if feat in fff:
          return True
        closed.append(f)
        ff = list(set(fff).union(set(ff)))
        ff = [x for x in ff if x != f]
      if not ff:
        return False
  return False


def match(pa, ex, feats={}, preds={}):
  """Match a given pattern S-expression to an input S-expression.
  
  :nil results from match_rec are mapped to an empty list, under the assumption
  that the ``match_rec([], [])`` case is unnecessary for Eta rule trees.

  Parameters
  ----------
  pa : s-expr
    A pattern, which is any S-expression where atoms may be:
      - A custom predicate of form ``!<pred>``, ``?<pred>``, ``*<pred>``, or ``+<pred>``,
        interpreted as matching exactly one expression, 0 or 1 expression,
        0 or more expressions, or 1 or more expressions, respectively. Custom
        predicates must be defined in eta.util.tt.preds. Some basic ones are
        'expr', 'atom', and 'lst', being true respectively of any expression,
        an atom, or a list.
      - An integer >= 0, where 0, 1, 2, ... respectively mean "zero or more expressions",
        "at most one expression", "at most 2 expressions", at most 3 expressions", etc.
      - A dotted atom, such as ``.verb`` or ``.branch-of-math``, i.e., starting with a dot and
        denoting features of atoms, as defined by the `feats` argument. These are matched
        by checking whether a given expression is connected to the feature through a chain
        of 'isa' connections.
      - Any other atom, which simply matches an identical atom in `ex`.
  ex : s-expr
    The input to match.
  feats : dict, optional
    A dict mapping a word w to a feature list x1, ..., xk, such that
    ``isa(w, xi)`` for each feature xi.
  preds : dict, optional
    A dict mapping predicate names to functions implementing those predicates.

  Returns
  -------
  s-expr
    An empty list ``[]`` if no match, otherwise an S-expression containing the
    result of the match. The result will resemble the input expression `ex`,
    except that sequences of 0 or more constituents matched by sequence variables
    will be encoded as ``[:seq, <item1>, <item2>, ...]``.
  """
  def match_rec(pa, ex):
    nonlocal feats, preds

    # An empty pa is a success if and only if matched with an empty ex
    if not pa:
      return [] if not ex else ':nil'
    
    # A null ex can be matched by non-null pa only if either pa is a hard
    # match variable that succeeds on [], or it is a list of "soft" variables
    # that can match empty sequences.
    if not ex:
      if num_var(pa):
        return [':seq', []]
      elif match_var(pa) and val(pa, [], preds=preds):
        return [':seq', []] if seq_var(pa) else []
      elif listp(pa):
        if any([listp(x) or hard_atom(x) for x in pa]):
          return ':nil'
        return [[':seq'] for x in pa]
      else:
        return ':nil'
      
    # Both pa and ex are non-null atoms
    if atom(pa) and not match_var(pa) and pa == ex:
      return ex
    
    # pa is a feature (dot-atom) not equivalent to ex
    if dot_atom(pa):
      feat = underlying_feat(pa)
      if atom(ex) and isa(ex, feat, feats):
        return ex
      else:
        return ':nil'
      
    # pa, ex are non-null, pa doesn't test a feature of ex, and if pa = ex and they
    # are atoms, then pa is a match variable & ex happens to "look like" a match variable
    # but is just an expression (or part of an expression) being matched.
    if atom(pa):
      if match_var(pa) and val(pa, ex, preds=preds):
        return [':seq', ex] if seq_var(pa) else ex
      else:
        return ':nil'
      
    # Either pa is an atom not matching ex, or is a non-null list; so it can't match an atom
    if atom(ex):
      return ':nil'
    
    # At this point, pa and ex are lists. So there are 7 cases depending on the first element
    # of pa (p) and the first element of ex (e):
    if not listp(pa) or not listp(ex):
      raise Exception(f'Unexpected condition in match_rec({pa}, {ex})')
    p = pa[0]
    e = ex[0]

    # 1. If p is a list, try matching it to e, and if successful, recurse on the tails of pa and ex.
    if listp(p):
      m = match_rec(p, e)
      if ok(m):
        mm = match_rec(pa[1:], ex[1:])
        if ok(mm):
          return cons(m, mm)
      return ':nil'
    
    # In remaining cases 2-7, initial element p is a non-nil atom.
    # ````````````````````````````````````````````````````````````

    # 2. For non-variable p, if it is equal to, or successfully tests a feature
    # of the 1st element of ex, we recurse on the tails of pa and ex, otherwise fail
    if not match_var(p):
      feat = None
      if dot_atom(p):
        feat = underlying_feat(p)
      if p == e or (feat and isa(e, feat, feats)):
        mm = match_rec(pa[1:], ex[1:])
        if ok(mm):
          return cons(e, mm)
      return ':nil'
    
    # 3. For integer p >= 0: if p = 0, do the match with p replaced by *expr;
    # for p = 1, do the match with p replaced by ?expr; for an integer
    # (numeric var) >= 2, we try an empty match, and try to recurse using the
    # tail of pa; if this fails, we try matching [p-1, ...] to the tail of ex,
    # combining [:seq, e] with the match result for p-1 if successful; otherwise fail
    if num_var(p):
      if int(p) == 0:
        return match_rec(cons('*expr', pa[1:]), ex)
      elif int(p) == 1:
        return match_rec(cons('?expr', pa[1:]), ex)
      else:
        mm = match_rec(pa[1:], ex)
        if ok(mm):
          return cons([':seq'], mm)
        else:
          p = '?expr' if int(p) == 2 else dec_num_var(p)
          mm = match_rec(cons(p, pa[1:]), ex[1:])
          if ok(mm):
            return cons(cons(':seq', cons(e, mm[0][1:])), mm[1:])
      return ':nil'

    # 4. For a !-variable p, we try an initial element match, and if successful,
    # recurse on the tails of pa and ex.
    if e_var(p):
      m = match_rec(p, e)
      if ok(m):
        mm = match_rec(pa[1:], ex[1:])
        if ok(mm):
          return cons(m, mm)
      return ':nil'
    
    # 5. For a ?-variable, we try preprending [:seq] to a recursive match of the
    # the tail of pa to ex; if the recursion fails, we try an initial-element match,
    # and if successful, recurse on the tails of pa & ex.
    if q_var(p):
      mm = match_rec(pa[1:], ex)
      if ok(mm):
        return cons([':seq'], mm)
      else:
        m = match_rec(p, e)
        if ok(m):
          mm = match_rec(pa[1:], ex[1:])
          if ok(mm):
            return cons(m, mm)
      return ':nil'
    
    # 6. For a *-variable, we try prepending [:seq] to a recursive match of the tail
    # of pa to ex; if the recursion fails, we try an initial-element match, and if
    # successful, recurse on pa (unchanged) and the tail of ex.
    if s_var(p):
      mm = match_rec(pa[1:], ex)
      if ok(mm):
        return cons([':seq'], mm)
      else:
        m = match_rec(p, e)
        if ok(m):
          mm = match_rec(pa, ex[1:])
          if ok(mm):
            return cons(m + mm[0][1:], mm[1:])
      return ':nil'
    
    # 7. For a +-variable, we try an initial element match, and if successful,
    # recurse on pa and the tail of ex with the initial +-variable of pa replaced
    # by the corresponding *-variable.
    if p_var(p):
      m = match_rec(p, e)
      if ok(m):
        sv = s_variant_of_p_var(p)
        mm = match_rec(cons(sv, pa[1:]), ex[1:])
        if ok(mm):
          return cons(m + mm[0][1:], mm[1:])
      return ':nil'
    
    # This exception should never be reached, as the above conditions should be exhaustive.
    raise Exception(f'Unexpected: match_rec({pa}, {ex}) gave neither success nor failure')

  res = match_rec(pa, ex)
  return [] if res == ':nil' else res


def spec_function(x):
  """Check if `x` is a user-defined evaluable function, i.e., if it ends with '!'."""
  return isinstance(x, str) and x and x != '!' and x[-1] == '!'


def position_index(i):
  """Map a string denoting a position index to either an integer or list of integers (or return ``[]`` if not a position index)."""
  if (isinstance(i, int) or (isinstance(i, str) and i.isdigit())):
    return int(i)
  elif not check_position_index_syntax(i):
    return []
  else:
    return [int(c) for c in i.split('.')]


def check_position_index_syntax(i):
  """Check if `i` is a valid position index.
  
  A position index in tree transductions can take the following syntax:
    - 0, 1, 2, 3, ...,
      (equivalently, 0., 1., 2., 3., ..., but NOT 0.0, 1.0, 2.0, 3.0, ...)
    - or 1.1, 1.2, 1.3, ..., 2.1, 2.2, 2.3, ..., etc.,
      (equivalently 1.1., 1.2., 1.3., ..., 2.1., 2.2., 2.3., ...)
    - or 1.1.1, 1.1.2, ..., 1.2.1, 1.2.2, ..., 2.1.1, 2.1.2, ... etc.
      (equivalently 1.1.1., 1.1.2., ..., 1.2.1., 1.2.1., 1.2.2., ... )
  
  Since trailing 0 digits are not allowed (except for standalone 0), an input
  like '13.20' should be given as '13.20.'.
  """
  if (isinstance(i, int) or (isinstance(i, str) and i.isdigit())):
    return True
  if not i or not isinstance(i, str):
    return False
  else:
    if any([c.isalpha() for c in i]):
      return False
    i = i.replace('|', '')
    n = len(i)
    if n < 2:
      return False
    if not num_var(i[0]):
      return False
    ndots = 0
    prev_dot = False
    for c in i:
      if c == '.':
        ndots += 1
        if prev_dot:
          return False
        else:
          prev_dot = True
      elif not num_var(c):
        return False
      elif prev_dot and num_var(c) and int(c) == 0:
        return False
      else:
        prev_dot = False
    if ndots == 1 and num_var(i[-1]) and int(i[-1]) == 0:
      return False
  return True


def fill_template(template, match_result, preds={}):
  """Fill a template containing positional indices with constituents from a match result.
  
  Parameters
  ----------
  template : s-expr
    An S-expression containing:
      - Positional indicators such as 3, 3.2, 3.3.2, etc., where pieces of `match_result` are
        to be placed. E.g., here, the references are to the 3rd element of `match_result`,
        the 2nd element of the 3rd element of `match_result`, etc. The index 0 is special,
        as it refers to the (flattened) match result as a whole.
      - Evaluable predicates ending in '!' applied to some arguments, e.g., ``[lex-ulf!, v, 3.2]``,
        in which case the result of the predicate called on the given arguments will filled in
        place. Custom predicates must be defined in ``eta.util.tt.preds``, and their arguments must
        match the arguments provided in `template`.
  match_result : s-expr
    An S-expression containing sequence expressions such as ``[:seq, [a, b], c, [d, [f, g]]]``.
  preds : dict, optional
    A dict mapping predicate names to functions implementing those predicates.

  Returns
  -------
  s-expr
    The template filled in with "pieces" from match_result, as indicated by the position
    indices it contains. If a position index points to a sequence, i.e., ``[:seq, ...]``, the
    elements of the sequence are inserted into the result without the :seq wrapper.
  """
  def fill_template_rec(template, match_result):
    nonlocal preds

    if template == 0 or template == '0':
      return flatten_sequences(match_result)
    ii = position_index(template)
    if ii or ii == 0:
      return flatten_sequences(indexed_element_of(match_result, ii))
    if atom(template):
      return template
    if listp(template[0]):
      return cons(fill_template_rec(template[0], match_result), fill_template_rec(template[1:], match_result))
    ii = position_index(template[0])
    if ii or ii == 0:
      val = indexed_element_of(match_result, ii)
      if val and listp(val) and val[0] == ':seq':
        return flatten_sequences(val[1:]) + fill_template_rec(template[1:], match_result)
      else:
        return cons(flatten_sequences(val), fill_template_rec(template[1:], match_result))
    if spec_function(template[0]):
      fname = template[0][:-1]
      if fname in DEFAULT_PREDS:
        f = DEFAULT_PREDS[fname]
      elif fname in preds:
        f = preds[fname]
      else:
        raise Exception(f'Predicate {fname} does not exist')
      return f(*fill_template_rec(template[1:], match_result))
    
    return cons(template[0], fill_template_rec(template[1:], match_result))
  
  return fill_template_rec(template, match_result)


def apply_rules(rules, expr, feats={}, preds={},
                rule_order='slow-forward',
                shallow=False,
                max_n=1000):
  """Apply each rule (a pattern/template pair) within a list of rules to a given expression until convergence.

  Parameters
  ----------
  rules : list[tuple[s-expr, s-expr]]
    A list of tuples (<pattern>, <template>), where ``pattern`` is a pattern
    to match, and ``template`` is the template to use to replace the matched
    expression, potentially containing references to the matched sequences.
  expr : s-expr
    The expression to apply the rules to.
  feats : dict, optional
    A dict mapping a word w to a feature list x1, ..., xk, such that
    ``isa(w, xi)`` for each feature xi.
  preds : dict, optional
    A dict mapping predicate names to functions implementing those predicates.
  rule_order : str, default='slow-forward'
    The order to apply the rules; the value must be one of the following options:

      * slow-forward - apply each rule until that rule no longer applies,
        possibly repeating the entire sequence.
      * earliest-first - always apply the first rule in the list that
        is applicable, repeat until no rules are applicable (the rule
        list may be processed multiple times).
      * fast-forward - apply each rule at most once, in order, repeating
        the list until convergence.
    
  shallow : bool, default=False
    If given as True, only match the top-level expression. Otherwise, use the first
    match obtained in a recursive tree search of the expression.
  max_n : int, default=1000
    The limit on the maximum number of edits to make to the expression.

  Returns
  -------
  s-expr
    The modified expression after applying the rules.
  """
  if rule_order not in ['slow-forward', 'earliest-first', 'fast-forward']:
    rule_order = 'slow-forward'

  def apply_shallow(rule, expr):
    nonlocal feats, preds
    match_result = match(rule[0], expr, feats, preds)
    if match_result:
      return fill_template(rule[1], match_result, preds), True
    else:
      return expr, False
    
  def apply_deep(rule, expr):
    nonlocal feats, preds
    match_result = match(rule[0], expr, feats, preds)
    if match_result:
      return fill_template(rule[1], match_result, preds), True
    elif not expr or not isinstance(expr, list):
      return expr, False
    else:
      expr1 = []
      success = False
      for e in expr:
        if not success:
          e1, success = apply_deep(rule, e)
        else:
          e1 = e
        expr1.append(e1)
      return expr1, success
  
  apply_func = apply_shallow if shallow else apply_deep
  expr1 = expr
  converged = False
  prevs = [expr1]
  n = 0
  
  if rule_order == 'slow-forward':
    while not converged:
      converged = True
      for rule in rules:
        converged2 = False
        while not converged2 and n < max_n:
          converged2 = True
          expr1, success = apply_func(rule, expr1)
          if success:
            n += 1
            if expr1 not in prevs:
              converged = False
              converged2 = False
              prevs.append(expr1)

  elif rule_order in ['earliest-first', 'fast-forward']:
    while not converged:
      converged = True
      for rule in rules:
        expr1, success = apply_func(rule, expr1)
        if success:
          n += 1
          if expr1 not in prevs:
            converged = False
            prevs.append(expr1)
          if rule_order == 'earliest-first':
            break

  return expr1


def apply_rule(rule, expr, feats={}, preds={},
                shallow=False,
                max_n=1000):
  """Apply a rule (a pattern/template pair) to a given expression until convergence.

  Parameters
  ----------
  rule : tuple[s-expr, s-expr]
    A tuple (<pattern>, <template>), where ``pattern`` is a pattern
    to match, and ``template`` is the template to use to replace the matched
    expression, potentially containing references to the matched sequences.
  expr : s-expr
    The expression to apply the rule to.
  feats : dict, optional
    A dict mapping a word w to a feature list x1, ..., xk, such that
    ``isa(w, xi)`` for each feature xi.
  preds : dict, optional
    A dict mapping predicate names to functions implementing those predicates.
  shallow : bool, default=False
    If given as True, only match the top-level expression. Otherwise, use the first
    match obtained in a recursive tree search of the expression.
  max_n : int, default=1000
    The limit on the maximum number of edits to make to the expression.

  Returns
  -------
  s-expr
    The modified expression after applying the rule.
  """
  return apply_rules([rule], expr, feats=feats, preds=preds, shallow=shallow, max_n=max_n)
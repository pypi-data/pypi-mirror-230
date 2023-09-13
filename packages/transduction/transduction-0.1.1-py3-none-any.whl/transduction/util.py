"""List utilities."""

def listp(lst):
	"""Check whether an input is a list (including the empty list)."""
	return isinstance(lst, list)


def atom(lst):
	"""Check whether an input is an atom (either empty list or a non-list)."""
	return not lst or not listp(lst)


def expr(lst):
	return True


def cons(lst1, lst2):
	"""Insert a value to the front of a list or set.
	
	Parameters
	----------
	lst1 : object
		An object (possibly a sublist) to insert.
	lst2 : list[object], set[object], or object
		A list, set, or object to cons the given object to.
	
	Returns
	-------
	list[object] or set[object]
	"""
	if listp(lst2):
		return [lst1] + lst2
	elif isinstance(lst2, set):
		return {lst1} | lst2
	else:
		return [lst1, lst2]
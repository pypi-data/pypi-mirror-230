import re

def replaceall(str, replist):
	"""Make a list of replacements to a given string in sequence.
	
	Parameters
	----------
	str : str
		A string whose contents should be replaced.
	replist : list[tuple]
		A list of replacements to make. A replacement is a tuple of one of the following forms:
			- ``(old, new)``
			- ``(old, new, is_regex)``
		If is_regex is given as True for a tuple, the old and new values are interpreted as regex strings.
	
	Returns
	-------
	str
	"""
	for tup in replist:
		if len(tup) == 3:
			a, b, is_regex = tup
		else:
			a, b = tup
			is_regex = False
		if is_regex:
			str = re.sub(a, b, str)
		else:
			str = str.replace(a, b)
	return str


def indent(n):
	"""Indent a string some number of levels."""
	return "  "*(n-1)


def isquote(s):
	"""Check if a given input is a quoted expression."""
	return isinstance(s, str) and len(s) >= 2 and s[0] == '"' and s[-1] == '"'

def rec_replace(old, new, lst):
	"""Recursively replace some old value with a new value throughout a list."""
	if lst == old:
		return new

	new_lst = []
	for e in lst:
		if e == old:
			new_lst.append(new)
		elif type(e) == list:
			new_lst.append(rec_replace(old, new, e))
		else:
			new_lst.append(e)

	return new_lst


def rec_remove(target, lst):
	"""Recursively remove a given target from a list."""
	new_lst = []
	for e in lst:
		if e == target:
			continue
		elif type(e) == list:
			new_lst.append(rec_remove(target, e))
		else:
			new_lst.append(e)

	return new_lst


def escaped_symbol_p(s):
	"""Check if a given symbol is an "escaped" symbol, equivalent to vertical bars in LISP."""
	return isinstance(s, str) and len(s) >= 2 and s.count('|') == 2


def symbolp(s):
	"""Check if a given variable is a "symbol" (i.e., a string)."""
	return isinstance(s, str)


def listp(lst):
	"""Check whether an input is a list (including the empty list)."""
	return isinstance(lst, list)


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
	

def push(lst1, lst2):
	"""Insert a value to the end of a list or set.

	Parameters
	----------
	lst1 : object
		An object (possibly a sublist) to insert.
	lst2 : list[object], set[object], or object
		A list, set, or object to push the given object to.
	
	Returns
	-------
	list[object] or set[object]
	"""
	if listp(lst2):
		return lst2 + [lst1]
	elif isinstance(lst2, set):
		return lst2 | {lst1}
	else:
		return [lst2, lst1]
	

def atom(lst):
	"""Check whether an input is an atom (either empty list or a non-list)."""
	return not lst or not listp(lst)


def append(lst):
  """Append each sublist within lst together, creating a single combined list."""
  return [x for l in lst for x in l]


def flatten(lst):
	"""Recursively flatten a list, creating a single list with no sub-lists."""
	if not listp(lst):
		return [lst]
	else:
		return append([flatten(x) for x in lst])
	

def remove_duplicates(lst, order=False):
	"""Remove duplicate items in a list, preserving the initial order of `order` is given as True."""
	if order:
		visited = []
		lst1 = []
		for l in lst:
			if not l in visited:
				lst1.append(l)
				visited.append(l)
		return lst1
	else:
		return list(set(lst))
	

def remove_nil(lst):
	"""Remove any null values from a list."""
	return [x for x in lst if x]
	

def subst(a, b, lst):
	"""Recursively substitute b for a throughout a list."""
	def subst_rec(a, b, x):
		if x == b:
			return a
		elif atom(x):
			return x
		else:
			return [subst_rec(a, b, y) for y in x]
	return subst_rec(a, b, lst)


def substall(lst, replist):
	"""Given a set of replacements, make a substitution in a list for each replacement."""
	for (b, a) in replist:
		lst = subst(a, b, lst)
	return lst


def get_keyword_contents(lst, keys):
	"""Get the contents immediately following each keyword in `keys` from a list."""
	return [e2 for (e1, e2) in zip(lst, lst[1:]+[None]) if e1 in keys and e2]


def to_key(lst):
	"""Convert a list to a valid dict key consisting of only tuples and strings."""
	if lst is None:
		return None
	if atom(lst):
		return str(lst)
	else:
		return tuple([to_key(x) for x in lst])
	

def split_by_cond(lst, cndfn):
	"""Split a list by a given condition function.
	
	Parameters
	----------
	lst : list
	cndfn : function

	Returns
	-------
	filtered : list
		The input list with elements matching `cndfn` filtered out.
	matching : list
		A list of elements from the input list matching `cndfn`.
	"""
	filtered = [x for x in lst if not cndfn(x)]
	matching = [x for x in lst if cndfn(x)]
	return filtered, matching
	

def extract_category(lst, catfn, ignfn=None):
	"""Recurse through a (possibly nested) list and extract categories that satisfy a given function.
	
	Parameters
	----------
	lst : s-expr
	catfn : function
		A function used to match categories to be extracted.
	ignfn : function, optional
		If given, a function used to ignore matching subexpressions (i.e.,
		avoid recursing within them).
	
	Returns
	-------
	lst_new : s-expr
		The input list with matching subexpressions removed.
	categories : list[s-expr]
		A list of extracted matching subexpressions.
	"""
	def rec(lst):
		nonlocal catfn, ignfn

		if atom(lst):
			return lst, []
		
		if ignfn is not None and ignfn(lst):
			no_sent_ops = lst
			sent_ops = []
		else:
			no_sent_ops, sent_ops = split_by_cond(lst, catfn)
		
		recursed = [rec(x) for x in no_sent_ops]
		lst_new = [x[0] for x in recursed]
		categories = append(cons(sent_ops, [x[1] for x in recursed]))
		return lst_new, categories
	return rec(lst)


def rec_find(lst, x, test=lambda x,y: x==y):
	"""Return subexpressions in a tree that are the same as the given symbol.
	
	A different binary function can be provided using the `test` argument.
	"""
	_, categories = extract_category(lst, lambda y: test(x, y))
	return categories


def rec_find_if(lst, cndfn):
	"""Return subexpressions in a tree that satisfy `cndfn`."""
	_, categories = extract_category(lst, cndfn)
	return categories
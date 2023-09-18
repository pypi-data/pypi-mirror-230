"""Utilities for handling S-expression lists."""

from ulf2english.util import atom, symbolp, escaped_symbol_p, replaceall

def balanced_substr(s):
	"""Find a substring with a balanced number of parentheses."""
	count = 1
	for i in range(1, len(s)):
		c = s[i]

		if c == '(':
			count += 1
		if c == ')':
			count -= 1
		if count == 0:
			return s[:i+1]

	return None


def clean_s_expr(s_expr):
	"""Clean a string representation of an S-expression by removing newlines and standardizing whitespace."""
	s_expr = s_expr.replace('\n', '')
	s_expr = s_expr.replace('\t', '')
	s_expr = replaceall(s_expr,
						[(r"\| ([a-zA-Z0-9-_.']+)\|", r'|\1|', True),
						 (r"\|([a-zA-Z0-9-_.']+) \|", r'|\1|', True),
						 # For handling proper names with multiple words (up to 4)
						 (r"\|([a-zA-Z0-9-_.']+)[ ]?([a-zA-Z0-9-_.']+)?[ ]?([a-zA-Z0-9-_.']+)?[ ]?([a-zA-Z0-9-_.']+)?\|",
							r'|\1_\2_\3_\4|', True)])
	while '__' in s_expr:
		s_expr = s_expr.replace('__', '_')
	while '  ' in s_expr:
		s_expr = s_expr.replace('  ', ' ')
	return s_expr


def standardize_symbols(s_expr):
	"""Standardize the symbols within an S-expression by mapping to lowercase, unless enclosed in escape symbols."""
	def standardize_rec(e):
		if symbolp(e) and not escaped_symbol_p(e):
			return e.lower()
		elif symbolp(e):
			parts = e.split('|')
			before = parts[0].lower()
			escaped = parts[1]
			after = parts[2].lower()
			if '.' in escaped:
				word, suffix = escaped.split('.')
				if suffix and suffix[0] != '_':
					escaped = word
					suffix = suffix.strip('_')
					after = '.'+suffix.lower()+after
			escaped = escaped.strip('_').replace('_', ' ')
			return before+escaped+after
		else:
			return [standardize_rec(x) for x in e]
	return standardize_rec(s_expr)


def convert_quotes(s_expr):
	"""Convert any quoted word lists (i.e., single ' symbol followed by a list of symbols) to a single quoted string."""
	def convert_quotes_rec(e):
		if atom(e):
			return e
		elif len(e) == 1:
			return [convert_quotes_rec(e[0])]
		else:
			e1 = []
			for x1, x2 in zip([None]+e[:-1], e):
				if x1 == "'" and x2 and isinstance(x2, list) and all([isinstance(x, str) for x in x2]):
					e1.append('"'+' '.join(x2)+'"')
				elif x2 != "'":
					e1.append(x2)
			return [convert_quotes_rec(x) for x in e1]
	return convert_quotes_rec(s_expr)


def parse_s_expr(s_expr):
	"""Parse a string containing an S-expression (in LISP form) into a structured list.
	
	Parameters
	----------
	s_expr : str
		An S-expression in LISP form, e.g., ``(a (b c (d e)) '(f g h))``.
	
	Returns
	-------
	s-expr
		A structured S-expression, i.e., a recursively nested list structure with string "symbols" as atoms.
		e.g., ``['a', ['b', 'c', ['d', 'e']], "f g h"]``
	"""
	def parse_s_expr_rec(s_expr):
		s_expr = clean_s_expr(s_expr)

		if len(s_expr) == 0:
			return None

		if s_expr[0] != '(' or s_expr[-1] != ')':
			return s_expr

		items = []

		item_buf = []
		i = 1
		while i < len(s_expr):
			c = s_expr[i]

			if c == ' ':
				if len(item_buf) > 0:
					items.append(''.join(item_buf))
					item_buf = []
				i += 1
			elif c != '(':
				if c != ')':
					item_buf.append(c)
				i += 1
			else:
				if len(item_buf) > 0:
					items.append(''.join(item_buf))
					item_buf = []
				inner = balanced_substr(s_expr[i:])
				items.append(parse_s_expr_rec(inner))
				i += len(inner)

		if len(item_buf) > 0:
			items.append(''.join(item_buf))
			item_buf = []

		return items

	return standardize_symbols(convert_quotes(parse_s_expr_rec(s_expr)))
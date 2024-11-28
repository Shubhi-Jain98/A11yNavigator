"""
Tab (or Spaces) indentation style checker for flake8
"""

__version__ = "2.1.0"

import collections
import re
import tokenize

import flake8.checker
import flake8.processor
from flake8.processor import NEWLINE, count_parentheses


# List of keywords in Python as of Python 3.7.2rc1
# See: https://docs.python.org/3/reference/lexical_analysis.html#keywords (update as needed)
KEYWORDS = frozenset({
	'False', 'await', 'else', 'import', 'pass', 'None', 'break', 'except', 'in', 'raise',
	'True', 'class', 'finally', 'is', 'return', 'and', 'continue', 'for', 'lambda', 'try',
	'as', 'def', 'from', 'nonlocal', 'while', 'assert', 'del', 'global', 'not', 'with',
	'async', 'elif', 'if', 'or', 'yield'
})

# List of keywords that start a new definition (function or class)
KEYWORDS_DEFINITION = frozenset({'async', 'def', 'class'})

NEWLINE_CLOSE = NEWLINE | {tokenize.OP}


class Indent(collections.namedtuple("Indent", ("tabs", "spaces"))):
	"""
	Convience class representing the combined indentation of tabs and spaces with vector-style math
	"""
	def __bool__(self):
		return self.tabs != 0 or self.spaces != 0
	
	def __pos__(self):
		return self
	
	def __neg__(self):
		return Indent(-self.tabs, -self.spaces)
	
	def __add__(self, other):
		return Indent(self.tabs + other[0], self.spaces + other[1])
	
	def __sub__(self, other):
		return Indent(self.tabs - other[0], self.spaces - other[1])
	
	def __mul__(self, other):
		return Indent(self.tabs * other[0], self.spaces * other[1])
	
	def __div__(self, other):
		return Indent(self.tabs / other[0], self.spaces / other[1])

Indent.null = Indent(0, 0)


class FileChecker(flake8.checker.FileChecker):
	"""
	Blacklist some `pycodestyle` checks that our plugin will implement instead
	"""
	
	BLACKLIST = frozenset({
		# E101 indentation contains mixed spaces and tabs
		#  – Incorrectly reports cases of using tabs for indentation but spaces for alignment
		#    (We have our own checks for cases where the two are mixed, which is still an error.)
		"pycodestyle.tabs_or_spaces",
		
		# E121 continuation line under-indented for hanging indent
		# E122 continuation line missing indentation or outdented
		# E123 closing bracket does not match indentation of opening bracket’s line
		# E126 continuation line over-indented for hanging indent
		# E127 continuation line over-indented for visual indent
		# E128 continuation line under-indented for visual indent
		#  – We handle these ourselves: That's what this checker is about after all
		# E124 closing bracket does not match visual indentation
		# E125 continuation line with same indent as next logical line
		# E129 visually indented line with same indent as next logical line
		# E131 continuation line unaligned for hanging indent
		# E133 closing bracket is missing indentation
		#  – These aren't handled yet but cannot be disabled separately
		"pycodestyle.continued_indentation",
		
		# W191 indentation contains tabs
		#  – Not applicable since we love tabs 🙂️
		"pycodestyle.tabs_obsolete",
		
		# W291 trailing whitespace
		# W293 blank line contains whitespace
		#  – Implemented by `BlankLinesChecker` with more options and saner defaults
		"pycodestyle.trailing_whitespace",
	})
	
	def __init__(self, filename, checks, options):
		if not IndentationChecker.USE_PYCODESTYLE_INDENT:
			for checks_type in checks:
				checks[checks_type] = list(filter(
					lambda c: c["name"] not in self.BLACKLIST,
					checks[checks_type]
				))
		super().__init__(filename, checks, options)

def _code2text(code):
	return "ET{0} (flake8-tabs)".format(code)

def expand_indent(line):
	r"""Return the amount of indentation (patched function for `flake8`)
	
	Tabs are expanded to the next multiple of the current tab size.
	
	>>> expand_indent('    ')
	4
	>>> expand_indent('\t')
	4
	>>> expand_indent('   \t')
	4
	>>> expand_indent('    \t')
	8
	"""
	if "\t" not in line:
		return len(line) - len(line.lstrip())
	result = 0
	for char in line:
		if char == "\t":
			result  = result // IndentationChecker.TAB_WIDTH * IndentationChecker.TAB_WIDTH
			result += IndentationChecker.TAB_WIDTH
		elif char == " ":
			result += 1
		else:
			break
	return result


def patch_flake8():
	flake8.checker.FileChecker = FileChecker
	flake8.processor.expand_indent = expand_indent


class BlankLinesChecker:
	"""
	Checks indentation in blank lines to match the next line if there happens to be any
	"""
	name    = "flake8-tabs"
	version = __version__
	
	
	REGEXP = re.compile(r"([ \t\v]*).*?([ \t\v]*)([\r\x0C]*\n?)$")
	
	DEFAULT_MODE = "maybe"
	MODE = DEFAULT_MODE
	
	
	@classmethod
	def add_options(cls, option_manager):
		# Indentation style options
		MODE_CHOICES = ("maybe", "always", "never")
		option_manager.add_option(
			"--blank-lines-indent", type="choice", choices=MODE_CHOICES, metavar="MODE",
			default=cls.DEFAULT_MODE, parse_from_config=True,
			help=("Whether there should be, properly aligned, indentation in blank lines; "
			      "\"always\" forces this, \"never\" disallows this (Default: %default)")
		)
	
	@classmethod
	def parse_options(cls, option_manager, options, extra_args):
		cls.MODE = options.blank_lines_indent
	
	def __new__(cls, physical_line, lines, line_number):
		indent, trailing, crlf = cls.REGEXP.match(physical_line).groups()
		if len(physical_line) - len(crlf) < 1:  # Totally blank line
			if cls.MODE != "always":
				return  # Otherwise check whether the next non-blank line is also unindented
		elif len(indent) + len(crlf) == len(physical_line):
			if cls.MODE == "never":  # Cannot have indented blank line in this mode
				return (0, "WT293 (flake8-tabs) blank line contains whitespace")
		else:
			# Not a blank line with whitespace
			if len(trailing) > 0:
				return (
					len(physical_line) - len(trailing) - len(crlf),
					"WT291 (flake8-tabs) trailing whitespace"
				)
			return
		
		# Scan for next non-blank line
		expected_indent = ""
		for idx in range(line_number, len(lines)):
			line_indent, _, line_crlf = cls.REGEXP.match(lines[idx]).groups()
			if len(line_indent) + len(line_crlf) != len(lines[idx]):
				expected_indent = line_indent
				break
		
		# Compare the two indents
		if indent != expected_indent:
			return (0, "WT293 (flake8-tabs) blank line contains unaligned whitespace")
	
	def __init__(self, physical_line, lines, line_number):
		pass



class IndentationChecker:
	"""
	Checks indentation within braces with a “tabs for indentation, spaces for alignment” kind of
	mindset
	"""
	name    = "flake8-tabs"
	version = __version__
	
	# Tab width: Used when requiring further indentation after we already have alignment
	DEFAULT_TAB_WIDTH = 4
	TAB_WIDTH = DEFAULT_TAB_WIDTH
	
	DEFAULT_USE_FLAKE8_TABS        = False
	DEFAULT_USE_PYCODESTYLE_INDENT = None
	USE_FLAKE8_TABS        = DEFAULT_USE_FLAKE8_TABS
	USE_PYCODESTYLE_INDENT = DEFAULT_USE_PYCODESTYLE_INDENT
	
	# Indentation tabs: The number of tabs, when indenting, to require for the
	#                   first level of indentation of functions calls,
	#                   function/class definitions and other expressions
	DEFAULT_INDENT_TABS_CALL = 1
	DEFAULT_INDENT_TABS_DEF  = 2  # PEP-8 requires indentation to be destingishable
	DEFAULT_INDENT_TABS_EXPR = 1
	INDENT_TABS_CALL = DEFAULT_INDENT_TABS_CALL
	INDENT_TABS_DEF  = DEFAULT_INDENT_TABS_DEF
	INDENT_TABS_EXPR = DEFAULT_INDENT_TABS_EXPR
	
	# Continuation line style: Which indentation style to allow on continuation lines
	#  * “aligned” means that follow-up lines should be indented by the exact
	#    number of extra spaces required to align them if the previous line's
	#    final opening brace
	#  * “hanging” means that follow-up lines should be indented by a tab
	#  * “both” chooses the allowed indentation style based on whether the
	#    first lines contains any relevant values after the final opening brace
	DEFAULT_CONTINUATION_STYLE = "both"
	CONTINUATION_STYLE = DEFAULT_CONTINUATION_STYLE
	
	
	@classmethod
	def add_options(cls, option_manager):
		patch_flake8()
		
		# Patcher options
		option_manager.add_option(
			"--use-flake8-tabs", action="store_true",
			default=cls.DEFAULT_USE_FLAKE8_TABS, parse_from_config=True,
			help=("Use flake8-tabs instead for indentation checking? "
			      "Enabling this will disable PyCodeStyle's indentation checks "
			      "unless you override that behaviour; by default (if this "
			      "option is not used) only minimal checking will be performed")
		)
		option_manager.add_option(
			"--use-pycodestyle-indent", action="store_true",
			default=cls.DEFAULT_USE_PYCODESTYLE_INDENT, parse_from_config=True,
			help=("Force the use of PyCodeStyle's indentation checks even if "
			      "flake8-tabs is enabled")
		)
		
		# First-indentation tab number options
		option_manager.add_option(
			"--indent-tabs-call", type="int", metavar="TABS",
			default=cls.DEFAULT_INDENT_TABS_CALL, parse_from_config=True,
			help=("Number of tabs to indent on the first level of indentation within a function/"
			      "method call (Default: %default)")
		)
		option_manager.add_option(
			"--indent-tabs-def", type="int", metavar="TABS",
			default=cls.DEFAULT_INDENT_TABS_DEF, parse_from_config=True,
			help=("Number of tabs to indent on the first level of indentation within a class/"
			      "function definition (Default: %default)")
		)
		option_manager.add_option(
			"--indent-tabs-expr", type="int", metavar="TABS",
			default=cls.DEFAULT_INDENT_TABS_EXPR, parse_from_config=True,
			help=("Number of tabs to indent on the first level of indentation within an "
			      "expression (Default: %default)")
		)
		
		
		# More rigid style enforcing options
		CONTINUATION_STYLE_CHOICES = ("aligned", "hanging", "both")
		option_manager.add_option(
			"--continuation-style", type="choice", choices=CONTINUATION_STYLE_CHOICES,
			metavar="STYLE", default=cls.DEFAULT_CONTINUATION_STYLE, parse_from_config=True,
			help=("Which continuation line style to enforce; \"hanging\" means "
			      "that no values should be present after the final opening "
			      "brace and further lines should be indented; \"aligned\" "
			      "means that there should be values present after the final "
			      "opening brace and further lines should be aligned to match "
			      "the starting column of these values (Default: %default)")
		)
		
		# Prevent conflict with other plugins registering `--tab-width` as well
		for option in option_manager.options:
			if option.dest == "tab_width":
				return
		
		option_manager.add_option(
			"--tab-width", type="int", metavar="n",
			default=cls.DEFAULT_TAB_WIDTH, parse_from_config=True,
			help="Number of spaces per tab character for line length checking (Default: %default)",
		)
	
	@classmethod
	def parse_options(cls, option_manager, options, extra_args):
		if options.use_pycodestyle_indent is not cls.DEFAULT_USE_PYCODESTYLE_INDENT:
			cls.USE_PYCODESTYLE_INDENT = options.use_pycodestyle_indent
		else:
			cls.USE_PYCODESTYLE_INDENT = not options.use_flake8_tabs
		cls.USE_FLAKE8_TABS = options.use_flake8_tabs
		
		cls.INDENT_TABS_CALL = options.indent_tabs_call
		cls.INDENT_TABS_DEF  = options.indent_tabs_def
		cls.INDENT_TABS_EXPR = options.indent_tabs_expr
		
		cls.CONTINUATION_STYLE = options.continuation_style
		
		cls.TAB_WIDTH = options.tab_width
	
	
	@classmethod
	def _parse_line_indent(cls, line):
		"""
		Count number of tabs at start of line followed by number of spaces at start of line
		"""
		tabs   = 0
		spaces = 0
		expect_tab = True
		for char in line:
			if expect_tab and char == '\t':
				tabs += 1
			elif expect_tab and char == ' ':
				spaces += 1
				expect_tab = False
			elif not expect_tab and char == ' ':
				spaces += 1
			elif not expect_tab and char == '\t':
				raise ValueError("Mixed tabs and spaces in indentation")
			else:
				break
		return Indent(tabs, spaces)
	
	@classmethod
	def _group_tokens_by_physical_line(cls, tokens):
		idx_last = len(tokens) - 1
		current  = []
		for idx, token in enumerate(tokens):
			current.append(token)
			if idx >= idx_last or token.end[0] < tokens[idx + 1].start[0]:
				next_line = None
				if idx < idx_last:
					next_line = tokens[idx + 1].line
				yield tuple(current), next_line
				current.clear()
	
	def __init__(self, logical_line, indent_char, line_number, noqa, tokens):
		self.messages = []
		
		# We only care about non-empty non-noqa-marked lines
		if not self.USE_FLAKE8_TABS or len(tokens) < 1 or noqa:
			return
		
		# Detect which general category the given set of tokens belongs to
		tokens = list(tokens)
		
		# Assume first line to be correctly indented
		try:
			first_indent = current_indent = self._parse_line_indent(tokens[0].line)
		except ValueError:  # mixed tabs and spaces – report error and abort this logical line
			self.messages.append((
				tokens[0].start,
				"ET101 (flake8-tabs) indentation contains mixed spaces and tabs"
			))
			return
		
		# Category stack: Keeps track which indentation style we should expect at this level
		category_stack = ["expression"]
		next_category = "expression"
		
		# Identation stack: Keeps track of the indentation `(tabs, spaces)`
		#                   caused by each brace
		# Item 0 represents the base indentation we got above, item 1 represents
		# indentation gained because of continuation lines
		indent_stack = [current_indent, Indent.null]
		
		prev_braces_count = 0
		for token_set, next_line in self._group_tokens_by_physical_line(tokens):
			assert len(token_set) >= 1
			
			try:
				line_indent = self._parse_line_indent(token_set[0].line)
			except ValueError:  # mixed tabs and spaces – report error and abort this logical line
				self.messages.append((
					tokens[0].start,
					"ET101 (flake8-tabs) indentation contains mixed spaces and tabs"
				))
				return
			
			# Parse indentation of the following line (if any), in case we
			# really and truely cannot predict which indentation it should have
			# and therefor need to actually peak at what is actually there
			next_indent = Indent.null
			try:
				if next_line is not None:
					next_indent = self._parse_line_indent(next_line)
			except ValueError:
				pass
			
			# +-------------------------------------+ #
			# | Parse line indentation and category | #
			# +-------------------------------------+ #
			
			# Count parentheses, number of characters in inital keywords (such
			# as `assert`, `with`, …) and detect the category (definition,
			# function call or expression) that we're currently in
			keyword_indent = Indent.null
			keyword_at_start = True
			braces_count = prev_braces_count
			brace_offsets = []
			brace_at_end = False
			braces_closing_at_start = True
			braces_closed_indent_start = Indent.null
			braces_closed_indent_total = Indent.null
			for token in token_set:
				if token.type in NEWLINE or token.type == tokenize.COMMENT:
					continue
				
				brace_at_end = False
				
				if token.type == tokenize.OP:
					keyword_at_start = False
					
					last_braces_count = braces_count
					braces_count = count_parentheses(braces_count, token.string)
					if last_braces_count < braces_count:
						braces_closing_at_start = False
						
						# Opening parathese: Push latest expected category on stack
						category_stack.append(next_category)
						
						# Since this parenthesis has not caused any indent yet,
						# push dummy value
						indent_stack.append(Indent.null)
						
						# Record character offset of opened brace
						# Opened braces that are closed on the same line will be
						# poped again, telling us how many spaces to add should
						# we chose alignment
						brace_offsets.append(token.end[1] - line_indent.tabs - line_indent.spaces)
						
						# This will be overwritten if the last token in the line
						# wasn't an opening parenthese
						brace_at_end = True
					elif last_braces_count > braces_count:
						# Closing parenthese: Remove last category from stack
						category_stack.pop()
						
						if len(brace_offsets) > 0:
							brace_offsets.pop()
						
						indent_popped = indent_stack.pop()
						
						# Add up all the removed indentation thanks to closing
						# parenthesis (remember that most will be `(0, 0)`!)
						braces_closed_indent_total += indent_popped
						
						# Add up all the removed indentation that happened
						# before any other indentation to find the proper level
						# of outdenting
						if braces_closing_at_start:
							braces_closed_indent_start += indent_popped
					else:
						braces_closing_at_start = False
				elif token.type == tokenize.NAME:
					braces_closing_at_start = False
					
					# Count number of characters (including a following space)
					# of any keywords at the start of the line
					if keyword_at_start and token.string in KEYWORDS:
						keyword_indent += Indent(0, len(token.string) + 1)
					keyword_at_start = False
					
					if token.string in KEYWORDS_DEFINITION:
						# Definition keyword for class or function
						# (If it's not a definition it'd have be a syntax error.)
						next_category = "definition"
						continue
					elif token.string not in KEYWORDS and next_category != "definition":
						# Non-keyword name not preceeded by definition: Probably a function call
						next_category = "call"
						continue
					elif token.string not in KEYWORDS:
						continue
				elif token.type not in NEWLINE:
					braces_closing_at_start = False
				
				# Catch-all for cases other than the two above
				next_category = "expression"
			assert braces_count == len(category_stack) - 1
			category = category_stack[-1]
			
			# +----------------------------------------------+ #
			# | Determine expected indentation for next line | #
			# +----------------------------------------------+ #
			
			# Choose expected indentation style for the following lines based on
			# the innermost active category
			indent_tabs = self.INDENT_TABS_EXPR
			if category == "call":
				indent_tabs = self.INDENT_TABS_CALL
			elif category == "definition":
				indent_tabs = self.INDENT_TABS_DEF
			
			# Calculate new expected indentation
			# (both for this and the following lines)
			current_indent_delta = Indent.null
			if braces_count > prev_braces_count:
				if brace_at_end:  # Expect next line indented
					if self.CONTINUATION_STYLE == "aligned":
						self.messages.append((
							token_set[0].start,
							"{0} option continuation-style=aligned does not "
							"allow use of hanging indentation".format(
								_code2text(113)
							)
						))
					
					# Expect one extra level of indentation for each line that
					# left some braces open in the following lines, except for
					# the first level which has a configurable increase per type
					tabs = indent_tabs if prev_braces_count == 0 else 1
					
					# Do not increase number of tabs after having added spaces for any reason
					# (including lines that are indented with spaces entirely!)
					expand_tabs = False
					if current_indent.spaces - braces_closed_indent_total.spaces > 0:
						expand_tabs = True
					elif current_indent.tabs < 1 and braces_closed_indent_total.tabs < 1:
						# There were neither tabs nor spaces yet, meaning we're
						# no seeing our first indentation on a top-level scope,
						# so we “expect” the indentation style actually used on
						# the next line, erring on the side of tabs if the next
						# line wasn't indented either (which will then result in
						# an error)
						expand_tabs = next_indent.tabs < 1 and next_indent.spaces > 0
					
					if expand_tabs:
						current_indent_delta += (0, tabs * self.TAB_WIDTH)
					else:
						current_indent_delta += (tabs, 0)
				else:  # Expect next line aligned to innermost brace
					if self.CONTINUATION_STYLE == "hanging":
						self.messages.append((
							token_set[0].start,
							"{0} option continuation-style=hanging does not "
							"allow use of alignment as indentation".format(
								_code2text(113)
							)
						))
					
					current_indent_delta += (0, brace_offsets[-1] if len(brace_offsets) > 0 else 0)
			
			# +-----------------------------------------------+ #
			# | Compare found indentation with expected value | #
			# +-----------------------------------------------+ #
			
			# Update indent stack entry to attach the diff from above to the
			# last opened brace
			indent_stack[-1] = indent_stack[-1] + current_indent_delta
			
			# Apply indentation changes caused by closed braces
			current_indent_delta -= braces_closed_indent_total
			
			
			# Expect the closing braces that come before any content on the
			# this line to be on the new level already
			if braces_count < prev_braces_count:
				current_indent       -= braces_closed_indent_start
				current_indent_delta += braces_closed_indent_start
			
			# IF there are no open braces after the end of the current line,
			# expect the next line to be indent by the size of any leading
			# keyword (useful for `assert`, `with`, … – see the OK example file)
			if braces_count == 0 and keyword_indent:
				current_indent       -= indent_stack[1]
				current_indent_delta += keyword_indent
				indent_stack[1]       = keyword_indent
			
			# Compare settings on current line
			if line_indent != current_indent:
				# Find error code similar to `pycodestyle`
				code_text = _code2text(112)
				if line_indent == first_indent:
					code_text = _code2text(122)
				elif current_indent.spaces == line_indent.spaces == 0:
					if line_indent.tabs < current_indent.tabs:
						code_text = _code2text(121)
					else:
						code_text = _code2text(126)
				else:
					if line_indent.spaces > current_indent.spaces:
						code_text = _code2text(127)
					else:
						code_text = _code2text(128)
				
				# Generate and store error message
				if current_indent.spaces == line_indent.spaces:
					self.messages.append((
						token_set[0].start,
						"{0} unexpected number of tabs at start of {1} line "
						"(expected {2.tabs}, got {3.tabs})".format(
							code_text, category, current_indent, line_indent
						)
					))
				elif current_indent.tabs == line_indent.tabs:
					self.messages.append((
						token_set[0].start,
						"{0} unexpected number of spaces at start of {1} line "
						"(expected {2.spaces}, got {3.spaces})".format(
							code_text, category, current_indent, line_indent
						)
					))
				else:
					self.messages.append((
						token_set[0].start,
						"{0} unexpected number of tabs and spaces at start of {1} line "
						"(expected {2.tabs} tabs and {2.spaces} spaces, "
						"got {3.tabs} tabs and {3.spaces} spaces)".format(
							code_text, category, current_indent, line_indent,
						)
					))
			
			# +-----------------------+ #
			# | Prepare for next line | #
			# +-----------------------+ #
			
			# Apply deltas
			current_indent += current_indent_delta
			assert sum(indent_stack, Indent.null) == current_indent
			
			# Remember stuff for next iteration
			prev_braces_count = braces_count
		
		# All parentheses that were opened must have been closed again
		assert prev_braces_count == 0
	
	def __iter__(self):
		return iter(self.messages)

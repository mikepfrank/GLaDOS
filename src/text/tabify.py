
# tabify.py

# Code level 0

# Defines a function to automatically tabify a text string.  This is
# somewhat nontrivial since it involves keeping track of the current
# column, and understanding that it doesn't change when VT (vertical tab) is used..

def tabify(instr:str, tabwidth:int=8, startcol:int=0):

	"""Converts an ASCII string to a form where the maximum number of
		spaces have been replaced by tab characters, taking care to
		handle VT (vertical tab) and CR/LF characters appropriately.
		NOTE: We currently don't try to do anything intelligent here
		with BS (backspace) characters; i.e., they are just treated
		like normal printable characters. (This might be considered
		appropriate in GLaDOS since the display module does render
		them as printable glyphs. However, the AI might not see them
		that way. They might even be filtered out of its input.) We
		also don't try to do anything intelligent with form feed;
		teleprinter conventions may vary as to whether it returns to
		the leftmost column or not.

		One thing, however, that makes our job here more complicated
		is that we'd prefer to avoid changing the space immediately
		prior to the start of a word to a tab, because this will mess
		up the GPT tokenizer.

	"""

	column = startcol	# Start at specified column.

	outstr = ""


	# Note the following is an internal function. Consider making
	# it public so we can use it in the display module, if needed.
	def _nextstop(col:int):

		"""Returns the column of the next tab stop, in the context
			of the current tab width."""

		return (int(col/tabwidth)+1)*tabwidth
			# Explanation of expression: int(col/tabwidth) finds the
			# index of the tab stop that's at or behind our current
			# column, the +1 advances forward one tab stop, and then
			# the *tabwidth converts it back to a column number.


	# We use an index here instead of just 'for ch in instr' so that
	# we can look ahead at upcoming characters.

	# Loop over positions in the input string.
	inlen = len(instr)
	for i in range(inlen):

		# Extract the character at the current position.
		ch = instr[i]

			# Remember what column we were at before processing
			# this character.
		prevcol = column

		if ch=='\r' or ch=='\n':	# CR or LF?
			column = 0		# Reset column to far-left.

		elif ch=='\t':		# Horizontal TAB character?
			column = _nextstop(column)
				# Column advances forward to next tab stop.

		elif ch!='\v':		# Vertical tabs don't change the column.
			column += 1		# Normal characters advance column by 1.

		outstr += ch

		# If we're in the leftmost column, there's nothing special
		# we can do here, so just continue to the next input character.
		if column == 0:
			continue

		# If the present column isn't a multiple of the tab width,
		# then it isn't time yet to try to do something special,
		# so just continue.
		if (column % tabwidth) != 0:
			continue
		
		# OK, so, we are currently at a tab stop position. But, if we
		# just outputted a space, and the next input character after
		# the current one (looking ahead) is alphabetic, then changing
		# that last space to a tab risks screwing up the tokenizer, so
		# don't consider it; just continue.

		if i+1 < inlen-1 and ch==' ' and instr[i+1].isalpha():
			continue

		# Alright, so, we don't have to worry about the tokenizer
		# here, so, we can consider doing special stuff here. However,
		# if the last character we output wasn't a space or a tab,
		# there's nothing we can do here, so just continue.

		if ch!=' ' and ch!='\t':
			continue

		# Alright; now let's check and see what column we were at just
		# before processing the last character. If we were all the way
		# back at column-8, then we must have just output a tab that
		# went as far as possible already, and there's nothing more we
		# can do, so just continue.
		if prevcol == column-8:
			continue

		# By the time we get here, we finally have a solid candidate
		# for doing some real space-to-tab conversion.  A first case
		# to consider is, if the last two characters seen were both
		# spaces, then we can immediately replace them both with a
		# tab.

		# If the last two characters are two spaces,
		if len(outstr) >= 2 and outstr[-2:]=='  ':

			# Go ahead and turn those two spaces to a tab, and bump
			# back our idea of what the previous column was.

			outstr = outstr[:-2] + '\t'
			prevcol -= 1

		# So, when we get here, we know that the last character in
		# outstr is definitely a tab now, and the only question is how
		# many additional earlier spaces we want to absorb into
		# it. Let's just slurp them up iteratively.

		# While the previous column is after column-8, and the
		# second-to-last character is a space,
		while prevcol > column-8 and len(outstr) >= 2 and outstr[-2]==' ':

			# Nuke that space and bump back our idea of where we were
			# before this tab.
			outstr = outstr[:-2] + '\t'
			prevcol -= 1

		# By the time we get here, we've done all we can -- either
		# we've run out of spaces to absorb, or this tab has already
		# absorbed the maximum number of spaces. In either can, we
		# can't do any more special stuff, so just continue.

	#__/ End for i in positions in the input string.

	return outstr	# Return our accumulated output string.

	# We'll use this function for transforming markdown hyperlinks
	# and reserved characters to try to make sure they're formatted in a
	# way that doesn't cause the Telegram's markdown v2 parser to choke.

	def _local_replaceFunc(match):

		hyperLink = match.group(1)		# This is bound iff we matched a hyperlink.
		fullMatch = match.group(0)		# The entire part of the message being matched.

		if hyperLink:

			hlink_text	= match.group(2)	# The linked text inside the [...] part.
			url			= match.group(3)	# The link URL inside the (...) part.
			
			# In the []-delimited hyperlinked text, we want to make sure that
			# any of MarkdownV2's reserved characters that appears in that text
			# is escaped. We use negative lookbehind to match just the ones that
			# are not already escaped.

			hlink_text = re.sub(r'(?<!\\)([\[\]()>#+=|{}.!`-])',
								lambda m: '\\' + m.group(), hlink_text)
				# Note we even escape "`" here, because fixed-width text doesn't
				# render within hyperlink text in the iOS and Windows Telegram
				# clients anyway.

			# We don't bother transforming the URL; we wouldn't have matched it
			# anyway if everything that needed to be escaped in it hadn't been
			# escaped properly. (At least, that's what we're assuming here.)

			return f"[{hlink_text}]({url})"
				# Reassemble the hyperlink now that we've escaped the text part.

		else:
			return '\\' + fullMatch

#---------------------------------------------------------------


		# This code needs improvement.
		# Here, we really want a regex that matches any of several cases:
		#
		#  (1) A (more or less) properly-formatted hyperlink form.
		#		(1a) Inside the text field of which we can have item (4)'s or item (5)'s.
		#		(1b) Inside the url field of which we can have '\)' and '\\', but we fix bare '\'.
		#
		#  (2) A (more or less) properly-formatted ```...``` form.
		#		Inside of which we can have escaped "`" and escaped "\", but we fix bare "`" and bare "\".
		#
		#  (3) A (more or less) properly-formatted `...` form.
		#		Inside of which we can have escaped "`" and escaped "\", but we fix bare '\'.
		#
		#  (4) A properly-escaped reserved character.
		#
		#  (5) A non-properly-escaped reserved character.
		#
		#  (6) A normal character that isn't any of the above.


		#re.sub(r'( \[   \] \(   \) ) | (```(? \\` | \\\\  | [^`] | `[^`] | ``[^`] )*```) | ( ) | ( ) | ( )')

		escapedMsg = re.sub(r'(\[([^\]]*[^\\])\]\(([^\]]*[^\\])\))|(?<!\\)[\[\]()>#+=|{}.!-]', _local_replaceFunc, msgToSend)
			# Replaces well-formatted hyperlinks with themselves, but with escaped hyperlink text,,
			# and unescaped special characters with their backslash-escaped equivalents.

#----------------------------------------------------------------------

				## FOR SOME REASON THIS BLOCK IS CAUSING INFINITE LOOPS. COMMENTING OUT FOR NOW.
				## If it's just asking us to escape a character, then escape it and try again.
				#match = re.match(r"Can't parse entities: character '(.)' is reserved and must be escaped with the preceding '\\'", errmsg)
				#if match:
				#	char = match.group(1)
				#
				#	_logger.normal(f"\tBackslash-escaping '{char}' character in response to {user_name} in {chat_id}...")
				#
				#	# Replace occurrences of the reserved character in text with the escaped version
				#	text = text.replace(char, '\\' + char)
				#	continue


import math
import os
import sys
from ClassLexicon import *
from signatures import *

# from fsm import State, Transducer, get_graph



""""	 Signatures is a map: its keys are signatures. Its values are *sets* of stems. 
	 StemToWord is a map; its keys are stems.      Its values are *sets* of words.
	 StemToSig is a map; its keys are stems.       Its values are individual signatures.
	 WordToSig is a Map. its keys are words.       Its values are *lists* of signatures.
	 StemCounts is a map. Its keys are words. 	Its values are corpus counts of stems.
"""  # ---------------------------------------------------------------------------------------------------------------------------------------------#


def list_to_string(mylist):
	outstring = ""
	if mylist == None:
		return None
	sep = '-'
	for i in range(len(mylist)):
		if mylist[i] == None:
			outstring += "@"
		else:
			outstring += mylist[i]
		if i < len(mylist) - 1:
			outstring += sep
	# print outstring
	return outstring


# ------------------- New -----------------------------------------------------------------------------------
def makeFSM(morphology, Signatures, start, end):
	stateDict = dict()
	signumber = 0
	howmanywords = 3
	numberOfSignaturesToDisplay = 8
	SortedListOfSignatures = sorted(Signatures.items(), lambda x, y: cmp(len(x[1]), len(y[1])), reverse=True)
	for sig, stemset in SortedListOfSignatures:
		stemlist = list(stemset)
		stateDict[signumber] = State(sig)
		for i in range(howmanywords):
			if i == len(stemlist):
				break
			start[stemlist[i]] = stateDict[signumber]
		for affix in sig.split('-'):
			stateDict[signumber][affix] = end
		signumber += 1
		if signumber > numberOfSignaturesToDisplay:
			break
	get_graph(morphology).draw('morphology.png', prog='dot')


# ---------------------------------------------------------#
def decorateFilenameWithIteration(filename, outfolder, extension):
	# Check that logfilename does NOT contain a (.
	filenameLength = len(filename)
	filenames = os.listdir(outfolder)
	suffixes = list()
	maxvalue = 0
	for thisfilename in filenames:
		pieces = thisfilename.partition("(")
		if thisfilename[0:filenameLength] == filename:
			remainder = thisfilename[
						len(filename):]  # chop off the left-side of the thisfile's name, the part that is filename
			if thisfilename[-1 * len(extension):] == extension:
				remainder = remainder[:-1 * len(extension)]  # chop off the extension
				if len(remainder) > 0 and remainder[0] == "(" and remainder[-1] == ")":
					stringFileNumber = remainder[1:-1]
					if stringFileNumber > maxvalue:
						maxvalue = int(stringFileNumber)
	if maxvalue > 0:
		filename = outfolder + filename + "(" + str(maxvalue + 1) + ")" + extension
	else:
		filename = outfolder + filename + "(0).txt"
	return filename


# ---------------------------------------------------------#
def findSignatureInformationContent(signatures, signature, bitsPerLetter):
	stemSetPhonoInformation = 0
	stemSetOrderingInformation = 0
	affixPhonoInformation = 0
	affixOrderingInformation = 0
	letters = 0
	stemset = signatures[signature]
	for stem in stemset:
		stemlength = len(stem)
		letters += stemlength
		stemSetPhonoInformation += bitsPerLetter * stemlength
		stemSetOrderingInformation += math.log(stemlength * (stemlength - 1) / 2, 2)
	for affix in signature:
		affixlength = len(affix)
		letters += affixlength
		affixPhonoInformation += bitsPerLetter * len(affix)
		if affixlength > 1:
			affixOrderingInformation += math.log(affixlength * (affixlength - 1) / 2, 2)
		else:
			affixOrderingInformation = 0
	phonoInformation = int(stemSetPhonoInformation + affixPhonoInformation)
	orderingInformation = int(stemSetOrderingInformation + affixOrderingInformation)
	return (letters, phonoInformation, orderingInformation)


# ---------------------------------------------------------#
def makeWordListFromSignature(signature, stemset):
	wordlist = list()
	word = ""
	for stem in stemset:
		for affix in signature:
			if affix == "NULL":
				word = stem
			else:
				word = stem + affix
		wordlist.append(word)
	return wordlist


# ---------------------------------------------------------#
def FindSignature_LetterCountSavings(Signatures, sig):
	affixlettercount = 0
	stemlettercount = 0
	numberOfAffixes = len(sig)
	numberOfStems = len(Signatures[sig])
	for affix in sig:
		affixlettercount += len(affix) + 1
	for stem in Signatures[sig]:
		stemlettercount += len(stem) + 1
	lettercountsavings = affixlettercount * (numberOfStems - 1) + stemlettercount * (numberOfAffixes - 1)
	return lettercountsavings


# ---------------------------------------------------------#

def findWordListInformationContent(wordlist, bitsPerLetter):
	phonoInformation = 0
	orderingInformation = 0
	letters = 0
	for word  in wordlist:
		wordlength = len(word)
		letters += wordlength
		phonoInformation += bitsPerLetter * wordlength
		orderingInformation += wordlength * (wordlength - 1) / 2
	return (letters, phonoInformation, orderingInformation)


# ------------------- end of New -----------------------------------------------------------------------------------
# ---------------------------------------------------------#
def makesortedstring(string):
	letters = list(string)
	letters.sort()
	return letters


# ---------------------------------------------------------#
def formatPRule(pair):
	piece1 = pair[0]
	piece2 = pair[1]
	if len(piece1) == 0 and len(piece2) == 0:
		outstring = "[ @ ]"
		return outstring
	if len(piece1) == 0:
		piece1 = "@"
	if len(piece2) == 0:
		piece2 = "@"
	outstring = "[" + piece1 + " = " + piece2 + "]"
	return outstring


# ---------------------------------------------------------#
def maximalcommonprefix(a, b):
	howfar = len(a)
	if len(b) < howfar:
		howfar = len(b)
	for i in range(howfar):
		if not a[i] == b[i]:
			return a[:i]
	return a[:howfar]


# ---------------------------------------------------------#
def listToSignature(thislist):
	for i in range(len(thislist)):
		if i == 0:
			signature = thislist[0]
		else:
			signature += "-" + thislist[i]
	return signature


# ---------------------------------------------------------#
def maximalcommonsuffix(a, b):
	alen = len(a)
	blen = len(b)
	howfar = alen
	if len(b) < howfar:
		howfar = len(b)
	for i in range(0, howfar, 1):
		if not a[alen - i - 1] == b[blen - i - 1]:
			startingpoint = alen - i
			return a[startingpoint:]
	return a[(alen - howfar):]


# ---------------------------------------------------------#
def DeltaLeft(a,
			  b):  # Returns a pair of strings, consisting of prefixes of a and b, up to the maximal common suffix that a and b share.
	howfar = len(a)
	if len(b) < howfar:
		howfar = len(b)
	# if a == "s" and b == "rs":
	# print "\n 1 DeltaLeft" ,a,"/", b, "howfar: ",  howfar
	i = 1
	while i < howfar + 1:
		# print "2 i = ", i, a[len(a) - i], b[len(b) - i]
		if not a[len(a) - i] == b[len(b) - i]:
			# print "disagreement at ", i
			a_piece = len(a) - i + 1
			b_piece = len(b) - i + 1
			# print "3. Will return ",a[:a_piece], ",", b[:b_piece]
			return (a[:a_piece], b[:b_piece])
		i += 1
	# print "4 no difference during string checkover shorter string, i is ",i
	a_piece = len(a) - i + 1
	b_piece = len(b) - i + 1
	# if a == "s" and b == "rs":
	# print "5. Will return ", a[:a_piece],"/",  b[:b_piece]
	return (a[:a_piece], b[:b_piece])


# ---------------------------------------------------------#
def DeltaRight(a,
			   b):  # Returns a pair of strings, consisting of the suffixes of each string following any maximal common prefix that may exist.
	howfar = len(a)
	if len(b) < howfar:
		howfar = len(b)
	for i in range(howfar):
		if not a[i] == b[i]:
			return (a[i:], b[i:])
	return (a[howfar:], b[howfar:])


# ---------------------------------------------------------#
def DifferenceOfDifference((X1, X2), (Y1, Y2), DiffType):
	if DiffType == "suffixal":
		# print
		lowerdifference = DeltaLeft(X2, Y2)
		# print "*2.1", X2,":",Y2, ":",lowerdifference
		upperdifference = DeltaLeft(X1, Y1)
		# print "*2.2", X1,":",Y1,":", upperdifference
		# print
		r1 = upperdifference
		r2 = lowerdifference
		return (r1, r2)

	if DiffType == "prefixal":
		# print
		lowerdifference = DeltaRight(X2, Y2)
		# print "*2.1", X2,":",Y2, ":",lowerdifference
		upperdifference = DeltaRight(X1, Y1)
		# print "*2.2", X1,":",Y1,":", upperdifference
		# print
		r1 = upperdifference
		r2 = lowerdifference
		return (r1, r2)

	if DiffType == "unordered":
		x1 = list(X1)
		x2 = list(X2)
		y1 = list(Y1)
		y2 = list(Y2)
		r1 = []
		r2 = []
		x1.extend(y2)  # add y2 to x1
		del y2[:]
		x1.sort()

		x2.extend(y1)
		del y1[:]
		x2.sort()

		while len(x1) > 0:  # remove anything in y1 from x1
			if len(x2) == 0:
				r1.extend(x1)
				del x1[:]
				break
			else:
				if x1[0] < x2[0]:
					r1.append(x1.pop(0))
				elif x1[0] == x2[0]:
					x1.pop(0)
					x2.pop(0)
				else:
					r2.append(x2.pop(0))
		if len(x2) > 0:
			r2.extend(x2)
			del x2[:]

		r1 = ''.join(r1)
		r2 = ''.join(r2)
	return (r1, r2)


# ---------------------------------------------------------#

def makesignature(a):
	delimiter = '.'
	sig = ""
	for i in range(len(a) - 1):
		if len(a[i]) == 0:
			sig += "NULL"
		else:
			sig += a[i]
		sig += delimiter
	sig += a[len(a) - 1]
	# print "sig", sig
	return sig


# ---------------------------------------------------------#
def makesignaturefrom2words(a, b):
	stemlength = 0
	howfar = len(a)
	if len(b) < howfar:
		howfar = len(b)
	for i in range(0, howfar, -1):
		if a[i] == b[i]:
			stemlength = i + 1
		else:
			break;
	affix1 = a[:stemlength]
	affix2 = b[:stemlength]
	if len(affix1) == 0:
		affix1 = "NULL"
	if len(affix2) == 0:
		affix2 = "NULL"
	return (affix1, affix2)


# ---------------------------------------------------------#
def stringdiff(instring1, instring2):
	if instring1 == 'NULL':
		instring1 = ''
	if instring2 == 'NULL':
		instring2 = ''
	# ---------------------------#
	"""
	# this function can look for suffixal differences, prefixal differences, or unordered string differences
	"""
	# ---------------------------#
	DiffType = "suffixal"

	if DiffType == "suffixal":
		# this returns a pair of lists, which give the differences of the ends of instring1 and instring2
		positive, negative = DeltaRight(instring1, instring2)
		# print "stringdiff: ", instring1,':', instring2,':', positive,':', negative
		return (positive, negative)
	elif DiffType == "unordered":
		string1 = makesortedstring(instring1)
		# print string1
		string2 = makesortedstring(instring2)
		i = 0
		j = 0
		del positive[:]
		del negative[:]
		while (True):
			if (i < len(string1) and j < len(string2)):
				if (string1[i] == string2[j]):
					i = i + 1
					j = j + 1
				elif (string1[i] < string2[j]):
					positive.append(string1[i])
					i = i + 1
				else:
					negative.append(string2[j])
					j = j + 1
			elif i == len(string1) and j == len(string2):
				for k2 in range(j, len(string2)):
					negative.append(string2[k2])
				for k1 in range(i, len(string1)):
					positive.append(string1[k1])
				break
			elif (i >= len(string1)):
				for k2 in range(j, len(string2)):
					negative.append(string2[k2])
				break
			elif (j >= len(string2)):
				for k1 in range(i, len(string1)):
					positive.append(string1[k1])
				break
	positive = ''.join(positive)
	negative = ''.join(negative)
	return (positive, negative)


# ---------------------------------------------------------------------------------------------------------------------------------------------#
class intrasignaturetable:
	def setsignature(self, sig):
		self.affixes = sig.split('-')
		self.affixlabels = {}  # use this if we care deeply about the spelling of the morphemes
		for affix in self.affixes:
			self.affixlabels[affix] = affix
		# if affix=='NULL':
		#	affix = ''
		self.indexed_affixlabels = []  # use this if we have entered the elements of the signature in a particular and significant order, an order which we wish to use to compare against another signature e.g.
		for m in range(len(self.affixes)):
			self.indexed_affixlabels.append(affix)
		self.differences = {}  #
		self.indexed_differences = {}
		positive = []
		negative = []

		for m in range(len(self.affixes)):
			affix1 = self.affixes[m]
			for n in range(len(self.affixes)):
				affix2 = self.affixes[n]
				(positive, negative) = stringdiff(affix1, affix2)
				self.differences[(affix1, affix2)] = (positive, negative)
				self.indexed_differences[(m, n)] = (positive, negative)

	def compress(self):
		# print "sig", self.affixes, self.differences
		pairInventory = {}
		costPerLetter = 5
		costForNull = 1
		TotalCost = 0
		# print
		for pair in self.differences:
			(positive, negative) = self.differences[pair]
			pairString = ''.join(positive) + ':' + ''.join(negative)
			# print "pairString", pairString
			if not pairString in pairInventory:
				pairInventory[pairString] = 1
			# print "new pair: ", pairString, len(positive), len(negative)
			else:
				pairInventory[pairString] += 1
		for pair in pairInventory:
			# print pair
			pieces = pair.split(':')
			affix1 = pieces[0]
			affix2 = pieces[1]
			if len(affix1) == 0 and len(affix2) == 0:
				costA = 0
				costB = 0
			# print "both null"
			else:
				if len(affix1) == 0:
					costA = costForNull
				else:
					costA = len(affix1) * costPerLetter
				if len(affix2) == 0:
					costB = costForNull
				else:
					costB = len(affix2) * costPerLetter
				TotalCost += (costA + costB) + (pairInventory[pair] - 1)  # we pay the "full price" for the first pair,
				# and each additional occurrence costs just one bit.
				# print costA, costB

				# print TotalCost
		# print TotalCost
		return (TotalCost, pairInventory)

	def display(self):
		positive = []
		negative = []

	# print 'making table'
	# print '\t',
	# for affix in self.affixes:
	#	print affix, '\t',
	# print

	# for affix1 in self.affixes:
	#	print affix1, ':','\t',
	#	for affix2 in self.affixes:
	#		print self.differences[(affix1, affix2)][0],':',self.differences[(affix1, affix2)][1],
	#	print
	def changeAffixLabel(self, before, after):
		for n in range(len(self.affixes)):
			if self.affixes[n] == before:
				self.affixlabels[before] = after
				return
		return

	def changeIndexedAffixLabel(self, index, after):
		self.indexed_affixlabels[index] = after

	def displaytofile(self, outfile):
		positive = []
		negative = []

		for affix in self.affixes:
			print >> outfile, '%18s' % self.affixlabels[affix],
		print >> outfile

		for affix1 in self.affixes:
			print >> outfile, '%10s' % self.affixlabels[affix1],
			for affix2 in self.affixes:
				# print "display to file, suffixes", affix1, affix2
				item = self.differences[(affix1, affix2)]
				print >> outfile, '[%4s]:[%-4s]    ' % (item[0], item[1]),
			print >> outfile
		TotalCost, pairInventory = self.compress()
		print >> outfile, "Compressed form: ", TotalCost
		return TotalCost

	def displaytolist(self, outlist):
		positive = []
		negative = []
		outlist = []
		line = "@"  # makes empty box in table
		for affix in self.affixes:
			line = line + "\t" + self.affixlabels[affix]
		outlist.append(line)
		for affix1 in self.affixes:
			line = self.affixlabels[affix1]
			for affix2 in self.affixes:
				# print "display to file, suffixes", affix1, affix2
				item = self.differences[(affix1, affix2)]
				part1 = item[0]
				part2 = item[1]
				if len(part1) == 0 and len(part2) == 0:
					line = line + " $NULL$"
				else:
					if len(part1) == 0:
						part1 = "NULL"
					if len(part2) == 0:
						part2 = "NULL"
					line = line + " $\\frac{" + part1 + "}{" + part2 + "}$"
			outlist.append(line)
		return outlist

	def displaytolist_aligned_latex(self, outlist):
		positive = []
		negative = []
		outlist = []
		affix1 = ""
		line = "@"  # makes empty box in table
		for n in range(len(self.affixes)):
			line = line + "\t" + self.indexed_affixlabels[n]
		outlist.append(line)
		for n in range(len(self.affixes)):
			affix1 = self.affixes[n]
			line = self.indexed_affixlabels[n]
			for m in range(len(self.affixes)):
				affix2 = self.affixes[m]
				item = self.indexed_differences[(n, m)]
				part1 = item[0]
				part2 = item[1]
				if len(part1) == 0 and len(part2) == 0:
					line = line + " $NULL$"
				else:
					if len(part1) == 0:
						part1 = "NULL"
					if len(part2) == 0:
						part2 = "NULL"
					line = line + " $\\frac{" + part1 + "}{" + part2 + "}$"
			outlist.append(line)
		return outlist

	def displaytolist_aligned(self, outfile):
		positive = []
		negative = []
		outlist = []
		colwidth = 30
		# outputtemplate = "%25s"
		# outputtemplate2 = "    [%5s %5s]    "
		# outputtemplate3 = "%5s]"

		print >> outfile, "".center(15),
		for n in range(len(self.affixes)):
			affix1 = self.affixes[n]
			# print >>outfile,  '%25s' %self.indexed_affixlabels[n],
			print >> outfile, self.indexed_affixlabels[n].ljust(30),
		print >> outfile
		for n in range(len(self.affixes)):
			affix1 = self.affixes[n]
			# print >>outfile, '%15s' %self.indexed_affixlabels[n],
			print >> outfile, self.indexed_affixlabels[n].ljust(15),
			for m in range(len(self.affixes)):
				affix2 = self.affixes[m]
				item = self.indexed_differences[(n, m)]
				part1 = item[0]
				part2 = item[1]
				if len(part1[0]) == 0 and len(part1[0]) == 0 and len(part2[0]) == 0 and len(part2[1]) == 0:
					#	#print >>outfile, "[    NULL   ]    ",
					print >> outfile, "[ @ ]".ljust(colwidth),
				else:
					outstring1 = formatPRule(part1)
					outstring2 = formatPRule(part2)
					# print >>outfile, outputtemplate2 %(outstring1, outstring2,)
					print >> outfile, outstring1, ":", outstring2.ljust(15), "".ljust(colwidth - 19 - len(outstring1)),
					# print >>outfile, outputtemplate3 %outstring, # '[%4s]:[%-4s]    '%(firstpiece,secondpiece) ,
			print >> outfile

		return

	def minus(self, other, DiffType):
		counterpart = {}
		(alignedAffixList1, alignedAffixList2) = FindBestAlignment(self.affixes, other.affixes)
		for i in range(len(alignedAffixList1)):
			counterpart[alignedAffixList1[i]] = alignedAffixList2[i]
		for index1 in range(len(alignedAffixList1)):
			for index2 in range(len(alignedAffixList2)):
				thispiece1 = alignedAffixList1[index1]
				thispiece2 = alignedAffixList1[index2]
				otherpiece1 = alignedAffixList2[index1]
				otherpiece2 = alignedAffixList2[index2]
				(thispositive, thisnegative) = self.differences[(thispiece1, thispiece2)]
				(otherpositive, othernegative) = other.differences[(otherpiece1, otherpiece2)]
				self.differences[(thispiece1, thispiece2)] = DifferenceOfDifference((thispositive, thisnegative), (otherpositive, othernegative), DiffType)

		# get rid of rows corresponding to unmatched affixes
		affixlistcopy = list(self.affixes)
		for affix1 in affixlistcopy:
			if not affix1 in alignedAffixList1:
				for affix2 in other.affixes:
					if (affix1, affix2) in self.differences:
						del self.differences[(affix1, affix2)]
				self.affixes.remove(affix1)
		for affix in self.affixes:
			self.changeAffixLabel(affix, str(affix + ":" + counterpart[affix]))
		return

	def minus_aligned(self, other, DiffType):
		for index1 in range(len(self.affixes)):
			for index2 in range(len(other.affixes)):
				thispiece1 = self.affixes[index1]
				thispiece2 = self.affixes[index2]
				otherpiece1 = other.affixes[index1]
				otherpiece2 = other.affixes[index2]
				(thispositive, thisnegative) = self.indexed_differences[(index1, index2)]
				(otherpositive, othernegative) = other.indexed_differences[(index1, index2)]
				self.indexed_differences[(index1, index2)] = DifferenceOfDifference((thispositive, thisnegative),
																					(otherpositive, othernegative),
																					DiffType)
				# put this back in: taken out for unicode, i don't know why
		for n in range(len(self.affixes)):
			self.changeIndexedAffixLabel(n, str(self.affixes[n] + ":" + other.affixes[n]))

		return


# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

# ---------------------------------------------------------#
# def Expansion(sig,stem):
#	wordset = set()
#	affixlist = sig.split('-')
#	for affix in affixlist:
#		if affix == 'NULL':
#			affix = ''
#		wordset.add(stem + affix)
#	return wordset
# ---------------------------------------------------------#
def makesignaturefrom2words_suffixes(a, b):
	stemlength = 0
	howfar = len(a)
	if len(b) < howfar:
		howfar = len(b)
	for i in range(howfar):
		if a[i] == b[i]:
			stemlength = i + 1
		else:
			break;
	affix1 = a[stemlength:]
	affix2 = b[stemlength:]
	if len(affix1) == 0:
		affix1 = "NULL"
	if len(affix2) == 0:
		affix2 = "NULL"
	return (affix1, affix2)


# ---------------------------------------------------------#
def sortfunc(x, y):
	return cmp(x[1], y[1])


# ---------------------------------------------------------#
def sortfunc1(x, y):
	return cmp(x[1], len(y[1]))


# ---------------------------------------------------------#
def subsignature(sig1, sig2):
	sigset1 = set(sig1.split('-'))
	sigset2 = set(sig2.split('-'))
	if sigset1 <= sigset2:  # subset
		return True
	return False


# ---------------------------------------------------------#
def RemoveNULL(list1):
	for item in list1:
		if item == "NULL":
			item = ""
	return list1


# ---------------------------------------------------------#
def StringDifference(str1, str2):
	if str1 == "NULL":
		str1 = ""
	if str2 == "NULL":
		str2 = ""
	list1 = list(str1)
	list2 = list(str2)
	list1.sort()
	list2.sort()
	m = 0
	n = 0
	overlap = 0
	difference = 0
	while (True):
		if m == len(str1) and n == len(str2):
			return (overlap, difference)
		if m == len(str1):
			difference += len(str2) - n
			return (overlap, difference)
		if n == len(str2):
			difference += len(str1) - m
			return (overlap, difference)

		if list1[m] == list2[n]:
			overlap += 1
			m += 1
			n += 1
		elif list1[m] < list2[n]:
			m += 1
			difference += 1
		elif list2[n] < list1[m]:
			n += 1
			difference += 1


# ----------------------------------------------------------------------------------------------------------------------------#
def SignatureDifference(sig1, sig2,outfile):  # this finds the best alignments between affixes of a signature, and also gives a measure of the similarity.
	list1 = list(sig1.split('-'))
	list1.sort()
	list2 = list(sig2.split('-'))
	list2.sort()
	reversedFlag = False
	if (len(list1) > len(list2)):
		temp = list1
		list1 = list2
		list2 = temp  # now list2 is the longer one, if they differ in lengthpart1[0], part1[1
		reversedFlag = True
	differences = {}
	list3 = []
	Alignments = []
	AlignedList1 = []
	AlignedList2 = []

	print >> outfile, "---------------------------------------\n", sig1, sig2
	print >> outfile, "---------------------------------------\n"
	for m in list1:
		differences[m] = {}
		# print >>outfile, '%8s ' % m, ":",
		for n in list2:
			o, d = StringDifference(m, n)
			differences[m][n] = o - d
			# print >>outfile, '%2s %2d;' % (n, o-d),
			# print >>outfile

	GoodAlignmentCount = 0
	TotalScore = 0
	for loopno in range(len(list1)):
		# print >>outfile, "-----------------------------\n"
		# print >>outfile, "loop no: ", loopno
		# for m in differences.keys():
		# print >>outfile, '%8s : ' % (m),
		# for n in differences[m].keys():
		# print >>outfile, '%2s %2d;' % (n, differences[m][n]),
		# print >>outfile
		# print >>outfile

		list3 = []
		for m in differences.keys():
			for n in differences[m].keys():
				list3.append(differences[m][n])
		list3.sort(reverse=True)

		bestvalue = list3[0]
		if bestvalue >= 0:
			GoodAlignmentCount += 1
		breakflag = False
		for m in differences.keys():
			for n in differences[m].keys():
				if differences[m][n] == bestvalue:
					winner = (m, n)
					# print >>outfile, "winner:", m, n, "closeness: ", bestvalue
					breakflag = True
					break
			if breakflag:
				break;
		AlignedList1.append(m)
		AlignedList2.append(n)

		Alignments.append((m, n, bestvalue))
		TotalScore += bestvalue
		del differences[winner[0]]
		for p in differences.keys():
			del differences[p][winner[1]]
	# print >>outfile, "Final affix alignments: ", sig1, sig2
	# for item in Alignments:
	#	print >>outfile, "\t%7s %7s %7d" % ( item[0], item[1], item[2] )
	# For scoring: we count a pairing as OK if its alignment is non-negative, and we give extra credit if there are more than 2 pairings
	if GoodAlignmentCount > 2:
		TotalScore += GoodAlignmentCount - 2
	if reversedFlag:
		return (AlignedList2, AlignedList1)
	return (TotalScore, AlignedList1, AlignedList2)


# ----------------------------------------------------------------------------------------------------------------------------#
def FindBestAlignment(list1, list2):  # this is very similar to SignatureDifference...
	AlignedList1 = []
	AlignedList2 = []
	reversedFlag = False
	if (len(list1) > len(list2)):
		temp = list1
		list1 = list2
		list2 = temp  # now list2 is the longer one, if they differ in length
		reversedFlag = True
	differences = {}
	list3 = []
	Alignments = []
	# print >>outfile,  "---------------------------------------\n"
	# print >>outfile, "---------------------------------------\n",list1, list2, "** Find Best Alignment **\n"
	for m in list1:
		differences[m] = {}
		for n in list2:
			o, d = StringDifference(m, n)
			differences[m][n] = o - d

	GoodAlignmentCount = 0
	TotalScore = 0
	for loopno in range(len(list1)):
		list3 = []
		for m in differences.keys():
			for n in differences[m].keys():
				list3.append(differences[m][n])
		list3.sort(reverse=True)

		bestvalue = list3[0]
		if bestvalue >= 0:
			GoodAlignmentCount += 1
		breakflag = False
		for m in differences.keys():
			for n in differences[m].keys():
				if differences[m][n] == bestvalue:
					winner = (m, n)
					# print >>outfile, "winner: %8s %8s closeness: %2d" %( m, n, bestvalue)
					breakflag = True
					break
			if breakflag:
				break;
		AlignedList1.append(m)
		AlignedList2.append(n)
		del differences[winner[0]]
		for p in differences.keys():
			del differences[p][winner[1]]

	if reversedFlag:
		return (AlignedList2, AlignedList1)
	return (AlignedList1, AlignedList2)


# ----------------------------------------------------------------------------------------------------------------------------#
def Sig1ExtendsSig2(sig1, sig2, outfile):  # for suffix signatures
	MaxLengthOfDifference = 2
	list1 = list(sig1 )
	list2 = list(sig2 )
	#print >>outfile, "B -------------------", sig1, sig2
	if len(list1) != len(list2):
		#print >>outfile, "C Different lengths"
		return (None, None, None)
	if sig1 == sig2:
		#print >>outfile, "E same signature" 
		return (None,None,None)
	length = len(list1)
	ThisExtendsThat = dict()
	for suffixno1 in range(length):  # we make an array of what suffix might possibly extend what suffix
		suffix1 = list1[suffixno1]
		ThisExtendsThat[suffixno1] = dict()
		if suffix1 == "NULL":
			suffix1_length = 0
		else:
			suffix1_length = len(suffix1)

		for suffixno2 in range(length):
			suffix2 = list2[suffixno2]
			if suffix2 == "NULL":
				suffix2_length = 0
			else:
				suffix2_length = len(suffix2) 
			if suffix1 == suffix2:
				ThisExtendsThat[suffixno1][suffixno2] = 1
			elif suffix2_length == 0 and suffix1_length <= MaxLengthOfDifference:
				ThisExtendsThat[suffixno1][suffixno2] = 1
			elif suffix1[-1 * suffix2_length:] == suffix2 and abs(suffix1_length - suffix2_length) <= MaxLengthOfDifference:  
				ThisExtendsThat[suffixno1][suffixno2] = 1
				#print suffix1,suffix2, suffix1_length, suffix2_length, suffix1_length - suffix2_length
			else:
				ThisExtendsThat[suffixno1][suffixno2] = 0
	for pos in range(length):  # now we try to find a good alignment
		thisrowcount = sum(ThisExtendsThat[pos].values())
		if thisrowcount == 1:  # this means only one alignment is permitted, so this is helpful to know.
			for pos2 in range(length):
				if ThisExtendsThat[pos][pos2] == 1:
					that_pos = pos2
					break
			for pos3 in range(length):
				if pos3 != pos:
					ThisExtendsThat[pos3][that_pos] = 0

	# at this point, if any row is empty, then alignment is impossible. If any row has two 1's, then alignment is still ambiguous, but this is very unlikely.
	#for pos1 in range(length):
	#	for pos2 in range(length):
	#		print >>outfile, ThisExtendsThat[pos1][pos2],
	#	print >>outfile

	AlignPossibleFlag = True
	AlignedList1 = list()
	AlignedList2 = list()
	Differences = list()
	for pos in range(length):
		rowcount = sum(ThisExtendsThat[pos].values())
		if rowcount == 0:
			AlignmentPossibleFlag = False
			#print >>outfile, "G Alignment impossible"
			break
		if rowcount == 1:
			AlignedList1.append(list1[pos])
			for pos2 in range(length):
				if ThisExtendsThat[pos][pos2] == 1:
					AlignedList2.append(list2[pos2])
					if list2[pos2] == "NULL":
						sig2_item_length = 0
					else:
						sig2_item_length = len(list2[pos2])
					lengthofdifference = len(list1[pos]) - sig2_item_length
					if list1[pos] == "NULL" and list2[pos2] == "NULL":
						Differences.append("")
					else:
						Differences.append(list1[pos][:lengthofdifference])

	if AlignPossibleFlag == True:
		if len(Differences) == len(list1):
			return (AlignedList1, AlignedList2, Differences)
		else:
			return (None, None, None)
	else:
		return (None, None, None)


# ----------------------------------------------------------------------------------------------------------------------------#
def AverageCountOfTopStems(howmany, sig, Signatures, StemCounts):
	stemlist = list(Signatures[sig])
	countlist = []
	count = 0
	average = 0
	for stem in stemlist:
		countlist.append(StemCounts[stem])
	countlist = sorted(countlist, reverse=True)
	if len(countlist) < howmany:
		howmany = len(countlist)
	for n in range(howmany):
		average += countlist[n]
	average = average / howmany
	return average


# ----------------------------------------------------------------------------------------------------------------------------#
def printSignatures(Lexicon, lxalogfile, outfile_signatures, outfile_wordstosigs, outfile_stemtowords, outfile_stemtowords2, outfile_SigExtensions, outfile_suffixes, encoding,
					FindSuffixesFlag):
	# ----------------------------------------------------------------------------------------------------------------------------#



	# Print signatures (not their stems) , sorted by number of stems
	ColumnWidth = 35
	stemcountcutoff = Lexicon.MinimumStemsInaSignature
	SortedListOfSignatures = sorted(Lexicon.SignatureToStems.items(), lambda x, y: cmp(len(x[1]), len(y[1])),
									reverse=True)
	DisplayList = []
	for sig, stems in SortedListOfSignatures:
		if len(stems) < stemcountcutoff:
			continue;
		DisplayList.append((sig, len(stems), getrobustness(sig, stems)))
	DisplayList.sort

	# ____________________________________________
	# This first part is for Jackson's program.

	singleton_signatures = 0
	doubleton_signatures = 0

	for sig, stemcount, robustness in DisplayList:
		if stemcount == 1:
			singleton_signatures += 1
		elif stemcount == 2:
			doubleton_signatures += 1

	totalrobustness = 0
	for sig, stemcount, robustness in DisplayList:
		totalrobustness += robustness

 

	print  >> outfile_signatures,  "{:45s}{:10,d}".format("Number of words: ", len(Lexicon.WordList.mylist))
	print	>> outfile_signatures, "{:45s}{:10,d}".format("Total letter count in words ", Lexicon.TotalLetterCountInWords)
	print 	>> outfile_signatures, "{:45s}{:10,d}".format("Number of signatures: ", len(DisplayList))
	print	>> outfile_signatures, "{:45s}{:10,d}".format("Number of singleton signatures: ", singleton_signatures)
	print	>> outfile_signatures, "{:45s}{:10,d}".format("Number of doubleton signatures: ", doubleton_signatures)
	print	>> outfile_signatures, "{:45s}{:10,d}".format("Total number of letters in stems: ", Lexicon.LettersInStems)
	print	>> outfile_signatures, "{:45s}{:10,d}".format("Total number of affix letters: ", Lexicon.AffixLettersInSignatures)
	print	>> outfile_signatures, "{:45s}{:10,d}".format("Total letters in signatures: ", Lexicon.LettersInStems + Lexicon.AffixLettersInSignatures)
	print	>> outfile_signatures, "{:45s}{:10,d}".format("Number of analyzed words ", Lexicon.NumberOfAnalyzedWords)
	print	>> outfile_signatures, "{:45s}{:10,d}".format("Total number of letters in analyzed words ", Lexicon.LettersInAnalyzedWords)
# 	print	>> outfile_signatures, "{:45s}{:10.2f}".format("Compression ", (Lexicon.LettersInAnalyzedWords - Lexicon.LettersInStems - Lexicon.AffixLettersInSignatures)/ float(Lexicon.LettersInAnalyzedWords))
 	print


	
 

	print  >>lxalogfile,  "{:45s}{:10,d}".format("Number of words: ", len(Lexicon.WordList.mylist))
	print  >>lxalogfile, "{:45s}{:10,d}".format("Total letter count in words ", Lexicon.TotalLetterCountInWords)
	print  >>lxalogfile, "{:45s}{:10,d}".format("Number of signatures: ", len(DisplayList))
	print  >>lxalogfile, 	"{:45s}{:10,d}".format("Number of singleton signatures: ", singleton_signatures)
	print  >>lxalogfile, 	"{:45s}{:10,d}".format("Number of doubleton signatures: ", doubleton_signatures)
	print  >>lxalogfile, 	"{:45s}{:10,d}".format("Total number of letters in stems: ", Lexicon.LettersInStems)
	print  >>lxalogfile, 	"{:45s}{:10,d}".format("Total number of affix letters: ", Lexicon.AffixLettersInSignatures)
	print  >>lxalogfile, 	"{:45s}{:10,d}".format("Total letters in signatures: ", Lexicon.LettersInStems + Lexicon.AffixLettersInSignatures)
	print  >>lxalogfile, 	"{:45s}{:10,d}".format("Number of analyzed words ", Lexicon.NumberOfAnalyzedWords)
	print  >>lxalogfile, 	"{:45s}{:10,d}".format("Total number of letters in analyzed words ", Lexicon.LettersInAnalyzedWords)
# 	print  >>lxalogfile, "{:45s}{:10.2f}".format("Compression ", (Lexicon.LettersInAnalyzedWords - Lexicon.LettersInStems - Lexicon.AffixLettersInSignatures)/ float(Lexicon.LettersInAnalyzedWords))
 	print



	print   "  {:45s}{:10,d}".format("Number of words: ", len(Lexicon.WordList.mylist))
	print	"  {:45s}{:10,d}".format("Total letter count in words ", Lexicon.TotalLetterCountInWords)
	print 	"  {:45s}{:10,d}".format("Number of signatures: ", len(DisplayList))
	print	"  {:45s}{:10,d}".format("Number of singleton signatures: ", singleton_signatures)
	print	"  {:45s}{:10,d}".format("Number of doubleton signatures: ", doubleton_signatures)
	print	"  {:45s}{:10,d}".format("Total number of letters in stems: ", Lexicon.LettersInStems)
	print	"  {:45s}{:10,d}".format("Total number of affix letters: ", Lexicon.AffixLettersInSignatures)
	print	"  {:45s}{:10,d}".format("Total letters in signatures: ", Lexicon.LettersInStems + Lexicon.AffixLettersInSignatures)
	print	"  {:45s}{:10,d}".format("Number of analyzed words ", Lexicon.NumberOfAnalyzedWords)
	print	"  {:45s}{:10,d}".format("Total number of letters in analyzed words ", Lexicon.LettersInAnalyzedWords)
# 	print	"  {:45s}{:10.2f}".format("Compression ", (Lexicon.LettersInAnalyzedWords - Lexicon.LettersInStems - Lexicon.AffixLettersInSignatures)/ float(Lexicon.LettersInAnalyzedWords))
 	print


 	for sig, stemcount, robustness in DisplayList:
		if len(Lexicon.SignatureToStems[sig]) > 5:
			Lexicon.Multinomial(sig,FindSuffixesFlag)



 
	runningsum = 0.0
	if (False):
		print >> outfile_signatures, "\n" + "-" * 150
		print >> outfile_signatures, '{0:<70}{1:>20s} {2:>10s} {3:>25s} {4:>20s} '.format("Signature", "Stem count",
																						  "Robustness",
																						  "Proportion of robustness",
																						  "Running sum")
		print >> outfile_signatures, "-" * 150
		for sig, stemcount, robustness in DisplayList:
			runningsum += robustness
			if len(sig) == 0:
				print >> outfile_signatures, "PROBLEM!!"
			if encoding == "utf8":
				print >> outfile_signatures, sig, stemcount, robustness
			else:
				print >> outfile_signatures, '{0:<70}{1:10d} {2:15d} {3:25.3%} {4:20.3%}'.format(sig, stemcount, robustness, float(robustness) / totalrobustness, runningsum / totalrobustness)
		print >> outfile_signatures, "--------------------------------------------------------------"

	# Print signatures (not their stems) sorted by robustness
	if (True):
		print "  Printing signature file."
		print >> outfile_signatures, "\n" + "-" * 150
		print >> outfile_signatures, '{0:<70}{1:>10s} {2:>15s} {3:>25s} {4:>20s} '.format("Signature", "Stem count", "Robustness", "Proportion of robustness", 	  "Running sum")
		print >> outfile_signatures, "-" * 150		
		DisplayList = sorted(DisplayList, lambda x, y: cmp(x[2], y[2]), reverse=True)
 
		for sig, stemcount, robustness in DisplayList:
			runningsum+=robustness
			if stemcount < stemcountcutoff:
				break;
			if encoding == "utf8":
				print >> outfile_signatures, sig, stemcount, robustness
			else:
				formatstring = '{:<70}{:10d} {:15d} {:25.3%} {:20.3%}'
				robustnessproportion = float(robustness) / totalrobustness
				runningsumproportion = runningsum/totalrobustness
				print >> outfile_signatures, formatstring.format(sig, stemcount, robustness,robustnessproportion, runningsumproportion )
		print >> outfile_signatures, "--------------------------------------------------------------"




	# for sig, stemcount, robustness in DisplayList:

	# print the stems of each signature:

	numberofstemsperline = 6
	stemlist = []
	reversedstemlist = []
	count = 0
	print >> outfile_signatures, "*** Stems in each signature"
	for sig, stemcount, robustness in DisplayList:
		if encoding == "utf8":
			print >> outfile_signatures, "\n=============================================\n", sig, "\n"
		else:
			print >> outfile_signatures, "\n=============================================\n", '{0:30s} \n'.format(sig)
		n = 0

		stemlist = Lexicon.SignatureToStems[sig].keys()
		stemlist.sort()
		numberofstems = len(stemlist)
		for stem in stemlist:
			n += 1
			print >> outfile_signatures, '{0:12s}'.format(stem),
			if n == numberofstemsperline:
				n = 0
				print >> outfile_signatures
		print >> outfile_signatures, "\n-------------------------"
		# ------------------- New -----------------------------------------------------------------------------------
		howmany = 5		
		print >>outfile_signatures, "Average count of top",howmany, " stems:" , AverageCountOfTopStems(howmany, sig, Lexicon.SignatureToStems, Lexicon.StemCounts)
		

		# ------------------------------------------------------------------------------------------------------
		bitsPerLetter = 5
		wordlist = makeWordListFromSignature(sig, Lexicon.SignatureToStems[sig])
		(a, b, c) = findWordListInformationContent(wordlist, bitsPerLetter)
		(d, e, f) = findSignatureInformationContent(Lexicon.SignatureToStems, sig, bitsPerLetter)
		formatstring = '%35s %10d  '
		formatstringheader = '%35s %10s    %10s  %10s'
		print >> outfile_signatures, formatstringheader % ("", "Phono", "Ordering", "Total")
		print >> outfile_signatures, formatstring % ("Letters in words if unanalyzed:", a   )
		print >> outfile_signatures, formatstring % ("Letters as analyzed:", d)
		# ------------------------------------------------------------------------------------------------------
		howmanytopstems = 5
		


		print >> outfile_signatures, "\n-------------------------"
		print >> outfile_signatures, "Entropy-based stability: ", StableSignature(stemlist,FindSuffixesFlag)
		print >> outfile_signatures, "\n", "High frequency possible affixes \nNumber of stems: ", len(stemlist)
		formatstring = '%10s    weight: %5d count: %5d %2s'
		peripheralchunklist = find_N_highest_weight_affix(stemlist, FindSuffixesFlag)

		for item in peripheralchunklist:
			if item[2] >= numberofstems * 0.9:
				flag = "**"
			else:
				flag = ""
			print >> outfile_signatures, formatstring % (item[0], item[1], item[2], flag)

			# print WORDS of each signature:
	if True:
		words = Lexicon.WordToSig.keys()
		words.sort()
		print >> outfile_wordstosigs, "***"
		print >> outfile_wordstosigs, "\n--------------------------------------------------------------"
		print >> outfile_wordstosigs, "Words and their signatures"
		print >> outfile_wordstosigs, "--------------------------------------------------------------"
		maxnumberofsigs = 0
		ambiguity_counts = dict()
		for word in Lexicon.WordToSig:
			ambiguity = len(Lexicon.WordToSig[word])
			if ambiguity not in ambiguity_counts:
				ambiguity_counts[ambiguity] = 0
			ambiguity_counts[ambiguity] += 1
			if len(Lexicon.WordToSig[word]) > maxnumberofsigs:
				maxnumberofsigs = len(Lexicon.WordToSig[word])
				#print word, maxnumberofsigs
		print >> lxalogfile, "How many words have multiple analyses?"
		print "  How many words have multiple analyses?"
		for i in range(maxnumberofsigs):
			if i in ambiguity_counts:
				print >> lxalogfile, "{:4d}{:10,d}".format(i, ambiguity_counts[i])
				print             	 "{:4d}{:10,d}".format(i, ambiguity_counts[i])
 

		wordlist = Lexicon.WordToSig.keys()
		wordlist.sort()

		for word in wordlist:
			print >> outfile_wordstosigs, '{0:<30}'.format(word), ":",
			for n in range(len(Lexicon.WordToSig[word])):				
				sig = MakeStringFromSignature(Lexicon.WordToSig[word][n], ColumnWidth)
				print >> outfile_wordstosigs, sig + " " * (ColumnWidth - len(sig)),
			print >> outfile_wordstosigs

 
	print >>outfile_suffixes,  "--------------------------------------------------------------"
	print >>outfile_suffixes , "        Suffixes "
	print >>outfile_suffixes,  "--------------------------------------------------------------"
	print "  Printing suffixes."
	suffixlist = list(Lexicon.Suffixes.keys())
	suffixlist.sort(key=lambda  suffix:Lexicon.Suffixes[suffix], reverse=True)
	for suffix in suffixlist:
		print >>outfile_suffixes,"{:8s}{:9,d}".format(suffix, Lexicon.Suffixes[suffix])


	stems = Lexicon.StemToWord.keys()
	stems.sort()
	print >> outfile_stemtowords, "--------------------------------------------------------------"
	print >> outfile_stemtowords, "---  Stems and their words"
	print >> outfile_stemtowords, "--------------------------------------------------------------"
	print "  Printing stems and their words."
	Lexicon.StemCounts = dict()
	for stem in stems:
		print >> outfile_stemtowords, '{:15}'.format(stem),
		wordlist = Lexicon.StemToWord[stem].keys()
		wordlist.sort()
		stemcount = 0
		for word in wordlist:
			stemcount += Lexicon.WordCounts[word]
		Lexicon.StemCounts[stem]=stemcount
		print 	 >> outfile_stemtowords, '{:5d}'.format(stemcount),'; ',
		stemcount = float(stemcount)	
		for word in wordlist:
			wordcount = Lexicon.WordCounts[word]
			print >> outfile_stemtowords, '{:15}{:4n} {:7.1%} '.format(word,wordcount, wordcount/stemcount),
		print >> outfile_stemtowords

        # We print a list of stems with their words (and frequencies) in which only those suffixes which are among the K most frequent suffixes,
        # in order to use visualization methods that put soft limits on the number of dimensions they can handle well.
        
        threshold_for_top_affixes = 11 # this will give us one more than that number, since we are zero-based counting.
        top_affixes = suffixlist[0:threshold_for_top_affixes]
	print >> outfile_stemtowords2, "\n--------------------------------------------------------------"
	print >> outfile_stemtowords2, "---  Stems and their words with high frequency affixes"
	print >> outfile_stemtowords2, "--------------------------------------------------------------"
	print "  Printing stems and their words, but only with high frequency affixes."
	print >>outfile_stemtowords2, "---\n--- Only signatures with these affixes: ", top_affixes
	print >>outfile_stemtowords2, "---"
	Lexicon.StemCounts = dict()
	for stem in stems:
	        signature = Lexicon.StemToSignature[stem]
	        for affix in signature:
	                if affix not in top_affixes:
	                        print stem, signature, affix
	                        continue 
		print >> outfile_stemtowords2, '{:15}'.format(stem),
		wordlist = Lexicon.StemToWord[stem].keys()
		wordlist.sort()
		stemcount = 0
		for word in wordlist:
			stemcount += Lexicon.WordCounts[word]
		Lexicon.StemCounts[stem]=stemcount
		print 	 >> outfile_stemtowords2, '{:5d}'.format(stemcount),'; ',
		stemcount = float(stemcount)	
		for word in wordlist:
			wordcount = Lexicon.WordCounts[word]
			print >> outfile_stemtowords2, '{:15}{:4n} {:7.1%} '.format(word,wordcount, wordcount/stemcount),
		print >> outfile_stemtowords2        
        print top_affixes





	print >>outfile_SigExtensions,  "--------------------------------------------------------------"
	print >>outfile_SigExtensions , "        Signature extensions  "
	print >>outfile_SigExtensions,  "--------------------------------------------------------------"
	print "  Printing signature extensions."
	ListOfAlternations = list()
	ListOfAlternations2 = list()
	DictOfAlternations = dict()
	AlternationDict = dict()
	count = 0
	for (sig1,stemcount,robustness)  in  DisplayList:
		 
		if count > 100:
			break
		count += 1


		#if count > 10:
			#print sig1, count
		#print >>lxalogfile, "897", "sig1", sig1 

		for sig2, count2, robustness2 in DisplayList:

			if len(sig1) != len(sig2) :
				continue

			(AlignedList1, AlignedList2, Differences) = Sig1ExtendsSig2(sig2,sig1,lxalogfile)
			stemcount = len(Lexicon.SignatureToStems[sig2])

			

			if  AlignedList1 != None:
				print >>outfile_SigExtensions, "{:35s}{:35s}{:35s}".format(AlignedList1, AlignedList2, Differences), 
				#Make CAlternation:
				this_alternation = CAlternation(stemcount)
				for i  in range(len(AlignedList1)):
					this_alloform = CAlloform(Differences[i], AlignedList2[i], stemcount)
					this_alternation.AddAlloform (this_alloform)
				print  >>outfile_SigExtensions, this_alternation.display()
 				ListOfAlternations.append(this_alternation)

 				if (False):
		 			print >>outfile_SigExtensions, "A", FindSuffixesFlag, "{:35s}{:35s}{:35s}".format(AlignedList1, AlignedList2, Differences)
		 			if len(AlignedList1)==2:
		 				alternation = (Differences[0],  Differences[1])
			 			ListOfAlternations.append((Differences[0], AlignedList2[0], Differences[1], AlignedList2[1]))
			 			if alternation not in DictOfAlternations:
			 				DictOfAlternations[alternation]= list()
			 			DictOfAlternations[alternation].append((Differences[0], AlignedList2[0], Differences[1], AlignedList2[1]))

	ListOfAlternations.sort(key=lambda item:item.Count, reverse=True)
 	for item in ListOfAlternations:
 		if item.Count > 1:
	 		print >>outfile_SigExtensions, item.display()

 	print >>outfile_SigExtensions, "*"*50
	print >>outfile_SigExtensions, "*"*50


	ListOfAlternations.sort(key=lambda item:item.Alloforms[0].Form)
 	for item in ListOfAlternations:
 		if item.Count > 1:
	 		print >>outfile_SigExtensions, item.Alloforms[0].Form, item.display()


	outfile_SigExtensions.flush()

	return


# ----------------------------------------------------------------------------------------------------------------------------#
def MakeStringFromSignature(sigset, maxlength):
	sig = "-".join(list(sigset))
	if len(sig) >  maxlength-2:
		sig = sig[:maxlength-5] + "..."
	return sig

def MakeStringFromAlternation(s1,s2,s3,s4):
	if s1== "":
		s1 = "nil"
	if s2== "NULL":
		s2 = "#"
	if s3== "":
		s3 = "nil"
	if s4== "NULL":
		s4 = "#"

	str = "{:4s} before {:5s}, and {:4s} before  {:5s}".format(s1,s2,s3,s4)
	return str

# ----------------------------------------------------------------------------------------------------------------------------#

def EvaluateSignatures(Lexicon, outfile):
	for sig in Lexicon.Signatures:
		print >> outfile, sig.Display()


# ----------------------------------------------------------------------------------------------------------------------------#
def RemoveRareSignatures(Lexicon, encoding, FindSuffixesFlag, outfile):
	# ----------------------------------------------------------------------------------------------------------------------------#
	#  we check to see which words currently are associated with more than one signature.
	# For those words that are, we choose the signature with the largest number of stems.

	MinStemCount = Lexicon.MinimumStemsInaSignature

	RobustnessCutoff = 1000  # signatures with this robustness are considered secure, and factorable.
	for sig in Lexicon.SignatureToStems:
		if Robustness(sig) < RobustnessCutoff:
			continue


# ----------------------------------------------------------------------------------------------------------------------------#
def SliceSignatures(Lexicon, encoding, FindSuffixesFlag, outfile):
	# ----------------------------------------------------------------------------------------------------------------------------#
	# we look to see if highly robust signatures like NULL.ly can be used to simplify
	# other longer signatures, like NULL.al.ally, making it NULL.al(ly), feeding NULL.ly
	# This is easiest to detect with the signatures, but easiest to implement the changes in the FSA.


	RobustnessCutoff = 1000  # signatures with this robustness are considered secure, and factorable.
	NumberOfStemsThreshold = 30
	for sig in Lexicon.SignatureToStems:
		if len(Lexicon.SignatureToStems[sig]) < NumberOfStemsThreshold:
			continue
		print >> outfile, "sig: ", sig
		for stem in Lexicon.SignatureToStems[sig]:
			# construct its words from its stems
			# those words should all share the same signatures
			# other than sig, how many are there?
			wordlist = list()
			# print "stem: ", stem,
			for affix in sig:
				if affix == "NULL":
					affix = ""
				word = stem + affix
				wordlist.append(word)
			# print wordlist,
			firstword = wordlist.pop()
			signatureset = Lexicon.WordToSig[firstword]
			# print firstword, signatureset
			for word in wordlist:
				this_signatureset = Lexicon.WordToSig[word]
				# if this_signatureset != signatureset:
				print >> outfile, '{:20}{:70}{:20}{:35}'.format(firstword, signatureset, word, this_signatureset)





				# ----------------------------------------------------------------------------------------------------------------------------#
	return


# ----------------------------------------------------------------------------------------------------------------------------#
def printWordsToSigTransforms(SignatureToStems, WordToSig, StemCounts, outfile_SigTransforms, g_encoding,
							  FindSuffixesFlag):
	sigtransforms = dict()
	for sig in SignatureToStems:
		affixes = list(sig)
		affixes.sort()
		sig_string = "-".join(affixes)
		stems = SignatureToStems[sig]
		for stem in stems:
			for affix in sig:
				if affix == "NULL":
					word = stem
				else:
					word = stem + affix
				transform = sig_string + "_" + affix
				if not word in sigtransforms:
					sigtransforms[word] = list()
				sigtransforms[word].append(transform)
	wordlist = sigtransforms.keys()
	wordlist.sort()
	for word in wordlist:
		print >> outfile_SigTransforms, '{:15}'.format(word),
		for sig in sigtransforms[word]:
			print >> outfile_SigTransforms, '{:35}'.format(sig),
		print >> outfile_SigTransforms

	# print >>outfile, '%18s' %self.affixlabels[affix],
	# ----------------------------------------------------------------------------------------------------------------------------#
	return


# ----------------------------------------------------------------------------------------------------------------------------#


# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------



 





# ----------------------------------------------------------------------------------------------------------------------------#
def ShiftFinalLetter(StemToWord, StemCounts, stemlist, CommonLastLetter, sig, FindSuffixesFlag, outfile):
	# ----------------------------------------------------------------------------------------------------------------------------#
	# print >>outfile, "Shift final letter: ", CommonLastLetter
	newsig = ''
	affixlist = sig.split('-')
	newaffixlist = []
	listOfAffectedWords = list()
	for affix in affixlist:
		if affix == "NULL":
			newaffixlist.append(CommonLastLetter)
		else:
			if FindSuffixesFlag:
				newaffixlist.append(CommonLastLetter + affix)
			else:
				newaffixlist.append(affix + CommonLastLetter)  # really commonfirstletter...change name of variable
	newsig = makesignature(newaffixlist)
	# print >>outfile, "old sig", sig, "new sig", newsig
	for stem in stemlist:
		# print >>outfile, "shifting this stem: ", stem
		if FindSuffixesFlag:
			if not stem[-1] == CommonLastLetter:
				# print >>outfile, "\tNo good fit: ", stem
				continue
		else:
			if not stem[0] == CommonLastLetter:
				continue
		if FindSuffixesFlag:
			newstem = stem[:-1]
		else:
			newstem = stem[1:]
		if not newstem in StemCounts.keys():
			StemCounts[newstem] = StemCounts[stem]
		else:
			StemCounts[newstem] += StemCounts[stem]
		del StemCounts[stem]

		if not newstem in StemToWord.keys():
			StemToWord[newstem] = set()

		listOfAffectedWords = StemToWord[stem].copy()
		for word in listOfAffectedWords:
			StemToWord[stem].remove(word)
			StemToWord[newstem].add(word)
			# print >>outfile, "We're adding" , newstem , "as the stem of ", word
			if not word in StemToWord[newstem]:
				StemToWord[newstem].add(word)
		if len(StemToWord[stem]) == 0:
			# print >>outfile, "we're deleting this stemtoword stem, no longer used", stem
			del StemToWord[stem]

			# ----------------------------------------------------------------------------------------------------------------------------#
	return (StemToWord, newsig)


# ----------------------------------------------------------------------------------------------------------------------------#











# ----------------------------------------------------------------------------------------------------------------------------#
def findmaximalrobustsuffix(wordlist):
	# ----------------------------------------------------------------------------------------------------------------------------#
	bestchunk = ""
	bestwidth = 0
	bestlength = 0
	bestrobustness = 0
	maximalchunksize = 4  # should be 3 or 4 ***********************************
	threshold = 50
	bestsize = 0
	# sort by end of words:
	templist = []
	for word in wordlist:
		wordrev = word[::-1]
		templist.append(wordrev)
	templist.sort()
	wordlist = []
	for wordrev in templist:
		word = wordrev[::-1]
		wordlist.append(word)
	for width in range(1, maximalchunksize + 1):  # width is the size (in letters) of the suffix being considered
		numberofoccurrences = 0
		here = 0
		while (here < len(wordlist) - 1):
			numberofoccurrences = 0
			chunk = wordlist[here][-1 * width:]
			for there in range(here + 1, len(wordlist)):
				if (not wordlist[there][-1 * width:] == chunk) or (there == len(wordlist) - 1):
					numberofoccurrences = there - here
					currentrobustness = numberofoccurrences * width
					if currentrobustness > bestrobustness:
						bestrobustness = currentrobustness
						bestchunk = chunk
						bestwidth = width
						bestnumberofoccurrences = numberofoccurrences
						count = numberofoccurrences
					break
			here = there
	permittedexceptions = 2
	if bestwidth == 1:
		if bestnumberofoccurrences > 5 and bestnumberofoccurrences >= len(
				wordlist) - permittedexceptions and bestrobustness > threshold:
			return (bestchunk, bestrobustness)
	if bestrobustness > threshold:
		return (bestchunk, bestrobustness)
	# ----------------------------------------------------------------------------------------------------------------------------#
	return ('', 0)


# ----------------------------------------------------------------------------------------------------------------------------#


# ----------------------------------------------------------------------------------------------------------------------------#
def find_N_highest_weight_affix(wordlist, FindSuffixesFlag):
	# ----------------------------------------------------------------------------------------------------------------------------#

	maximalchunksize = 6  # should be 3 or 4 ***********************************
	totalweight = 0
	# threshold 		= 50
	weightthreshold = 0.02
	# permittedexceptions 	= 2
	MinimalCount = 10
	chunkcounts = {}
	chunkweights = {}
	chunkweightlist = []
	tempdict = {}
	templist = []
	for word in wordlist:
		totalweight += len(word)

	if FindSuffixesFlag:
		for word in wordlist:
			for width in range(1, maximalchunksize + 1):  # width is the size (in letters) of the suffix being considered
				chunk = word[-1 * width:]
				if not chunk in chunkcounts.keys():
					chunkcounts[chunk] = 1
				else:
					chunkcounts[chunk] += 1
	else:
		for word in wordlist:
			for width in range(1, maximalchunksize + 1):  # width is the size (in letters) of the prefix being considered
				chunk = word[:width]
				if not chunk in chunkcounts.keys():
					chunkcounts[chunk] = 1
				else:
					chunkcounts[chunk] += 1
	for chunk in chunkcounts.keys():
		chunkweights[chunk] = chunkcounts[chunk] * len(chunk)
		if chunkweights[chunk] < weightthreshold * totalweight:
			continue
		if chunkcounts[chunk] < MinimalCount:
			continue
		tempdict[chunk] = chunkweights[chunk]

	templist = sorted(tempdict.items(), key=lambda chunk: chunk[1], reverse=True)
	for stem, weight in templist:
		chunkweightlist.append((stem, weight, chunkcounts[stem]))

	# ----------------------------------------------------------------------------------------------------------------------------#
	return chunkweightlist


# ----------------------------------------------------------------------------------------------------------------------------#
 

def FindSignatureDifferences():
	Differences = list()
	for sig1, stemlist1 in SortedListOfSignatures:
		for sig2, stemlist2 in SortedListOfSignatures:
			if sig1 == sig2: continue
			list1, list2, differences = Sig1ExtendsSig2(sig1, sig2, outfile)
			Differences.append((sig1, sig2, list1, list2, differences))

	Differences.sort(key=lambda entry: entry[4])
	width = 25
	h1 = "Sig 1"
	h2 = "Sig 2"
	h3 = "List 1"
	h4 = "List 2"
	h5 = "differences"
	print >> outfile, "Differences between similar pairs of signatures"
	print >> outfile, h1, " " * (width - len(h1)), \
	h2, " " * (width - len(h2)), \
	h3, " " * (width - len(h3)), \
	h4, " " * (width - len(h4)), \
	h5, " " * (width - len(h5))
	for item in Differences:
		if item[3] != None:
			sig1string = list_to_string(item[2])
			sig2string = list_to_string(item[3])
			print >> outfile, item[0], " " * (width - len(item[0])), \
			item[1], " " * (width - len(item[1])), \
			sig1string, " " * (width - len(sig1string)), \
			sig2string, " " * (width - len(sig2string)), \
			item[4], " " * (width - len(item[4]))


def AddSignaturesToFSA(Lexicon, SignatureToStems, fsa, FindSuffixesFlag):
	for sig in SignatureToStems:
		affixlist = list(sig)
		stemlist = Lexicon.SignatureToStems[sig]
		if len(stemlist) >= Lexicon.MinimumStemsInaSignature:
			if FindSuffixesFlag:
				fsa.addSignature(stemlist, affixlist, FindSuffixesFlag)
			else:
				fsa.addSignature(affixlist, stemlist, FindSuffixesFlag)


# ----------------------------------------------------------------------------------------------------------------------------#
def ShiftSignature(sig_target, shift, StemToWord, Signatures, outfile):
	# ----------------------------------------------------------------------------------------------------------------------------#
	print >> outfile, "-------------------------------------------------------"
	print >> outfile, "Shift wrongly cut suffixes"
	print >> outfile, "-------------------------------------------------------"
	suffixlist = []
	print >> outfile, sig_target, shift
	suffixes = sig_target.split('-')
	for n in range(len(suffixes)):
		if suffixes[n] == 'NULL':
			suffixes[n] = ''
	for suffix in suffixes:
		suffix = shift + suffix
		suffixlist.append(suffix)
	suffixlist.sort()
	newsig = '-'.join(suffixlist)
	Signatures[newsig] = set()
	shiftlength = len(shift)
	stemset = Signatures[sig_target].copy()  # a set to iterate over while removing stems from Signature[sig_target]
	for stem in stemset:
		thesewords = []
		if not stem.endswith(shift):
			continue
		newstem = stem[:-1 * shiftlength]
		for suffix in suffixes:
			thesewords.append(stem + suffix)
		Signatures[sig_target].remove(stem)
		Signatures[newsig].add(newstem)
		for word in thesewords:
			StemToWord[stem].remove(word)
		if len(StemToWord[stem]) == 0:
			del StemToWord[stem]
		if not newstem in StemToWord:
			StemToWord[newstem] = set()
		for word in thesewords:
			StemToWord[newstem].add(word)
	if len(Signatures[sig_target]) == 0:
		del Signatures[sig_target]
	# ----------------------------------------------------------------------------------------------------------------------------#
	return (StemToWord, Signatures)


# ----------------------------------------------------------------------------------------------------------------------------#




# ----------------------------------------------------------------------------------------------------------------------------#
def PullOffSuffix(sig_target, shift, StemToWord, Signatures, outfile):
	# ----------------------------------------------------------------------------------------------------------------------------#
	print >> outfile, "-------------------------------------------------------"
	print >> outfile, "Pull off a suffix from a stem set"
	print >> outfile, "-------------------------------------------------------"
	print >> outfile, sig_target, shift

	shiftlength = len(shift)
	newsig = shift
	suffixes = sig_target.split('-')
	stemset = Signatures[sig_target].copy()  # a set to iterate over while removing stems from Signature[sig_target]
	while newsig in Signatures:
		newsig = "*" + newsig  # add *s to beginning to make sure the string is unique, i.e. not used earlier elsewhere

	Signatures[newsig] = set()
	StemToWord["*" + shift] = sig_target

	for stem in stemset:
		thesewords = []
		if not stem.endswith(shift):
			continue
		newstem = stem[:-1 * shiftlength]
		for suffix in suffixes:
			if suffix == "NULL":
				word = stem
			else:
				word = stem + suffix
			StemToWord[stem].remove(word)

		if len(StemToWord[stem]) == 0:
			del StemToWord[stem]
		if newstem in StemToWord:
			newstem = "*" + newstem
			StemToWord[newstem] = set()
		for word in thesewords: StemToWord[newstem].add(word)
	if len(Signatures[sig_target]) == 0:
		del Signatures[sig_target]
	# ----------------------------------------------------------------------------------------------------------------------------#
	return (StemToWord, Signatures)


# ----------------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------------------------------##
#		Start, end latex doc
# --------------------------------------------------------------------##
def StartLatexDoc(outfile):
	header0 = "\documentclass[10pt]{article} \n\\usepackage{booktabs} \n\\usepackage{geometry} \n\\geometry{verbose,letterpaper,lmargin=0.5in,rmargin=0.5in,tmargin=1in,bmargin=1in} \n\\begin{document}  \n"
	print >> outfile, header0


def EndLatexDoc(outfile):
	footer = "\\end{document}"
	print >> outfile, footer
	outfile.close()


# --------------------------------------------------------------------##
#		Make latex table
# --------------------------------------------------------------------##
def MakeLatexFile(outfile, datalines):
	tablelines = []
	longestitem = 1
	numberofcolumns = 0
	for line in datalines:
		line = line.replace("NULL", "\\emptyset")
		line = line.replace(u"\u00FC", "\\\"{u}")
		line = line.replace(u"\u00F6", "\\\"{o}")
		items = line.split()
		if len(items) > numberofcolumns:
			numberofcolumns = len(items)
		tablelines.append(items)
		for piece in items:
			if len(piece) > longestitem:
				longestitem = len(piece)
		header1 = "\\begin{centering}\n"
	header2 = "\\begin{tabular}{"
	header3 = "\\toprule "
	footer1 = "\\end{tabular}"
	footer2 = "\\end{centering}\n"
	print >> outfile, header1
	print >> outfile, header2, 'l' * numberofcolumns, "}", header3

	for m in range(len(tablelines)):
		line = tablelines[m]
		for n in range(len(line)):
			field = line[n]
			if field == "@":
				print >> outfile, " " * longestitem,
			elif len(field.split(":")) == 2:
				fraction = field.split(":")
				field = "$\\frac{" + fraction[0] + "}{" + fraction[1] + "}$"
				print >> outfile, field + " " * (longestitem - len(field)),
			else:
				print >> outfile, field + " " * (longestitem - len(field)),
			if n < len(line) - 1:
				print >> outfile, "&",

		if m == 0:
			print >> outfile, "\\\\ \\midrule"
		else:
			print >> outfile, "\\\\"
	print >> outfile, "\\bottomrule", "\n"
	print >> outfile, footer1
	print >> outfile, footer2

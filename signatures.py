import math
import os
import sys
from ClassLexicon import *
from lxa_module import *
# ----------------------------------------------------------------------------------------------------------------------------#
def MakeSignatures(Lexicon, lxalogfile,outfile_Rebalancing_Signatures, FindSuffixesFlag, MinimumStemLength):
	# ----------------------------------------------------------------------------------------------------------------------------#

	 

	# Protostems are candidate stems made during the algorithm, but not kept afterwards.
	Protostems = dict()
	Lexicon.NumberOfAnalyzedWords = 0
	Lexicon.LettersInAnalyzedWords = 0
	Lexicon.NumberOfUnanalyzedWords = 0
	Lexicon.LettersInUnanalyzedWords = 0
	
	AnalyzedWords = dict()

 
	#Lexicon.TotalLetterCountInWords = 0

	Lexicon.TotalRobustnessInSignatures = 0
	Lexicon.LettersInStems = 0
	Lexicon.TotalLetterCostOfAffixesInSignatures = 0

	FindProtostems(Lexicon.WordList.mylist, Protostems, Lexicon.MinimumStemLength, FindSuffixesFlag)
	print "{:50s}{:>10,}".format("2a. Finished finding proto-stems.", len(Protostems)) 

 

	FindAffixes( Lexicon, Protostems,  FindSuffixesFlag)
	print "{:50s}{:>10,}".format("2b. Finished finding affixes for protostems.", len(Lexicon.Suffixes)+ len(Lexicon.Prefixes)) 	
 
	# It is possible for a stem to have only one affix at this point. We must eliminate those analyses.

	ListOfStemsToRemove = list()
	for stem in Lexicon.StemToAffix:
		if len(Lexicon.StemToAffix[stem]) < 2:
			#print "Removing: ", stem, Lexicon.StemToAffix[stem]
			ListOfStemsToRemove.append(stem)
 
	print "{:50s}{:>10,}".format("2c. Number of stems to remove due to mono-fixivity:", len(ListOfStemsToRemove)) 	

	for stem in ListOfStemsToRemove:
		del Lexicon.StemToWord[stem]
		del Lexicon.StemToAffix[stem]
	 
 





 
	Lexicon.LettersInStems =0
	Lexicon.TotalLetterCostOfAffixesInSignatures =0
	Lexicon.StemsToSignatures(FindSuffixesFlag)


	print "{:50s}{:>10,}".format("2d. Finished finding signatures.", len(Lexicon.SignatureToStems))  
	 
 

	# We look for a stem-final sequence that appears on all or almost all the stems, and shift it to affixes.
	# Make changes in Lexicon.SignatureToStems, and .StemToSig, and .WordToSig, and .StemToWord, and .StemToAffix  and signature_tuples....
	
	threshold = 0.80
	count = RebalanceSignatureBreaks2 (Lexicon, threshold, outfile_Rebalancing_Signatures, FindSuffixesFlag)

	print "{:50s}{:10d}".format("2e. Rebalance signature breaks.",count) 
	 
	if True:
		if FindSuffixesFlag:
			Affixes = Lexicon.Suffixes
		else:
			Affixes = Lexicon.Prefixes
	 	FindSignatureStructure (Lexicon,FindSuffixesFlag, lxalogfile, Affixes, affix_threshold=3)
 


 	#compute robustness
	Lexicon.ComputeRobustness()


 	

	print >> lxalogfile, "{:40s}{:10,d}".format("Number of analyzed words", Lexicon.NumberOfAnalyzedWords)
	print >> lxalogfile, "{:40s}{:10,d}".format("Number of unanalyzed words", Lexicon.NumberOfUnanalyzedWords)
	print >> lxalogfile, "{:40s}{:10,d}".format("Letters in stems", Lexicon.LettersInStems)
	print >> lxalogfile, "{:40s}{:10,d}".format("Letters in affixes", Lexicon.AffixLettersInSignatures)
	print >> lxalogfile, "{:40s}{:10,d}".format("Total robustness in signatures", Lexicon.TotalRobustnessInSignatures)
	
	return

# ----------------------------------------------------------------------------------------------------------------------------#
def FindSignatureStructure (Lexicon, FindSuffixesFlag, outfile, Affixes = None, affix_threshold = 1):

	# This function assumes that we have the set of stems already in Lexicon.SignatureToStems. It does the rest.

	StemList = Lexicon.StemToWord.keys()
 	Lexicon.StemToSig = {}
	Lexicon.StemToAffix = {}# ok
	Lexicon.StemToWord = dict()# ok
	Lexicon.Signatures = {}
	Lexicon.SignatureToStems = {}
	Lexicon.WordToSig = {}
	Lexicon.StemCounts = {}
	 
 

	#  Signatures with way too many affixes are spurious.
	# If we have already run this function before, we have a set of affixes ranked by frequency,
	# and we can use these now to eliminate low frequency suffixes from signatures with
	# just one affix. 
	# Lexicon.MaximumNumberOfAffixesInASignature
	# Number of affixes we are confident in:

	print "2f1. Finding affixes we are confident about."
	number_of_affixes_per_line = 10
 


	if len (Affixes ) ==0:
		if FindSuffixesFlag:
			print "No suffixes found yet."
		else:
			print "No prefixes found yet." 
	else:
		NumberOfConfidentAffixes = 50
		ConfidentAffixes = dict()
		SortedAffixes = list(Affixes.keys())
		SortedAffixes.sort(key=lambda affix:Affixes[affix], reverse=True)
 
		print "Confidence affixes:"
		count = 0
		for affixno in range(NumberOfConfidentAffixes):
			ConfidentAffixes[SortedAffixes[affixno]]=1
			print  "{:6s} ".format(SortedAffixes[affixno]),
			count += 1
			if count % number_of_affixes_per_line == 0:
				print 

		for sig in Lexicon.SignatureToStems:
			stems = Lexicon.SignatureToStems[sig]
			newsig = list()
			if len(stems) == 1:			
				for affix in sig:
					if affix in ConfidentAffixes:
						newsig.append(affix)
		print 
	 

 


 

	 
 




	 
	# Creates Lexicon.StemToWord, Lexicon.StemToAffix. 
	print "Reanalyzing words." 
	if True:
		print "Word number:"  ,   # loop on words
		for i in range(len(Lexicon.WordList.mylist)):			
			if i % 2500 == 0:
				print "{:7,d}".format(i),			
				sys.stdout.flush()
			word = Lexicon.WordList.mylist[i].Key
				 
			WordAnalyzedFlag = False
			for i in range(len(word)-1 , Lexicon.MinimumStemLength-1, -1):   # loop on positions in the word, left to right
				if FindSuffixesFlag:
					stem = word[:i]
				else:
					stem = word[-1*i:]	
				if stem in StemList:  
					affixlength = len(word)-i
					if FindSuffixesFlag:
						affix = word[i:]
					else:
						affix = word[:affixlength]	
					if len(affix) > Lexicon.MaximumAffixLength:
						continue
					# the next line involves putting a threshold on frequencies of affixes.
					if Affixes and affix in Affixes and Affixes[affix] < affix_threshold:
						continue						
					#print stem, suffix		 	 
					if stem not in Lexicon.StemToWord:
						Lexicon.StemToWord[stem] = dict()
					Lexicon.StemToWord[stem][word]=1
					if stem not in Lexicon.StemToAffix:
						Lexicon.StemToAffix[stem] = dict()
					Lexicon.StemToAffix[stem][affix] = 1 
					if stem in Lexicon.WordCounts:	# this is for the case where the stem is a free-standing word also								 
						Lexicon.StemToWord[stem][word] = 1
						Lexicon.StemToAffix[stem]["NULL"] = 1
					if stem not in Lexicon.StemCounts:
						Lexicon.StemCounts[stem] = 0
					Lexicon.StemCounts[stem]+= Lexicon.WordCounts[word]
 			 
	print
	Lexicon.LettersInStems =0
	Lexicon.TotalLetterCostOfAffixesInSignatures =0		 



	if (False):
		for stem in Lexicon.StemToAffix:
			if len(StemToAffix[stem]) > Lexicon.MaximumNumberOfAffixesInASignature: 
				for sig in Lexicon.SignatureToStems:
					stems = Lexicon.SignatureToStems[sig]
					newsig = list()
					if len(stems) == 1:			
						for affix in sig:
							if affix in ConfidentAffixes:
								newsig.append(affix)
			 


	print "Finding a first set of signatures."
				 


	# From StemToAffix and StemToWord:
	# Create SignaturesToStems, Suffixes, StemToSig, WordToSig
	StemsToEliminate = list()
	for stem in Lexicon.StemToWord:
					 
		Lexicon.LettersInStems += len(stem)
		signature = list(Lexicon.StemToAffix[stem])
		#print stem, signature
					 
		signature.sort()
		signature_tuple = tuple(signature)

		if len(signature) == 1:
			StemsToEliminate.append(stem)
			continue

		if signature_tuple not in Lexicon.SignatureToStems:
			Lexicon.SignatureToStems[signature_tuple] = dict()
			for affix in signature:
				Lexicon.TotalLetterCostOfAffixesInSignatures += len(affix)
				if affix not in Affixes:
					Affixes[affix]=1
				else:
					Affixes[affix] +=1
				 
		Lexicon.SignatureToStems[signature_tuple][stem] = 1
			


		Lexicon.StemToSig[stem] = signature_tuple
		for word in Lexicon.StemToWord[stem]:
			if word not in Lexicon.WordToSig:
				Lexicon.WordToSig[word] = list()
			Lexicon.WordToSig[word].append(signature_tuple)
			Lexicon.LettersInAnalyzedWords += len(word)

	for stem in StemsToEliminate:
		del Lexicon.StemToAffix[stem]
		del Lexicon.StemToWord[stem]

	print "{:50s}{:>10,}".format("2h. Signatures.", len(Lexicon.SignatureToStems)) 
 


	print  "Finished redoing structure"
	print >>outfile, "Finished redoing structure \n "
	#print "Number of sigs: ", len(Lexicon.SignatureToStems)
	print >>outfile, "Number of sigs: ", len(Lexicon.SignatureToStems)
 			 
	 		 




#-----------------------------------------------------------------------------------------------------------------------------#
def FindProtostems(wordlist, Protostems,minimum_stem_length,FindSuffixesFlag):
	previousword = ""
	if FindSuffixesFlag:
		for i in range(len(wordlist)):
			word = wordlist[i].Key
			differencefoundflag = False
			if previousword == "":  # only on first iteration
				previousword = word
				continue
			span = min(len(word), len(previousword))
			for i in range(span):
				if word[i] != previousword[i]: #will a stem be found in the very first word?
					differencefoundflag = True
					stem = word[:i]
					if len(stem) >= minimum_stem_length :
						if stem not in Protostems:
							Protostems[stem] = 1
						else:
							Protostems[stem] += 1
					previousword = word
					break
			if differencefoundflag:
				continue
			if len(previousword) > i + 1:
				previousword = word
				continue
			if (len(word)) >= i:
				if len(previousword) >= minimum_stem_length:
					if (previousword not in Protostems):
						Protostems[previousword] = 1
					else:
						Protostems[previousword] += 1
			previousword = word

	else:
		#print "prefixes"
		ReversedList = list()
		TempList = list()
		for word in wordlist:
			key = word.Key
			key = key[::-1]
			TempList.append(key)
		TempList.sort()
		for word in TempList:
			ReversedList.append(word[::-1])
		for i in range(len(ReversedList)):
 			word = ReversedList[i]
  			differencefoundflag = False
			if previousword == "":  # only on first iteration
				previousword = word
				continue
			span = min(len(word), len(previousword))
			for i in range(1,span,):
				if word[-1*i] != previousword[-1*i]:
					differencefoundflag = True
					stem = word[-1*i+1:]						
					if len(stem) >= minimum_stem_length:
						if stem not in Protostems:
							Protostems[stem] = 1
						else:
							Protostems[stem] += 1
						#print previousword, word, stem
					previousword = word
					break
			if differencefoundflag:
				continue
			if len(previousword) > i + 1:
				previousword = word
				continue
			if (len(word)) >= i:
				if len(previousword) >= minimum_stem_length:
					if (previousword not in Protostems):
						Protostems[previousword] = 1
					else:
						Protostems[previousword] += 1
			previousword = word

#----------------------------------------------------------------------------------------------------------------------------#
def FindAffixes(Lexicon, Protostems,  FindSuffixesFlag):

	wordlist=Lexicon.WordList.mylist
	MinimumStemLength = Lexicon.MinimumStemLength
	MaximumAffixLength = Lexicon.MaximumAffixLength
	if FindSuffixesFlag:  
		for i in range(len(wordlist)):
			word = wordlist[i].Key
			WordAnalyzedFlag = False
			for i in range(len(word)-1 , MinimumStemLength-1, -1):
				stem = word[:i]
				if stem in Protostems:
					suffix = word[i:]
					if len(suffix) > MaximumAffixLength:
						continue
					if stem not in Lexicon.StemToWord:
						Lexicon.StemToWord[stem] = dict()
					Lexicon.StemToWord[stem][word]=1
					if stem not in Lexicon.StemToAffix:
						Lexicon.StemToAffix[stem] = dict()
					Lexicon.StemToAffix[stem][suffix] = 1 
					if stem in Lexicon.WordCounts:
						Lexicon.StemToWord[stem][word] = 1
						Lexicon.StemToAffix[stem]["NULL"] = 1
					Lexicon.Suffixes[suffix]=1	
 
 

	else:
		for i in range(len(wordlist)):
			word = wordlist[i].Key
			WordAnalyzedFlag = False
			for i in range(MinimumStemLength-1, len(word)-1):
				stem = word[-1*i:]
				if stem in Protostems:
					j = len(word) - i 
					prefix = word[:j]
 
					if len(prefix) > MaximumAffixLength:
						continue
					if stem not in Lexicon.StemToWord:
						Lexicon.StemToWord[stem] = dict()
					Lexicon.StemToWord[stem][word]=1	
					if stem not in Lexicon.StemToAffix:
						Lexicon.StemToAffix[stem] = dict()	
					Lexicon.StemToAffix[stem][prefix]=1		

					if stem in Lexicon.WordCounts:
							Lexicon.StemToWord[stem][word] = 1
 							Lexicon.StemToAffix[stem]["NULL"]=1
 					Lexicon.Prefixes[prefix]=1
 
# ----------------------------------------------------------------------------------------------------------------------------#
def	RebalanceSignatureBreaks2 (Lexicon, threshold, outfile, FindSuffixesFlag):
# this version is much faster, and does not recheck each signature; it only changes stems.
# ----------------------------------------------------------------------------------------------------------------------------#
	count=0
	MinimumNumberOfStemsInSignaturesCheckedForRebalancing = 5
 	SortedListOfSignatures = sorted(Lexicon.SignatureToStems.items(), lambda x, y: cmp(len(x[1]), len(y[1])),
									reverse=True)		 
	for (sig,wordlist) in SortedListOfSignatures:
		sigstring="-".join(sig)
		numberofstems=len(Lexicon.SignatureToStems[sig])
		 
		if numberofstems <MinimumNumberOfStemsInSignaturesCheckedForRebalancing: 				
			print >>outfile, "       Too few stems to shift material from suffixes", sigstring, numberofstems		
			continue
		print >>outfile, "{:20s} count: {:4d} ".format(sigstring,   numberofstems),

		shiftingchunk, shiftingchunkcount  = TestForCommonEdge(Lexicon.SignatureToStems[sig], outfile, threshold, FindSuffixesFlag) 

		if shiftingchunkcount > 0:
			#print "CC" ,sig, shiftingchunk
 			print >>outfile,"{:5s} count: {:5d}".format(shiftingchunk,   shiftingchunkcount)
 		else:
 			print >>outfile, "no chunk to shift"  
 
		if len(shiftingchunk) >0: 
			count +=1				 
			chunklength = len(shiftingchunk)
			newsignature = list()	
			sigstring2 = ""
			for affix in sig:
				if affix == "NULL":
					affix = ""
				if FindSuffixesFlag:
					newaffix = shiftingchunk + affix
					sigstring2 += newaffix + " - "
					shiftpair = (affix, newaffix)
					sigstring2 = sigstring2[:-2] ##????
				else:
					newaffix = affix + shiftingchunk
					sigstring2 += "-" + newaffix
					shiftpair = (affix, newaffix)
					sigstring2 = sigstring2[2:] ##???
				newsignature.append(newaffix)
			formatstring = "{:30s} {:10s} {:35s}  Number of stems {:5d} Number of shifters {:5d}"
			print >>outfile, formatstring.format(sigstring, shiftingchunk, sigstring2, numberofstems, shiftingchunkcount)
			 
			if shiftingchunkcount >= numberofstems * threshold  :
				ChangeFlag = True
				
				stems_to_change = list(Lexicon.SignatureToStems[sig])
				for stem in stems_to_change:
					if FindSuffixesFlag: 
						if stem[-1*chunklength:] != shiftingchunk:
							continue
					else:
						if stem[:chunklength] != shiftingchunk:
							continue
					if FindSuffixesFlag:					
						newstem = stem[:len(stem)-chunklength]
					else:
						newstem = stem[chunklength:]
 
 					if newstem not in Lexicon.StemToWord:
						Lexicon.StemToWord[newstem] = dict()
					for word in Lexicon.StemToWord[stem]:		 	
						Lexicon.StemToWord[newstem][word] = 1
					del Lexicon.StemToWord[stem] #  is this too general? 					
	 				
					if newstem not in Lexicon.StemToAffix:
						Lexicon.StemToAffix[newstem] = {}				
					for affix in newsignature:
						Lexicon.StemToAffix[newstem][affix] = 1
					del Lexicon.StemToAffix[stem]

					if newstem not in Lexicon.StemToSignature:
						Lexicon.StemToSignature[newstem]=dict()
					Lexicon.StemToSignature[newstem]=[newsignature]
					del Lexicon.StemToSignature[stem]
						
	outfile.flush()
	return count






# ----------------------------------------------------------------------------------------------------------------------------#
def RemakeSignatures(WordToSig, SignatureToStems, StemToWord, StemToAffix, StemToSig):
	# ----------------------------------------------------------------------------------------------------------------------------#
	return ""


# ----------------------------------------------------------------------------------------------------------------------------#
def StableSignature(stemlist,MakeSuffixesFlag):
	# ----------------------------------------------------------------------------------------------------------------------------#
	"""Determines if this signature is prima facie plausible, based on letter entropy.
	   If this value is above 1.5, then it is a stable signature: the number of different letters
	   that precede it is sufficiently great to have confidence in this morpheme break."""

	entropy = 0.0
	frequency = dict()
	templist = list()
	if MakeSuffixesFlag == False:
		for chunk in stemlist:
			templist.append(chunk[::-1])
		stemlist = templist		
	for stem in stemlist:
		lastletter = stem[-1]
		if lastletter not in frequency:
			frequency[lastletter] = 1.0
		else:
			frequency[lastletter] += 1.0
	for letter in frequency:
		frequency[letter] = frequency[letter] / len(stemlist)
		entropy += -1.0 * frequency[letter] * math.log(frequency[letter], 2)
	return entropy

 


# ----------------------------------------------------------------------------------------------------------------------------#
def TestForCommonEdge(stemlist, outfile,  threshold, FindSuffixesFlag):
# ----------------------------------------------------------------------------------------------------------------------------#
 	WinningString = ""
 	WinningCount = 0
	MaximumLengthToExplore = 6
	ExceptionCount = 0
	proportion = 0.0
	FinalLetterCount = {}
	NumberOfStems = len(stemlist) 
	WinningStringCount = dict() #key is string, value is number of stems
 	 
	for length in range(1,MaximumLengthToExplore):
		FinalLetterCount = dict()
		for stem in stemlist:		 	 
			if len(stem) < length + 2:
				continue
			if FindSuffixesFlag:
				commonstring = stem[-1*length:]
			else:
				commonstring= stem[:length]
			if not commonstring in FinalLetterCount.keys():
				FinalLetterCount[commonstring] = 1
			else:
				FinalLetterCount[commonstring] += 1
			#print stem,	 		
		
		sorteditems = sorted(FinalLetterCount, key=FinalLetterCount.get, reverse=True)  # sort by value
		CommonLastString = sorteditems[0]
		CommonLastStringCount = FinalLetterCount[CommonLastString]
		WinningStringCount[CommonLastString]=CommonLastStringCount
		
		#print >>outfile,  "    ", "\nA", length,  CommonLastString, CommonLastStringCount, "Number Of Stems" , NumberOfStems
		if  CommonLastStringCount >= threshold * NumberOfStems:
			Winner = CommonLastString
			WinningStringCount[Winner]=CommonLastStringCount
			#print  "A", " length" , length, "best string" ,   CommonLastString, CommonLastStringCount, "Number Of Stems" , NumberOfStems
			#print "    ", "B", length,  CommonLastString, CommonLastStringCount, "Number Of Stems" , NumberOfStems
			#print "\nB winner so far", Winner
			continue

		else:
			if length > 1:			 
				WinningString = Winner # from last iteration
				WinningCount = WinningStringCount[WinningString]
			else:
				WinningString = ""
				WinningCount = 0
			break
 		 
 		
	# ----------------------------------------------------------------------------------------------------------------------------#
	#print "\n\n", WinningString, WinningCount	
	return (WinningString, WinningCount )


# ----------------------------------------------------------------------------------------------------------------------------#


 

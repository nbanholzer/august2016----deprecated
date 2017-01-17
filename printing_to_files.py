import math 

def initialize_files(this_lexicon, this_file,singleton_signatures,doubleton_signatures, DisplayList ):
    if this_file == "console":
        print  "{:45s}{:10,d}".format("Number of words: ", len(this_lexicon.WordList.mylist))
        print  "{:45s}{:10,d}".format("Total letter count in words ", this_lexicon.TotalLetterCountInWords)
        print  "{:45s}{:10,d}".format("Number of signatures: ", len(DisplayList))
        print  "{:45s}{:10,d}".format("Number of singleton signatures: ", singleton_signatures)
        print  "{:45s}{:10,d}".format("Number of doubleton signatures: ", doubleton_signatures)
        print  "{:45s}{:10,d}".format("Total number of letters in stems: ", this_lexicon.LettersInStems)
        print  "{:45s}{:10,d}".format("Total number of affix letters: ", this_lexicon.AffixLettersInSignatures)
        print  "{:45s}{:10,d}".format("Total letters in signatures: ", this_lexicon.LettersInStems + this_lexicon.AffixLettersInSignatures)
        print  "{:45s}{:10,d}".format("Number of analyzed words ", this_lexicon.NumberOfAnalyzedWords)
        print  "{:45s}{:10,d}".format("Total number of letters in analyzed words ", this_lexicon.LettersInAnalyzedWords)
    else:
        print  >> this_file,  "{:45s}{:10,d}".format("Number of words: ", len(this_lexicon.WordList.mylist))
        print   >> this_file, "{:45s}{:10,d}".format("Total letter count in words ", this_lexicon.TotalLetterCountInWords)
        print   >> this_file, "{:45s}{:10,d}".format("Number of signatures: ", len(DisplayList))
        print   >> this_file, "{:45s}{:10,d}".format("Number of singleton signatures: ", singleton_signatures)
        print   >> this_file, "{:45s}{:10,d}".format("Number of doubleton signatures: ", doubleton_signatures)
        print   >> this_file, "{:45s}{:10,d}".format("Total number of letters in stems: ", this_lexicon.LettersInStems)
        print   >> this_file, "{:45s}{:10,d}".format("Total number of affix letters: ", this_lexicon.AffixLettersInSignatures)
        print   >> this_file, "{:45s}{:10,d}".format("Total letters in signatures: ", this_lexicon.LettersInStems + this_lexicon.AffixLettersInSignatures)
        print   >> this_file, "{:45s}{:10,d}".format("Number of analyzed words ", this_lexicon.NumberOfAnalyzedWords)
        print   >> this_file, "{:45s}{:10,d}".format("Total number of letters in analyzed words ", this_lexicon.LettersInAnalyzedWords)
 
def print_signature_list_1(this_file, DisplayList,stemcountcutoff, totalrobustness):
    print "  Printing signature file."
    runningsum = 0.0
    formatstring1 = '{0:<70}{1:>10s} {2:>15s} {3:>25s} {4:>20s} '
    formatstring2 = '{:<70}{:10d} {:15d} {:25.3%} {:20.3%}'
    print >> this_file, "\n" + "-" * 150
    print >> this_file, formatstring1.format("Signature", "Stem count", "Robustness", "Proportion of robustness", "Running sum")
    print >> this_file, "-" * 150      
    DisplayList = sorted(DisplayList, lambda x, y: cmp(x[2], y[2]), reverse=True)
     
    for sig, stemcount, robustness in DisplayList:
        runningsum+=robustness
        if stemcount < stemcountcutoff:
            break;
        else:
            robustnessproportion = float(robustness) / totalrobustness
            runningsumproportion = runningsum/totalrobustness
            print >> this_file, formatstring2.format(sig, stemcount, robustness,robustnessproportion, runningsumproportion )
        print >> this_file, "-"*60

def print_signature_list_2(this_file, DisplayList,stemcountcutoff, totalrobustness, SignatureToStems, StemCounts, suffix_flag):
    numberofstemsperline = 6
    stemlist = []
    reversedstemlist = []
    count = 0
    print >> this_file, "*** Stems in each signature"
    for sig, stemcount, robustness in DisplayList:
        #if encoding == "utf8":
        #        print >> this_file, "\n"+"="*45 , sig, "\n"
        #else:
        print >> this_file, "\n"+"="*45, '{0:30s} \n'.format(sig)
        n = 0

        stemlist =  SignatureToStems[sig].keys()
        stemlist.sort()
        numberofstems = len(stemlist)
        for stem in stemlist:
                n += 1
                print >> this_file, '{0:12s}'.format(stem),
                if n == numberofstemsperline:
                    n = 0
                    print >> this_file
        print >> this_file, "\n" + "-"*25
        # ------------------- New -----------------------------------------------------------------------------------
        howmany = 5     
        print >>this_file, "Average count of top",howmany, " stems:" , AverageCountOfTopStems(howmany, sig, SignatureToStems, StemCounts)
            

        # ------------------------------------------------------------------------------------------------------
        bitsPerLetter = 5
        wordlist = makeWordListFromSignature(sig, SignatureToStems[sig])
        (a, b, c) = findWordListInformationContent(wordlist, bitsPerLetter)
        (d, e, f) = findSignatureInformationContent(SignatureToStems, sig, bitsPerLetter)
        formatstring = '%35s %10d  '
        formatstringheader = '%35s %10s    %10s  %10s'
        print >> this_file, formatstringheader % ("", "Phono", "Ordering", "Total")
        print >> this_file, formatstring % ("Letters in words if unanalyzed:", a   )
        print >> this_file, formatstring % ("Letters as analyzed:", d)
        # ------------------------------------------------------------------------------------------------------
        howmanytopstems = 5
            


        print >> this_file, "\n-------------------------"
        print >> this_file, "Entropy-based stability: ", StableSignature(stemlist,suffix_flag)
        print >> this_file, "\n", "High frequency possible affixes \nNumber of stems: ", len(stemlist)
        formatstring = '%10s    weight: %5d count: %5d %2s'
        peripheralchunklist = find_N_highest_weight_affix(stemlist, suffix_flag)

        for item in peripheralchunklist:
            if item[2] >= numberofstems * 0.9:
                    flag = "**"
            else:
                    flag = ""
            print >> this_file, formatstring % (item[0], item[1], item[2], flag)
# ----------------------------------------------------------------------------------------------------------------------------#
def print_suffixes(outfile, Suffixes ):
        print >>outfile,  "--------------------------------------------------------------"
        print >>outfile , "        Suffixes "
        print >>outfile,  "--------------------------------------------------------------"
        print "  Printing suffixes."
        suffixlist = list(Suffixes.keys())
        suffixlist.sort(key=lambda  suffix:Suffixes[suffix], reverse=True)
        for suffix in suffixlist:
            print >>outfile,"{:8s}{:9,d}".format(suffix, Suffixes[suffix])
        return suffixlist
# ----------------------------------------------------------------------------------------------------------------------------#
def print_stems(outfile1, outfile2, StemToWord, StemToSignature, WordCounts, suffixlist): 
        stems = StemToWord.keys()
        stems.sort()
        print >> outfile1, "--------------------------------------------------------------"
        print >> outfile1, "---  Stems and their words"
        print >> outfile1, "--------------------------------------------------------------"
        print "  Printing stems and their words."
        StemCounts = dict()
        for stem in stems:
            print >> outfile1, '{:15}'.format(stem),
            wordlist = StemToWord[stem].keys()
            wordlist.sort()
            stemcount = 0
            for word in wordlist:
                stemcount +=  WordCounts[word]
            StemCounts[stem]=stemcount
            print    >> outfile1, '{:5d}'.format(stemcount),'; ',
            stemcount = float(stemcount)    
            for word in wordlist:
                wordcount =  WordCounts[word]
                print >> outfile1 , '{:15}{:4n} {:7.1%} '.format(word,wordcount, wordcount/stemcount),
            print >> outfile1 

            # We print a list of stems with their words (and frequencies) in which only those suffixes which are among the K most frequent suffixes,
            # in order to use visualization methods that put soft limits on the number of dimensions they can handle well.
            
            threshold_for_top_affixes = 11 # this will give us one more than that number, since we are zero-based counting.
            top_affixes = suffixlist[0:threshold_for_top_affixes]
        print >> outfile2, "\n--------------------------------------------------------------"
        print >> outfile2, "---  Stems and their words with high frequency affixes"
        print >> outfile2, "--------------------------------------------------------------"
        print "  Printing stems and their words, but only with high frequency affixes."
        print >>outfile2, "---\n--- Only signatures with these affixes: ", top_affixes
        print >>outfile2, "---"
        StemCounts = dict()
        for stem in stems:
            signature = StemToSignature[stem]
            for affix in signature:
                if affix not in top_affixes:
                    continue 
            print >> outfile2, '{:15}'.format(stem),
            wordlist = StemToWord[stem].keys()
            wordlist.sort()
            stemcount = 0
            for word in wordlist:
                stemcount += WordCounts[word]
            StemCounts[stem]=stemcount
            print    >> outfile2, '{:5d}'.format(stemcount),'; ',
            stemcount = float(stemcount)    
            for word in wordlist:
                wordcount = WordCounts[word]
                print >> outfile2, '{:15}{:4n} {:7.1%} '.format(word,wordcount, wordcount/stemcount),
            print >> outfile2        
            #print top_affixes

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
def find_N_highest_weight_affix(wordlist, suffix_flag):
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

	if suffix_flag:
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







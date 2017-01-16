import sys

# This is just part of documentation:
# A signature is a tuple of strings (each an affix).
# Signatures is a map: its keys are signatures.  Its values are *sets* of stems.
# StemToWord is a map; its keys are stems.       Its values are *sets* of words.
# StemToSig  is a map; its keys are stems.       Its values are individual signatures.
# WordToSig  is a Map. its keys are words.       Its values are *lists* of signatures.
# StemCounts is a map. Its keys are words.   Its values are corpus counts of stems.
# SignatureToStems is a dict: its keys are tuples of strings, and its values are dicts of stems.

class CWordList:
    def __init__(self):
        self.mylist = list()
       
    def GetCount(self):
        return len(self.mylist)
    def AddWord(self, word):
        self.mylist.append(Word(word))

    def at(self, n):
        return self.mylist[n]

    def sort(self):
        self.mylist.sort(key=lambda item: item.Key)
        # for item in self.mylist:
        #   print item.Key
        for i in range(len(self.mylist)):
            word = self.mylist[i]
            word.leftindex = i
        templist = list()
        for word in self.mylist:
            thispair = (word.Key[::-1], word.leftindex)
            templist.append(thispair)
        templist.sort(key=lambda item: item[0])
        for i in range(len(self.mylist)):
            (drow, leftindex) = templist[i]
            self.mylist[leftindex].rightindex = i
            
        #not currently used
    def PrintXY(self, outfile):
        Size = float(len(self.mylist))
        for word in self.mylist:
            x = word.leftindex / Size
            y = word.rightindex / Size
            print >> outfile, "{:20s}{8i} {:9.5} {:9.5}".format(word.Key, x, y)


## -------                                                      ------- #
##              Class Lexicon                                   ------- #
## -------                                                      ------- #
class CLexicon:
    def __init__(self):
        self.WordList = CWordList()
        self.WordCounts = dict()

        self.Signatures = {}
        self.SignatureToStems = {}
        self.WordToSig = {}
        self.StemToWord = {}
        self.StemToAffix = {}
        self.StemCounts = {}
        self.StemToSignature = {}
        self.Suffixes={}
        self.Prefixes = {}
        self.MinimumStemsInaSignature =2
        self.MinimumStemLength = 5
        self.MaximumAffixLength =3
        self.MaximumNumberOfAffixesInASignature = 10
        self.NumberOfAnalyzedWords = 0
        self.LettersInAnalyzedWords = 0
        self.NumberOfUnanalyzedWords = 0
        self.LettersInUnanalyzedWords = 0
        self.TotalLetterCountInWords = 0
        self.LettersInStems = 0
        self.AffixLettersInSignatures = 0
        self.TotalRobustInSignatures = 0


## -------                                                      ------- #
##              Central signature computation                   ------- #
## -------                                                      ------- #

# ----------------------------------------------------------------------------------------------------------------------------#
    def MakeSignatures(self, lxalogfile,outfile_Rebalancing_Signatures, FindSuffixesFlag, MinimumStemLength):
# ----------------------------------------------------------------------------------------------------------------------------#
        formatstring1 =  "  {:50s}{:>10,}"
        formatstring2 =  "  {:50s}"
        print formatstring2.format("The MakeSignatures function")

        # Protostems are candidate stems made during the algorithm, but not kept afterwards.
        Protostems = dict()
        self.NumberOfAnalyzedWords      = 0
        self.LettersInAnalyzedWords     = 0
        self.NumberOfUnanalyzedWords    = 0
        self.LettersInUnanalyzedWords   = 0
    
        AnalyzedWords = dict()
        #Lexicon.TotalLetterCountInWords = 0

        self.TotalRobustnessInSignatures            = 0
        self.LettersInStems                         = 0
        self.TotalLetterCostOfAffixesInSignatures   = 0
    
        # 1 -------
        self.FindProtostems(self.WordList.mylist, Protostems, self.MinimumStemLength, FindSuffixesFlag)
        print formatstring1.format("1a. Finished finding proto-stems.", len(Protostems)) 

        self.FindAffixes( Protostems,  FindSuffixesFlag)
        print formatstring1.format("1b. Finished finding affixes for protostems.", len(self.Suffixes)+ len(self.Prefixes))  
         
        # 2 It is possible for a stem to have only one affix at this point. We must eliminate those analyses.  -------
        ListOfStemsToRemove = list()
        for stem in self.StemToAffix:
            if len(self.StemToAffix[stem]) < 2:
                ListOfStemsToRemove.append(stem)
        print formatstring1.format("2. Number of stems to remove due to mono-fixivity:", len(ListOfStemsToRemove))     

        for stem in ListOfStemsToRemove:
            del self.StemToWord[stem]
            del self.StemToAffix[stem]
             
        # 3  Execute Stems-to-signatures. This is in a sense the most important step.        -------
        
        self.LettersInStems                         =0
        self.TotalLetterCostOfAffixesInSignatures   =0
        self.StemsToSignatures(FindSuffixesFlag)

        print  formatstring1.format("3. Finished first pass of finding stems, affixes, and signatures.", len(self.SignatureToStems))  
              
        # 4 Rebalancing now, which means:                  -------
        # We look for a stem-final sequence that appears on all or almost all the stems, and shift it to affixes.
        # Make changes in Lexicon.SignatureToStems, and .StemToSig, and .WordToSig, and .StemToWord, and .StemToAffix  and signature_tuples....
        threshold = 0.80
        count = self.RebalanceSignatureBreaks2 (threshold, outfile_Rebalancing_Signatures, FindSuffixesFlag) 
        print formatstring1.format("4. Find signature structure function.",count) 
        if True:
            if FindSuffixesFlag:
                Affixes = self.Suffixes
            else:
                Affixes = self.Prefixes
            self.FindSignatureStructure (FindSuffixesFlag, lxalogfile, Affixes, affix_threshold=3)
         

        # 5  ------- compute robustness
        self.ComputeRobustness()
        print  formatstring2.format("5. Computed robustness")  

        #8  ------- Print
        print >> lxalogfile, "{:40s}{:10,d}".format("Number of analyzed words", self.NumberOfAnalyzedWords)
        print >> lxalogfile, "{:40s}{:10,d}".format("Number of unanalyzed words", self.NumberOfUnanalyzedWords)
        print >> lxalogfile, "{:40s}{:10,d}".format("Letters in stems", self.LettersInStems)
        print >> lxalogfile, "{:40s}{:10,d}".format("Letters in affixes", self.AffixLettersInSignatures)
        print >> lxalogfile, "{:40s}{:10,d}".format("Total robustness in signatures", self.TotalRobustnessInSignatures)
    
        return

# ----------------------------------------------------------------------------------------------------------------------------#
    def FindSignatureStructure (self, FindSuffixesFlag, outfile, Affixes = None, affix_threshold = 1):

    # This function assumes that we have the set of stems already in Lexicon.SignatureToStems. It does the rest.

            StemList = self.StemToWord.keys()
            self.StemToSig = {}
            self.StemToAffix = {}# ok
            self.StemToWord = dict()# ok
            self.Signatures = {}
            self.SignatureToStems = {}
            self.WordToSig = {}
            self.StemCounts = {}

            #  Signatures with way too many affixes are spurious.
            # If we have already run this function before, we have a set of affixes ranked by frequency,
            # and we can use these now to eliminate low frequency suffixes from signatures with
            # just one affix. 
            # Lexicon.MaximumNumberOfAffixesInASignature
            # Number of affixes we are confident in:
            formatstring1 =  "       {:50s}{:>10,}"
            formatstring2 =  "       {:50s}"
            print formatstring2.format("Inside Find_Signature_Structure.")
            print formatstring2.format("i. Finding affixes we are confident about.")
            number_of_affixes_per_line = 10

            # -----------------------------------------------------------------#
            # Block 1. This block defines affixes, confident affixes, and signatures.
            # -----------------------------------------------------------------#            
            if len (Affixes ) ==0:
                if FindSuffixesFlag:
                    print "No suffixes found yet."
                else:
                    print "No prefixes found yet." 
            else:
                ConfidentAffixes = dict()
                NumberOfConfidentAffixes = 50
                NumberOfAffixes = len(Affixes.keys())
                if NumberOfConfidentAffixes > NumberOfAffixes:
                    NumberOfConfidentAffixes = NumberOfAffixes          
                SortedAffixes = list(Affixes.keys())
                SortedAffixes.sort(key=lambda affix:Affixes[affix], reverse=True)
                
                print "\n       Top ", NumberOfConfidentAffixes, "affixes retained for use now (out of", len(SortedAffixes),")."
                count = 0
                print "      ",
                for affixno in range(NumberOfConfidentAffixes):
                    ConfidentAffixes[SortedAffixes[affixno]]=1
                    print  "{:6s} ".format(SortedAffixes[affixno]),
                    count += 1
                    if count % number_of_affixes_per_line == 0:
                        print 
                        print "      ",
                for sig in self.SignatureToStems:
                    stems = self.SignatureToStems[sig]
                    newsig = list()
                    if len(stems) == 1:         
                        for affix in sig:
                            if affix in ConfidentAffixes:
                                newsig.append(affix)
                print 

            #-----------------------------------------------------------------#
            # Block 2: This block loops through all words
            # -----------------------------------------------------------------#              
             
            # Creates Lexicon.StemToWord, Lexicon.StemToAffix. 
            print 
            print formatstring2.format("ii. Reanalyzing words, finding both stems and affixes.")
            if True:
                print "                 Word number:",
                for i in range(len(self.WordList.mylist)):          
                    if i % 2500 == 0:
                        print "{:7,d}".format(i),           
                        sys.stdout.flush()
                    word = self.WordList.mylist[i].Key
                    WordAnalyzedFlag = False
                    for i in range(len(word)-1 , self.MinimumStemLength-1, -1):   # loop on positions in the word, left to right
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
                            if len(affix) > self.MaximumAffixLength:
                                continue
                            # the next line involves putting a threshold on frequencies of affixes.
                            if Affixes and affix in Affixes and Affixes[affix] < affix_threshold:
                                continue                        
                            #print stem, suffix          
                            if stem not in self.StemToWord:
                                self.StemToWord[stem] = dict()
                            self.StemToWord[stem][word]=1
                            if stem not in self.StemToAffix:
                                self.StemToAffix[stem] = dict()
                            self.StemToAffix[stem][affix] = 1 
                            if stem in self.WordCounts: # this is for the case where the stem is a free-standing word also                               
                                self.StemToWord[stem][word] = 1
                                self.StemToAffix[stem]["NULL"] = 1
                            if stem not in self.StemCounts:
                                self.StemCounts[stem] = 0
                            self.StemCounts[stem]+= self.WordCounts[word]
                     
            print 
            self.LettersInStems =0
            self.TotalLetterCostOfAffixesInSignatures =0         



            if (False):
                for stem in self.StemToAffix:
                    if len(StemToAffix[stem]) > self.MaximumNumberOfAffixesInASignature: 
                        for sig in self.SignatureToStems:
                            stems = self.SignatureToStems[sig]
                            newsig = list()
                            if len(stems) == 1:         
                                for affix in sig:
                                    if affix in ConfidentAffixes:
                                        newsig.append(affix)
                     


            print "       iii. Finding an initial set of signatures."

            StemsToEliminate = list()
            for stem in self.StemToWord:
                self.LettersInStems += len(stem)
                signature = list(self.StemToAffix[stem])
                signature.sort()
                signature_tuple = tuple(signature)
                if len(signature) == 1:
                    StemsToEliminate.append(stem)
                    continue
                if signature_tuple not in self.SignatureToStems:
                    self.SignatureToStems[signature_tuple] = dict()
                    for affix in signature:
                        self.TotalLetterCostOfAffixesInSignatures += len(affix)
                        if affix not in Affixes:
                            Affixes[affix]=1
                        else:
                            Affixes[affix] +=1
                self.SignatureToStems[signature_tuple][stem] = 1

                self.StemToSig[stem] = signature_tuple
                for word in self.StemToWord[stem]:
                    if word not in self.WordToSig:
                        self.WordToSig[word] = list()
                    self.WordToSig[word].append(signature_tuple)
                    self.LettersInAnalyzedWords += len(word)

            for stem in StemsToEliminate:
                del self.StemToAffix[stem]
                del self.StemToWord[stem]

            print formatstring1.format("iv. Signatures.", len(self.SignatureToStems)) 
            print formatstring2.format("v. Finished redoing structure")
            print >>outfile, formatstring2.format("v. Finished redoing structure\n")
            print >>outfile, "Number of sigs: ", len(self.SignatureToStems)
                     
             




#-----------------------------------------------------------------------------------------------------------------------------#
    def FindProtostems(self, wordlist, Protostems,minimum_stem_length,FindSuffixesFlag):
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
    def FindAffixes(self, Protostems,  FindSuffixesFlag):

        wordlist=self.WordList.mylist
        MinimumStemLength = self.MinimumStemLength
        MaximumAffixLength = self.MaximumAffixLength
        if FindSuffixesFlag:  
            for i in range(len(wordlist)):
                word = wordlist[i].Key
                WordAnalyzedFlag = False
                #print (word)
                for i in range(len(word)-1 , MinimumStemLength-1, -1):
                    stem = word[:i]
                    if stem in Protostems:
                        suffix = word[i:]
                        if len(suffix) > MaximumAffixLength:
                            continue
                        if stem not in self.StemToWord:
                                self.StemToWord[stem] = dict()
                        self.StemToWord[stem][word]=1
                        if stem not in self.StemToAffix:
                            self.StemToAffix[stem] = dict()
                            self.StemToAffix[stem][suffix] = 1 
                        if stem in self.WordCounts:
                            self.StemToWord[stem][word] = 1
                            self.StemToAffix[stem]["NULL"] = 1
                            self.Suffixes[suffix]=1 
         
         

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
                            if stem not in self.StemToWord:
                                self.StemToWord[stem] = dict()
                            self.StemToWord[stem][word]=1   
                            if stem not in self.StemToAffix:
                                self.StemToAffix[stem] = dict() 
                            self.StemToAffix[stem][prefix]=1        
                            if stem in self.WordCounts:
                                    self.StemToWord[stem][word] = 1
                                    self.StemToAffix[stem]["NULL"]=1
                            self.Prefixes[prefix]=1
         
# ----------------------------------------------------------------------------------------------------------------------------#
    def RebalanceSignatureBreaks2 (self, threshold, outfile, FindSuffixesFlag):
# this version is much faster, and does not recheck each signature; it only changes stems.
# ----------------------------------------------------------------------------------------------------------------------------#
            count=0
            MinimumNumberOfStemsInSignaturesCheckedForRebalancing = 5
            SortedListOfSignatures = sorted(self.SignatureToStems.items(), lambda x, y: cmp(len(x[1]), len(y[1])),
                                            reverse=True)        
            for (sig,wordlist) in SortedListOfSignatures:
                sigstring="-".join(sig)
                numberofstems=len(self.SignatureToStems[sig])
                 
                if numberofstems <MinimumNumberOfStemsInSignaturesCheckedForRebalancing:                
                    print >>outfile, "       Too few stems to shift material from suffixes", sigstring, numberofstems       
                    continue
                print >>outfile, "{:20s} count: {:4d} ".format(sigstring,   numberofstems),

                shiftingchunk, shiftingchunkcount  = TestForCommonEdge(self.SignatureToStems[sig], outfile, threshold, FindSuffixesFlag) 

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
                
                        stems_to_change = list(self.SignatureToStems[sig])
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
         
                            if newstem not in self.StemToWord:
                                self.StemToWord[newstem] = dict()
                            for word in self.StemToWord[stem]:          
                                self.StemToWord[newstem][word] = 1
                            del self.StemToWord[stem] #  is this too general?                   
                            
                            if newstem not in self.StemToAffix:
                                self.StemToAffix[newstem] = {}              
                            for affix in newsignature:
                                self.StemToAffix[newstem][affix] = 1
                            del self.StemToAffix[stem]

                            if newstem not in self.StemToSignature:
                                self.StemToSignature[newstem]=dict()
                            self.StemToSignature[newstem]=[newsignature]
                            del self.StemToSignature[stem]
                        
            outfile.flush()
            return count



#--------------------------------------------------------------------------------------------------------------------------#
    def printSignatures(self, lxalogfile, outfile_signatures, outfile_wordstosigs, outfile_stemtowords, outfile_stemtowords2, outfile_SigExtensions, outfile_suffixes, encoding,
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
        print   >> outfile_signatures, "{:45s}{:10,d}".format("Total letter count in words ", Lexicon.TotalLetterCountInWords)
        print   >> outfile_signatures, "{:45s}{:10,d}".format("Number of signatures: ", len(DisplayList))
        print   >> outfile_signatures, "{:45s}{:10,d}".format("Number of singleton signatures: ", singleton_signatures)
        print   >> outfile_signatures, "{:45s}{:10,d}".format("Number of doubleton signatures: ", doubleton_signatures)
        print   >> outfile_signatures, "{:45s}{:10,d}".format("Total number of letters in stems: ", Lexicon.LettersInStems)
        print   >> outfile_signatures, "{:45s}{:10,d}".format("Total number of affix letters: ", Lexicon.AffixLettersInSignatures)
        print   >> outfile_signatures, "{:45s}{:10,d}".format("Total letters in signatures: ", Lexicon.LettersInStems + Lexicon.AffixLettersInSignatures)
        print   >> outfile_signatures, "{:45s}{:10,d}".format("Number of analyzed words ", Lexicon.NumberOfAnalyzedWords)
        print   >> outfile_signatures, "{:45s}{:10,d}".format("Total number of letters in analyzed words ", Lexicon.LettersInAnalyzedWords)
    #   print   >> outfile_signatures, "{:45s}{:10.2f}".format("Compression ", (Lexicon.LettersInAnalyzedWords - Lexicon.LettersInStems - Lexicon.AffixLettersInSignatures)/ float(Lexicon.LettersInAnalyzedWords))
        print


        
     

        print  >>lxalogfile,  "{:45s}{:10,d}".format("Number of words: ", len(Lexicon.WordList.mylist))
        print  >>lxalogfile, "{:45s}{:10,d}".format("Total letter count in words ", Lexicon.TotalLetterCountInWords)
        print  >>lxalogfile, "{:45s}{:10,d}".format("Number of signatures: ", len(DisplayList))
        print  >>lxalogfile,    "{:45s}{:10,d}".format("Number of singleton signatures: ", singleton_signatures)
        print  >>lxalogfile,    "{:45s}{:10,d}".format("Number of doubleton signatures: ", doubleton_signatures)
        print  >>lxalogfile,    "{:45s}{:10,d}".format("Total number of letters in stems: ", Lexicon.LettersInStems)
        print  >>lxalogfile,    "{:45s}{:10,d}".format("Total number of affix letters: ", Lexicon.AffixLettersInSignatures)
        print  >>lxalogfile,    "{:45s}{:10,d}".format("Total letters in signatures: ", Lexicon.LettersInStems + Lexicon.AffixLettersInSignatures)
        print  >>lxalogfile,    "{:45s}{:10,d}".format("Number of analyzed words ", Lexicon.NumberOfAnalyzedWords)
        print  >>lxalogfile,    "{:45s}{:10,d}".format("Total number of letters in analyzed words ", Lexicon.LettersInAnalyzedWords)
    #   print  >>lxalogfile, "{:45s}{:10.2f}".format("Compression ", (Lexicon.LettersInAnalyzedWords - Lexicon.LettersInStems - Lexicon.AffixLettersInSignatures)/ float(Lexicon.LettersInAnalyzedWords))
        print



        print   "  {:45s}{:10,d}".format("Number of words: ", len(Lexicon.WordList.mylist))
        print   "  {:45s}{:10,d}".format("Total letter count in words ", Lexicon.TotalLetterCountInWords)
        print   "  {:45s}{:10,d}".format("Number of signatures: ", len(DisplayList))
        print   "  {:45s}{:10,d}".format("Number of singleton signatures: ", singleton_signatures)
        print   "  {:45s}{:10,d}".format("Number of doubleton signatures: ", doubleton_signatures)
        print   "  {:45s}{:10,d}".format("Total number of letters in stems: ", Lexicon.LettersInStems)
        print   "  {:45s}{:10,d}".format("Total number of affix letters: ", Lexicon.AffixLettersInSignatures)
        print   "  {:45s}{:10,d}".format("Total letters in signatures: ", Lexicon.LettersInStems + Lexicon.AffixLettersInSignatures)
        print   "  {:45s}{:10,d}".format("Number of analyzed words ", Lexicon.NumberOfAnalyzedWords)
        print   "  {:45s}{:10,d}".format("Total number of letters in analyzed words ", Lexicon.LettersInAnalyzedWords)
    #   print   "  {:45s}{:10.2f}".format("Compression ", (Lexicon.LettersInAnalyzedWords - Lexicon.LettersInStems - Lexicon.AffixLettersInSignatures)/ float(Lexicon.LettersInAnalyzedWords))
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
            print >> outfile_signatures, '{0:<70}{1:>10s} {2:>15s} {3:>25s} {4:>20s} '.format("Signature", "Stem count", "Robustness", "Proportion of robustness",    "Running sum")
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
                    print                "{:4d}{:10,d}".format(i, ambiguity_counts[i])
     

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
            print    >> outfile_stemtowords, '{:5d}'.format(stemcount),'; ',
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
            print    >> outfile_stemtowords2, '{:5d}'.format(stemcount),'; ',
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









## -------                                                      ------- #
##              Utility functions                               ------- #
## -------                                                      ------- #
    def PrintWordCounts(self, outfile):
            formatstring = "{:20s} {:6d}"
            words = self.WordCounts.keys()
            words.sort()
            for word in words:
                    print >>outfile, formatstring.format(word, self.WordCounts[word])

    def Multinomial(self,this_signature,FindSuffixesFlag):
        counts = dict()
        total = 0.0
        #print "{:45s}".format(this_signature), 
        for affix in this_signature:
            #print "affix", affix            
            counts[affix]=0
            for stem in self.SignatureToStems[this_signature]:      
                #print "stem", stem  
                if affix == "NULL":
                    word = stem
                elif FindSuffixesFlag:
                    word = stem + affix
                else:
                    word= affix + stem
            #print stem,":", affix, "::", word
            #print "A", counts[affix], self.WordCounts[word]
            counts[affix] += self.WordCounts[word]
            total += self.WordCounts[word]
        frequency = dict()
        for affix in this_signature:
            frequency[affix] = counts[affix]/total
            #print "{:12s}{:10.2f}   ".format(affix, frequency[affix]),
        #print 

    def ComputeRobustness(self): 
        self.NumberOfAnalyzedWords= len(self.WordToSig)
        self.NumberOfUnanalyzedWords= self.WordList.GetCount() - self.NumberOfAnalyzedWords  
        for sig in self.SignatureToStems:
            numberofaffixes = len(sig)
            mystems = self.SignatureToStems[sig]
            numberofstems = len(mystems)
            AffixListLetterLength = 0
            for affix in sig:
                if affix == "NULL":
                        continue
                AffixListLetterLength += len(affix)
            StemListLetterLength = 0
            for stem in mystems:
                StemListLetterLength += len(stem)

            self.TotalRobustnessInSignatures +=  getrobustness(mystems,sig)
            self.AffixLettersInSignatures += AffixListLetterLength
    
    def StemsToSignatures(self,FindSuffixesFlag):
        if FindSuffixesFlag:
            Affixes = self.Suffixes
        else:
            Affixes = self.Prefixes

        #  Iterate through each stem, get its affixes and count them, and create signatures. 
        for stem in self.StemToWord:
            self.LettersInStems += len(stem)
            signature = list(self.StemToAffix[stem])
            signature.sort()
            signature_tuple = tuple(signature)
            for affix in signature:
                if affix not in Affixes:
                    Affixes[affix] = 0
                Affixes[affix] += 1
            if signature_tuple not in self.SignatureToStems:
                self.SignatureToStems[signature_tuple] = dict()
                for affix in signature:
                    self.TotalLetterCostOfAffixesInSignatures += len(affix)
            self.SignatureToStems[signature_tuple][stem] = 1
            self.StemToSignature[stem] = signature_tuple
            for word in self.StemToWord[stem]:
                if word not in self.WordToSig:
                    self.WordToSig[word] = list()
                self.WordToSig[word].append(signature_tuple)
        for sig in self.SignatureToStems:           
            if len(self.SignatureToStems[sig]) < self.MinimumStemsInaSignature:
                for stem in self.SignatureToStems[sig]:
                    del self.StemToSignature[stem]
                    for word in self.StemToWord[stem]:
                        if len( self.WordToSig[word] ) == 1:                     
                            del self.WordToSig[word]
                        else:
                            self.WordToSig[word].remove(sig)
                    del self.StemToWord[stem]

class Word:
    def __init__(self, key):
        self.Key = key
        self.leftindex = -1
        self.rightindex = -1

def makeword(stem, affix, sideflag):
    if sideflag == True:
        return stem + affix
    else: 
        return affix + stem

def byWordKey(word):
    return word.Key


class CSignature:
    count = 0

    def __init__(self):
        self.Index = 0
        self.Affixes = tuple()
        self.StartStateIndex = CSignature.count
        self.MiddleStateIndex = CSignature.Count + 1
        self.EndStateIndex = CSignature.count + 2
        CSignature.count += 3
        self.StemCount = 1

    def Display(self):
        returnstring = ""
        affixes = list(self.Affixes)
        affixes.sort()
        return "-".join(affixes)

        # ------------------------------------------------------------------------------------------##------------------------------------------------------------------------------------------#


class parseChunk:
    def __init__(self, thismorph, rString, thisedge=None):
        # print "in parsechunk constructor, with ", thismorph, "being passed in "
        self.morph = thismorph
        self.edge = thisedge
        self.remainingString = rString
        if (self.edge):
            self.fromState = self.edge.fromState
            self.toState = self.edge.toState
        else:
            self.fromState = None
            self.toState = None
            # print self.morph, "that's the morph"
            # print self.remainingString, "that's the remainder"

    def Copy(self, otherChunk):
        self.morph = otherChunk.morph
        self.edge = otherChunk.edge
        self.remainingString = otherChunk.remainingString

    def Print(self):
        returnstring = "morph: " + self.morph
        if self.remainingString == "":
            returnstring += ", no remaining string",
        else:
            returnstring += "remaining string is " + self.remainingString
        if self.edge:
            return "-(" + str(self.fromState.index) + ")" + self.morph + "(" + str(
                self.toState.index) + ") -" + "remains:" + returnstring
        else:
            return returnstring + "!" + self.morph + "no edge on this parsechunk"


            # ----------------------------------------------------------------------------------------------------------------------------#


class ParseChain:
    def __init__(self):
        self.my_chain = list()

    def Copy(self, other):
        for parsechunk in other.my_chain:
            newparsechunk = parseChunk(parsechunk.morph, parsechunk.remainingString, parsechunk.edge)
            self.my_chain.append(newparsechunk)

    def Append(self, parseChunk):
        # print "Inside ParseChain Append"
        self.my_chain.append(parseChunk)

    def Print(self, outfile):
        returnstring = ""
        columnwidth = 30
        for i in range(len(self.my_chain)):
            chunk = self.my_chain[i]
            this_string = chunk.morph + "-"
            if chunk.edge:
                this_string += str(chunk.edge.toState.index) + "-"
            returnstring += this_string + " " * (columnwidth - len(this_string))
        print >> outfile, returnstring,
        print >> outfile

    def Display(self):
        returnstring = ""
        for i in range(len(self.my_chain)):
            chunk = self.my_chain[i]
            returnstring += chunk.morph + "-"
            if chunk.edge:
                returnstring += str(chunk.edge.toState.index) + "-"
        return returnstring

        # ----------------------------------------------------------------------------------------------------------------------------#
class CAlternation:
    def __init__(self, stemcount = 0):
        self.Alloforms = list() # list of CAlloforms
        self.Count = stemcount
        
    def AddAlloform(self, this_alloform):
            self.Alloforms.append(this_alloform)

    def MakeProseReportLine(self):
        ReportLine = CProseReportLine()


        return ReportLine.MakeReport( )


    def display(self):
        this_datagroup = CDataGroup("KeyAndList",self.Count)         
        for i in range(len(self.Alloforms)):
            alloform = self.Alloforms[i]
            this_datagroup.Count = self.Count
            if alloform.Form ==  "":
                key = "nil" 
            else:
                key = alloform.Form
            if key not in this_datagroup.MyKeyDict:
                this_datagroup.MyKeyDict[key]=list()
            this_datagroup.MyKeyDict[key].append(alloform.Context)
         
        return this_datagroup.display()

 #       for i in range(len(self.Alloforms)):
 #         

#            return_string = ""
#            alloform = self.Alloforms[i]
#            if alloform.Form ==  "":
#                key = "nil" 
#            else:
#                key = alloform.Form
#            this_datagroup.MyListOfKeys.append(key)
#            this_datagroup.MyKeyDict[key]##

#            return_string += key
#            return_string += " in context: "
#            return_string += alloform.Context
            
#            return_list.append(return_string) 
#        return return_list

    def prose_statement(self):
        alloform_dict=dict()
        alloform_list=list()
        elsewhere_case=None
        for alloform in self.Alloforms:
            print "G",   alloform.Form, alloform.Context
            key = alloform.Form
            if key not in alloform_dict:
                alloform_dict[key] = list()
            alloform_dict[key].append(alloform)
            if alloform.Context == "NULL":
                elsewherecase_form = alloform.Form
        number_of_alloforms= len(alloform_dict)

        for item in alloform_dict:
            temp_alloform = CAlloform(item, "", 0)
            alloform_list.append(alloform_dict[item])
            print "W", item, alloform_dict[item]
            for subitem in item:
                temp_alloform.Context += " "+subitem.Context


        return_string = ""
        for alloform_no in range(number_of_alloforms):
            thisreportline = CReportLine()

            #alloform_list[alloform_no] is a  list of alloforms, all with the same Key
            key = alloform_list[alloform_no][0].Key # take the Key from the first one, because they are all the same

            context_list = list()
            for n in range(len(alloform_list[alloform_no])):

                context_list.append(alloform_list[alloform_no].context)  
            return_string += key + ":".join(context_list)    
        return return_string            

class CAlloform:
    def __init__(self,form, context, stemcount):
        self.Form = form
        self.Context = context
        self.StemCount = stemcount

class CProseReportLine:
    def __init__(self):
        self.MyList = list()
        self.MyLastItem = None

    def MakeReport(self):
        returnstring="hello!"
        for item in self.MyList:
            returnstring += item.MyHead
            for item2 in self.MyTail:
                returnstring += " " + item2
        if self.MyLastItem:
            returnstring += item.MyHead
            for item2 in self.MyTail:
                returnstring += " " + item2  
        return returnstring         


class CReportLineItem:
    def __init__(self):        
        self.MyHead = NULL
        self.MyTail = NULL

class CDataGroup:
    def __init__(self, type,count):
        self.Type = type
        self.MyKeyDict = dict()
        self.Count = count


    def display(self):
        colwidth1 = 20
        colwidth2 = 40
        countstring = str(self.Count)
        returnstring = countstring + " "*(4-len(countstring))
        string1 = ""
        string2 =""

        ItemList = list(self.MyKeyDict.keys())
        #if there is a word-finally, put it in last place


        for i in range(len(ItemList)):
            phone = ItemList[i]
            if "\#" in self.MyKeyDict[phone]:
                #word final phoneme
                word_final_phone = ItemList[i]
                del ItemList[i]
                ItemList.append(word_final_phone)
        #if there is a "NIL", then put it in first place.
        for i in range(len(ItemList)):
            phone=ItemList[i]
            if phone== "nil":
                del ItemList[i]
                ItemList.insert(0,"nil")



        if self.Type == "KeyAndList":
            for key in ItemList:
                NULL_flag = False
                string1 = "[" + key + "]" 
                string2 = ""
                returnstring += string1 + " "*(colwidth1-len(string1))
               
                FirstItemFlag= True
                for item in self.MyKeyDict[key]:
                    if item == "NULL":
                        NULL_flag = True
                        continue
                    if FirstItemFlag:
                        string2 += "before " 
                        FirstItemFlag = False
                    string2 += "/"+item + "/ "
                if NULL_flag:
                    if FirstItemFlag == False:
                        string2 += "and word-finally."
                    else:
                        string2 += "word-finally."
                returnstring += string2 + " "*(colwidth2- len(string2))

                     
             
        return returnstring



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


 











#
def getrobustness(sig, stems):
    # ----------------------------------------------------------------------------------------------------------------------------#
    countofsig = len(sig)
    countofstems = len(stems)
    lettersinstems = 0
    lettersinaffixes = 0
    for stem in stems:
        lettersinstems += len(stem)
    for affix in sig:
        lettersinaffixes += len(affix)
    # ----------------------------------------------------------------------------------------------------------------------------#
    return lettersinstems * (countofsig - 1) + lettersinaffixes * (countofstems - 1)


# ----------------------------------------------------------------------------------------------------------------------------#


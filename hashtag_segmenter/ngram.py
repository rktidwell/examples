#----------------------------
# Copyright 2014 Ryan Tidwell
#----------------------------

from decimal import *
import math

class BigramCorpus(object):

    corpus = None
    total_bigram_count = None
    vocab_size = None

    def __init__(self):
        self.corpus = {}
        self.total_bigram_count = float(0)
        self.vocab_size = float(0)

    def add_bigram(self, ugram1, ugram2, count):
        new_bigram_entry = ((ugram1,ugram2), float(count))
        ugram1_tuple = self.corpus.get(ugram1, None)
        
        if ugram1_tuple is None:
            ugram1_tuple = ()
            ugram1_dict = {}
            self.add_ugram2_entry(ugram2, new_bigram_entry, ugram1_dict)
            ugram1_tuple = (ugram1_dict, float(count))
        else:
            ugram1_dict = ugram1_tuple[0]
            bigram_entry = ugram1_dict.get(ugram2, None)
            if bigram_entry is not None:
                curr_count = float(bigram_entry[1])
                tmp_tuple = (bigram_entry[0], curr_count+float(count))
                new_bigram_entry = tmp_tuple
            else:
                self.vocab_size += 1
            self.add_ugram2_entry(ugram2, new_bigram_entry, ugram1_dict)

        curr_count = ugram1_tuple[1]
        new_ugram1_tuple = (ugram1_tuple[0], curr_count+count)
        self.add_ugram1_entry(ugram1, new_ugram1_tuple, self.corpus)
        self.total_bigram_count += count

    def add_ugram1_entry(self, ugram1, ugram1_tuple, corpus_dict):
        corpus_dict[ugram1] = ugram1_tuple

    def add_ugram2_entry(self, ugram2, bigram_entry, ugram1_dict):
        ugram1_dict[ugram2] = bigram_entry

    def get_bigram_entry(self, ugram1, ugram2):
        bigram_entry = None
        ugram1_tuple = self.corpus.get(ugram1, None)
        if ugram1_tuple is not None:
            bigram_entry = ugram1_tuple[0].get(ugram2, None)
        return bigram_entry

    def score_bigram(self, ugram1, ugram2):
        score = None
        denom = self.total_bigram_count
        bigram = self.get_bigram_entry(ugram1, ugram2)
        ugram_tuple = self.corpus.get(ugram1, None)
        if bigram is None:
            return score
            #bigram = ((ugram1,ugram2), float(0))
        bigram_prob = bigram[1]/denom
        score = math.log(bigram_prob)
        return score

class UnigramCorpus(object):

    ugrams = None
    total = None

    def __init__(self):
        self.ugrams = {}
        self.total = long(0)

    def add(self, ugram, count):
        tuple = self.get_ugram_tuple(ugram)
        if tuple is None:
            tuple = (ugram, long(0))
        tmp = (ugram, count+tuple[1])
        self.ugrams[ugram] = tmp
        self.total += count

    def get_ugram_tuple(self, ugram):
        return self.ugrams.get(ugram, None)

    def get_unigram_prob(self, ugram):
        tuple = self.ugrams.get(ugram, None)
        if tuple is None:
            tuple = (ugram, long(0))
        return float(tuple[1]+1)/float(self.total+len(self.ugrams))

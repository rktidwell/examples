#!/usr/bin/env python
#----------------------------
# Copyright 2014 Ryan Tidwell
#----------------------------


import os
import string
import sys
from tree import *
from ngram import *
import math
from decimal import *
import re

single_char_ugrams = ["a","i","x","y","1","2","3","4","5","6","7","8","9","0"]

def load_ugrams_and_bigram_corpus(ugram_dict, bigram_corpus, bigrams_file_path, ugrams_file_corpus):
    f = open(ugrams_file_corpus)
    for line in f:
        tmp = string.split(line.lower())
        if len(tmp[0]) > 1 or tmp[0] in single_char_ugrams:
            ugram_dict.add(tmp[0], long(tmp[1]))
    f.close()

    f = open(bigrams_file_path)
    for line in f:
        tmp = string.split(line.lower())
        if len(tmp[0]) == 1:
            continue
        if len(tmp[1]) == 1:
            continue
        ugram_dict.add(tmp[0], long(tmp[2]))
        ugram_dict.add(tmp[1], long(tmp[2]))
        bigram_corpus.add_bigram(tmp[0], tmp[1], long(tmp[2]))
    f.close()

def get_segmentation_tree(hashtag, unigrams):
    root = TreeNode(hashtag)
    load_child_nodes(hashtag, unigrams, root)
    return root

def load_child_nodes(hashtag, unigrams, root):
    range_end = len(hashtag)+1
    for i in range(1,range_end):
        str = hashtag[0:i]
        not_found = unigrams.get_ugram_tuple(str) is None
        if not_found:
            continue
        node = TreeNode(str)
        if i == range_end:
            return
        load_child_nodes(hashtag[i:], unigrams, node)
        attach_child(root, node)

def attach_child(parent, child):
    child.set_parent(parent)
    parent.add_child(child)

def print_children(root):
    print root.get_token()
    for node in root.get_children():
        print_children(node)

def read_segmentations(root, candidates, stack=None):
    if stack is None:
        stack = []
    is_leaf = len(root.get_children()) == 0
    is_root = (not is_leaf) and (root.get_parent() is None)
    if not is_root:
        stack.append(root)
    if is_leaf:
        candidates.append(list(stack))
    for child in root.get_children():
        read_segmentations(child, candidates, stack)
    if not is_root:
        stack.pop()
    
def argmax(hashtag, candidates, corpus, unigrams):
    tmp = []
    for seg in candidates:
        join = "".join([x.get_token() for x in seg])
        if join != hashtag:
            continue
        if len(seg) == len(hashtag) and len(candidates) > 1:
            continue
        score = score_segmentation(seg, corpus, unigrams)
        tmp.append((seg, score))
    ranks = sorted(tmp, key=lambda tuple:tuple[1])
    if len(ranks) == 0:
        ranks.append(([hashtag], float("-inf")))
    return ranks.pop()[0]
    
def score_segmentation(seg, corpus, unigrams):
    pattern = re.compile("[0-9]+[a-z]")
    seg_length = len(seg)
    score = 0
    if seg_length > 1:
        for i in range(0,seg_length-1):
            tok1 = seg[i].get_token()
            tok2 = seg[i+1].get_token()
            if pattern.match(tok1) is not None or pattern.match(tok2) is not None:
               return float("-inf")
            bigram_score = corpus.score_bigram(tok1, tok2)
            if bigram_score is None:
               '''Fall back on unigram probabilties if the bigram is not in the corpus'''
               int_score = unigrams.get_unigram_prob(tok1) * unigrams.get_unigram_prob(tok2)
               bigram_score = math.log(int_score/1000)
            else:
                bigram_score = bigram_score
            score += bigram_score
    else:
        score = float("-inf")
    return score

def print_segmentation(segmentation):
    for word in segmentation:
        print word,
    print ""

if len(sys.argv) != 4:
    print "Usage: hashtag_segmenter <hashtags file> <bigram corpus> <unigram corpus>"
    sys.exit(1)

unigrams = UnigramCorpus()
bigram_corpus = BigramCorpus()
roots = []

print "Loading corpus data..."
load_ugrams_and_bigram_corpus(unigrams, bigram_corpus, sys.argv[2], sys.argv[3])

print "Building segmentation trees..."
f = open(sys.argv[1])
for line in f:
  tmp = line[1:].lower()
  roots.append(get_segmentation_tree(tmp.strip(), unigrams))
f.close()

print "Results:"
for root in roots:
    candidates = []
    read_segmentations(root, candidates)
    print_segmentation(argmax(root.get_token(), candidates, bigram_corpus, unigrams))

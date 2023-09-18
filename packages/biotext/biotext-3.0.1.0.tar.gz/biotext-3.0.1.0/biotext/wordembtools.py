#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
This module provides a class for generating word embeddings from a collection
of texts using biotext.

Author: Diogo de J. S. Machado
Date: 13/07/2023
"""
from . import fastatools, aminocode
import numpy as np
from tqdm import tqdm
import sys
import sweep
from joblib import Parallel, delayed
from time import time
import re

class WordEmbedding:
    """
    A class for generating word embeddings from a collection of texts.

    Parameters
    ----------
    data_set : list or pandas.Series
        The collection of texts to generate embeddings.
    word_set : list, optional
        A pre-defined set of words to use for the embedding. Defaults to None.
    words_to_skip : bool, optional
        List of words to skip in word embedding. Defaults to None.
    min_occ_to_use : int, optional
        The minimum number of occurrences of a word in the collection of texts
        to include it in the embedding. Defaults to 100.
    max_words : int, optional
        The maximum number of words to include in the word set. Defaults to
        10000.
    word_tokenizer_fun : function, optional
        Custom function for tokenizing words in each text. Defaults to None.
    sweep_projection_mat : numpy.ndarray, optional
        The projection matrix for SWeeP vectorization. Defaults to None.
    sweep_mask : list, optional
        The mask to apply during SWeeP vectorization. Defaults to [2, 1, 2].
    sweep_dtype : dtype, optional
        The data type for SWeeP vectorization. Defaults to None.
    sweep_composition : str, optional
        The composition mode for SWeeP vectorization. Defaults to 'binary'.
    preserve_data_set_splited : bool, optional
        Whether to preserve the split data set object. Defaults to False.
    preserve_data_set_sweeped : bool, optional
        Whether to preserve the swept data set object. Defaults to False.
    n_jobs : int, optional
        The number of jobs to use for parallelization. Defaults to 1.
    chunk_size : int, optional
        The size of each chunk for parallelization. Defaults to 1000.
    sweep_n_jobs : int, optional
        The number of jobs to use for SWeeP vectorization. Defaults to None.
        If None, it receives the value of n_jobs.
    sweep_chunk_size : int, optional
        The size of each chunk for SWeeP vectorization. Defaults to None.
        If None, it receives the value of chunk_size.
    verbose : bool, optional
        Whether to print progress messages. Defaults to True.

    Attributes
    ----------
    word_set : list
        Set of unique words.
    word_embedding : numpy.ndarray
        Word embeddings for the words in the word_set.
    elapsed_time : list
        Elapsed time for each step of the process.

    Example
    --------
    >>> import biotext as bt
    >>> texts = []
    >>> with open ('texts.txt', 'r') as file:
    >>>     for line in file:
    >>>         texts.append(line)
    >>> we = bt.wordembtools.WordEmbedding(data_set = texts)
    >>> embeddings = we.word_embedding
    """
    def __init__(self, data_set,
                 word_set = None,
                 words_to_skip = None,
                 min_occ_to_use = 100,
                 max_words = 10000,
                 word_tokenizer_fun = None,
                 sweep_projection_mat = None,
                 sweep_mask = [2, 1, 2],
                 sweep_dtype = None,
                 sweep_composition = 'binary',
                 preserve_data_set_sweeped = False,
                 preserve_data_set_splited = False,
                 n_jobs = 1,
                 chunk_size = 1000,
                 sweep_n_jobs = None,
                 sweep_chunk_size = None,
                 verbose = True
                 ):
        
        def split_array(arr, chunk_size):
            chunks = []
            for i in range(0, len(arr), chunk_size):
                chunks.append(arr[i:i+chunk_size])
            return chunks

        def parallelization(func, chunks, desc):
            result = Parallel(n_jobs=n_jobs, prefer="threads")(
                delayed(func)
                (i) for i in tqdm(chunks,
                                  position=0,
                                  leave=True,
                                  desc=desc,
                                  file=sys.stdout,
                                  disable=(not verbose)))
            return result

        if verbose:
            print('Number of entries at start: %i' % len(data_set))
            
        process_count_max = 7
        process_count = 0
        
        if verbose:
            process_count += 1
            print(f'[{process_count}/{process_count_max}] Preparing...')
            
        if sweep_n_jobs == None:
            sweep_n_jobs = n_jobs
        if sweep_chunk_size == None:
            sweep_chunk_size = chunk_size
        if word_set is None:
            create_word_set = True
        else:
            create_word_set = False
        if word_tokenizer_fun is None:
            word_tokenizer_fun = lambda x: re.findall(r'\b(\w*[^\s]+\w*)\b', x)
            
        self.elapsed_time = []
            
        # Set projection matrix
        if sweep_projection_mat is None:
            s = time()
            self.sweep_projection_mat = sweep.get_default_proj_mat()
            self.elapsed_time.append(['projection matrix import', time() - s])
        else:
            self.sweep_projection_mat = sweep_projection_mat

        data_set=list(set(data_set))
        
        if verbose:
            print('Number of entries after removing duplicates: %i' % 
                  len(data_set))
            
        data_set = [str(i).lower() for i in data_set]
        
        # Generate splited data_set
        process_count += 1
        s = time()
        chunks = split_array(data_set,chunk_size)
        data_set_splited = parallelization(lambda x:
                                          [set(word_tokenizer_fun(i))
                                           for i in x],
                                          chunks,
                                          f'[{process_count}/'
                                          f'{process_count_max}] '
                                          'Tokenizing data_set')
        data_set_splited = [item for sublist in data_set_splited for item in
                           sublist]
        self.elapsed_time.append(['tokenizing', time() - s])
        
        # Print a message indicating that tokens are being identified in the
        # texts
        process_count += 1
        if verbose:
            print(f'[{process_count}/{process_count_max}] '
                  'Identifying tokens in texts...')
        s = time()
        # explode data_set_splited in a arrays with the index and the word 
        data_set_exploded = []
        data_set_exploded_idx = []
        for index, item in enumerate(data_set_splited):
            for token in item:
                if word_set is not None:
                    if token not in word_set:
                        continue
                data_set_exploded.append(token)
                data_set_exploded_idx.append(index)

        # If no word set is provided, create a set of unique words
        if create_word_set:
            word_set = set(data_set_exploded)
            word_set = sorted(set(word_set))

        # For each word in the word set, find which rows in the data set
        # contain that word and count
        word_count = {item: 0 for item in word_set}
        word_idx = {item: [] for item in word_set}
        for index, word in tqdm(enumerate(data_set_exploded),
                                total=len(data_set_exploded),
                                desc='Find and count tokens'):
            word_count[word] += 1
            word_idx[word].append(data_set_exploded_idx[index])
        word_idx = [word_idx[word] for word in word_set]
        word_count = [word_count[word] for word in word_set]
        # If no word set is provided, remove any words that appear fewer than
        # min_occ_to_use times and words in words_to_remove
        if create_word_set:
            word_count = [len(i) for i in word_idx]
            if min_occ_to_use > 0:
                more_than = [_ for _, x in enumerate(word_count) if x
                             >= min_occ_to_use]
                word_set = [word_set[i] for i in more_than]
                word_idx = [word_idx[i] for i in more_than]
                word_count = [word_count[i] for i in more_than]
            if words_to_skip != None:
                no_skip = [index for index, word in enumerate(word_set) if
                           word not in words_to_skip]
                word_set = [word_set[i] for i in no_skip]
                word_idx = [word_idx[i] for i in no_skip]
                word_count = [word_count[i] for i in no_skip]
            
        if create_word_set:
            # Sort word_count in descending order and get the corresponding
            # indices
            ord_idx = sorted(range(len(word_count)),
                             key=lambda i: word_count[i],
                             reverse=True)
            # Reorder lists based on ord_idx
            word_set = [word_set[i] for i in ord_idx]
            word_idx = [word_idx[i] for i in ord_idx]
            word_count = [word_count[i] for i in ord_idx]
        
        if max_words != None:
            # Select only the top 'max_words' elements from each list
            word_set = word_set[:max_words]
            word_idx = word_idx[:max_words]
            word_count = word_count[:max_words]
        self.elapsed_time.append(['identification of tokens in texts',
                                  time() - s])
        if verbose:
            print('Number of tokens: %i' % len(word_set))
        
        # Removing entries without words in word set
        process_count += 1
        if verbose:
            print(f'[{process_count}/{process_count_max}] Removing entries '
                  'without word set occurrences')
        s = time()
        # Create unique list with all entries that have word(s) of word_set
        idx_to_no_remove = sorted(set(
            [item for sublist in word_idx for item in sublist]))
        # Remove entries without word set occurrences
        data_set = [data_set[i] for i in idx_to_no_remove]
        data_set_splited = [data_set_splited[i] for i in idx_to_no_remove]
        # Create a dictionary by mapping old indexes to new indexes
        old_to_new = {}
        for new_idx,old_idx  in enumerate(idx_to_no_remove):
            old_to_new[old_idx] = new_idx
        # Update index in word_idx
        for sublist in word_idx:
            for i, idx in enumerate(sublist):
                sublist[i] = old_to_new[idx]
        self.elapsed_time.append(
            ['removal entries without word set occurrences',
             time() - s])
        
        if verbose:
            print('Number of entries after removing: %i' % len(data_set))

        # Encode the data set using aminocode
        process_count += 1
        s = time()
        chunks = split_array(data_set, chunk_size)
        data_set_encoded = parallelization(lambda x:
                                          aminocode.encode_list(x),
                                          chunks,
                                          f'[{process_count}/'
                                          f'{process_count_max}] Encoding')
        data_set_encoded = [item for sublist in data_set_encoded for item in 
                           sublist]
        self.elapsed_time.append(['aminocode encoding', time() - s])

        # Print a message indicating that the data set is being vectorized
        process_count += 1
        if verbose:
            print(f'[{process_count}/{process_count_max}] Vectorizing...')
        # Convert the encoded data set to a matrix using SWeeP
        s = time()
        data_set_sweeped = fastatools.fasta_to_mat(data_set_encoded,
                                        orth_mat = self.sweep_projection_mat,
                                        composition = sweep_composition,
                                        dtype = sweep_dtype,
                                        n_jobs = sweep_n_jobs,
                                        chunk_size = sweep_chunk_size,
                                        mask = sweep_mask,
                                        verbose = verbose)
        self.elapsed_time.append(['sweep vectorizing', time() - s])

        # If requested, preserve the sweep matrix
        if preserve_data_set_sweeped:
            self.data_set_sweeped = data_set_sweeped
                    
        # Obtain word embeddings by averaging the vectors of the tokens in
        # each text
        process_count += 1
        s = time()
        chunks = split_array(word_idx, chunk_size)
        self.word_embedding = parallelization(lambda x:
                                              [np.mean(j, axis=0,
                                                       where=~np.isnan(j))
                                               for j in [
                                                       data_set_sweeped[i]
                                                         for i in x]],
                                              chunks,
                                              f'[{process_count}/'
                                              f'{process_count_max}] '
                                              'Getting embedding')
        data_set_encoded = [item for sublist in
                            data_set_encoded for item in 
                           sublist]
        self.word_embedding = [item for sublist in self.word_embedding for
                               item in sublist]
        self.word_embedding = np.array(self.word_embedding)
        self.elapsed_time.append(['averaging per word', time() - s])
        
        self.word_set = word_set
        self.word_count = word_count
        
        if preserve_data_set_splited:
            self.data_set_splited  = data_set_splited

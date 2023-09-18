#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
This module provides functions for encoding and decoding text using DNAbits.

Functions:
- encode_string: Encodes a string using DNAbits.
- decode_string: Decodes a string encoded with DNAbits.
- encode_list: Encodes all strings in a list using DNAbits.
- decode_list: Decodes all strings in a list encoded with DNAbits.
- str_to_bin: Converts a string to a binary representation.
- bin_to_str: Converts a binary representation to a string.

Author: Diogo de J. S. Machado
Date: 13/07/2023
"""
import re
import numpy as np

def encode_string(input_string):
    """
    Encodes a string with DNAbits.
    
    Parameters
    ----------
    input_string : string
        Natural language text string to be encoded.
        
    Returns
    -------
    encoded_string : string
        Encoded text.
        
    Example
    -------
    Encode a string.

    >>> import biotext as bt
    >>> input_string = "Hello world!"
    >>> encoded_string = bt.dnabits.encode_string(input_string)
    >>> print(encoded_string)
    AGACCCGCATGCATGCTTGCAAGATCTCTTGCGATCATGCACGCCAGA
    """
    
    input_string=str_to_bin(input_string)
    text_0 = re.findall('.',input_string[0:len(input_string)-1:2])
    text_1 = re.findall('.',input_string[1:len(input_string):2])
    text = np.transpose(np.array([(text_0),(text_1)]))
    text = text.astype(int)
    text = text * [1,2]
    text = np.sum(text,1)
    text = text.astype(str)
    text[text=='0']='A'
    text[text=='1']='C'
    text[text=='2']='G'
    text[text=='3']='T'
    text=''.join(text)
    encoded_string = text
    return encoded_string

def decode_string(input_string):
    """
    Decodes a string with DNAbits reverse.	
    
    Parameters
    ----------
    input_string : string
        Text string encoded with DNAbits.

    Returns
    -------
    decoded_string : string
        Decoded text.
        
    Example
    -------
    Decode a string.

    >>> import biotext as bt
    >>> encoded_string = "AGACCCGCATGCATGCTTGCAAGATCTCTTGCGATCATGCACGCCAGA"
    >>> decoded_string = bt.dnabits.decode_string(encoded_string)
    >>> print(decoded_string)
    Hello world!
    """
    
    text = np.zeros((len(input_string),2)).astype(int)
    dna=np.array(re.findall('.',input_string))
    text[dna=='A']=[0,0]
    text[dna=='C']=[1,0]
    text[dna=='G']=[0,1]
    text[dna=='T']=[1,1]
    text=text.astype(str)
    text=''.join(np.concatenate(text))
    text=bin_to_str(text)
    decoded_string = text
    return decoded_string

def encode_list(string_list, verbose=False):
    """
    Encodes all strings in a list with DNAbits.	
    
    Parameters
    ----------
    string_list : list
        List of string to be encoded.
    verbose  : bool
        If True displays progress.

    Returns
    -------
    encoded_list : list
        List with all encoded text in string format.
        
    Example
    -------
    Encode the strings in a list and view the result of the first item.

    >>> import biotext as bt
    >>> string_list = ['Hello','world','!']
    >>> encoded_list = bt.dnabits.encode_list(string_list)
    >>> print(encoded_list)
    ['AGACCCGCATGCATGCTTGC', 'TCTCTTGCGATCATGCACGC', 'CAGA']
    """
    
    list_size = len(string_list)
    selectedEncoder = lambda x: encode_string(x)

    encoded_list = []
    if verbose:
        print('Encoding text...')
    for c,i in enumerate(string_list):
        seq = selectedEncoder(i)
        encoded_list.append(seq)
        if verbose and (c+1) % 10000 == 0:
            print (str(c+1)+'/'+str(list_size))
    if verbose:
        print (str(list_size)+'/'+str(list_size))
    return encoded_list

def decode_list(input_list,output_file=None,verbose=False):
    """
    Decodes all strings in a list with reverse DNAbits.	
    
    Parameters
    ----------
    string_list : list
        List of string encoded with DNAbits.
    verbose  : bool
        If True displays progress.

    Returns
    -------
    decoded_list : list of string
        List with all decoded text.
        
    Example
    --------
    Decode the strings in a list and view the result with a loop.

    >>> import biotext as bt
    >>> encoded_list = ['AGACCCGCATGCATGCTTGC', 'TCTCTTGCGATCATGCACGC', 'CAGA']
    >>> decoded_list = bt.dnabits.decode_list(encoded_list)
    >>> print(decoded_list)
    ['Hello', 'world', '!']
    """
    
    list_size = len(input_list)
    selectedEncoder = lambda x: decode_string(x)
    
    decoded_list = []
    if verbose:
        print('Decoding text...')
    for c,i in enumerate(input_list):
        c+=1
        if verbose and (c+1) % 10000 == 0:
            print(str(c+1)+'/'+str(list_size))
        decoded_list.append((selectedEncoder(str(i))))
    if verbose:
        print(str(list_size)+'/'+str(list_size))
    
    return decoded_list

def str_to_bin(string):
    res = ''
    for char in string:
        tmp = bin(ord(char))[2:]
        tmp = '%08d' %int(tmp)
        tmp=tmp[::-1]
        res += tmp
    return res

def bin_to_str(string):
    res = ''
    for idx in range(int(len(string)/8)):
        cstr = string[idx*8:(idx+1)*8]
        cstr=cstr[::-1] #???
        tmp = chr(int(cstr, 2))
        res += tmp
    return res
#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
This module provides functions for encoding and decoding text using AMINOcode.

Functions:
- encode_string: Encodes a string using AMINOcode.
- decode_string: Decodes a string encoded with AMINOcode.
- encode_list: Encodes all strings in a list using AMINOcode.
- decode_list: Decodes all strings in a list encoded with AMINOcode.

Author: Diogo de J. S. Machado
Date: 13/07/2023
"""
import re
import unidecode

aminocode_table = {
      "a": "YA",
      "b": "E",
      "c": "C",
      "d": "D",
      "e": "YE",
      "f": "F",
      "g": "G",
      "h": "H",
      "i": "YI",
      "j": "I",
      "k": "K",
      "l": "L",
      "m": "M",
      "n": "N",
      "o": "YQ",
      "p": "P",
      "q": "Q",
      "r": "R",
      "s": "S",
      "t": "T",
      "u": "YV",
      "v": "V",
      "x": "W",
      "z": "A",
      "w": "YW",
      "y": "YY",
      ".": "YP",
      "9": "YD",
      " ": "YS",
}

aminocode_table_d = {
      "0": "YDA",
      "1": "YDQ",
      "2": "YDT",
      "3": "YDH",
      "4": "YDF",
      "5": "YDI",
      "6": "YDS",
      "7": "YDE",
      "8": "YDG",
      "9": "YDN",
}

aminocode_table_p = {
      ".": "YPE",
      ",": "YPC",
      ";": "YPS",
      "!": "YPW",
      "?": "YPQ",
      ":": "YPT",
}  

def encode_string(input_string,detail='dp'):
    """
    Encodes a string with AMINOcode.
    
    Parameters
    ----------
    input_string : string
        Natural language text string to be encoded.
    detail : string
        Set details in coding. 'd' for details in digits; 'p' for details on 
        the punctuation; 'dp' or 'pd' for both. Default is 'dp'.
        
    Returns
    -------
    encoded_string : string
        Encoded text.
        
    Example
    -------
    Encode a string.

    >>> import biotext as bt
    >>> input_string = "Hello world!"
    >>> encoded_string = bt.aminocode.encode_string(input_string,'dp')
    >>> print(encoded_string)
    HYELLYQYSYWYQRLDYPW
    """
    
    try:
        input_string = input_string.decode('utf-8')
    except:
        pass
    
    input_string = unidecode.unidecode(input_string) #remove accents
    input_string = input_string.lower() #lower case
    input_string = re.sub('\s',' ',input_string) #all spaces to " "
    
    c_dict = aminocode_table.copy()
    if 'd' in detail:
        c_dict.update(aminocode_table_d)
    else:
        input_string = re.sub('\d','9',input_string) #all numbers to 9
    if 'p' in detail:
        c_dict.update(aminocode_table_p)
    else:
        input_string = re.sub('[,;!?:]','.',input_string) #all punctuation to "."
    
    for i in ''.join(set(input_string)):
        try:
            c_dict[i]
        except KeyError:
            c_dict[i]='YK'
            
    for k,v in c_dict.items():
        input_string = input_string.replace(k, v)
    encoded_string = input_string
    return encoded_string
    
def decode_string(input_string,detail='dp'):
    """
    Decodes a string with AMINOcode reverse.
    
    Parameters
    ----------
    input_string : string
        Text string encoded with AMINOcode.
    detail : string
        Set details in coding. 'd' for details in digits; 'p' for details on 
        the punctuation; 'dp' or 'pd' for both. Default is 'dp'.

    Returns
    -------
    decoded_string : string
        Decoded text.
        
    Example
    --------
    Decode a string.

    >>> import biotext as bt
    >>> encoded_string = "HYELLYQYSYWYQRLDYPW"
    >>> decoded_string = bt.aminocode.decode_string(encoded_string,'dp')
    >>> print(decoded_string)
    hello world!
    """
    
    c_dict = aminocode_table.copy()
    if 'd' in detail:
        c_dict.update(aminocode_table_d)
    if 'p' in detail:
        c_dict.update(aminocode_table_p)
        
    c_dict=dict(sorted(c_dict.items(),key=lambda x: (len(x[1]),x[0]),reverse=True))
    input_string = input_string.replace('YK', '-')
    for k,v in c_dict.items():
        input_string = input_string.replace(v, k)
    decoded_string = input_string
    return decoded_string

def encode_list(string_list, detail='dp', verbose=False):
    """
    Encodes all strings in a list with AMINOcode.
    
    Parameters
    ----------
    string_list : list
        List of string to be encoded.
    detail : string
        Set details in coding. 'd' for details in digits; 'p' for details on 
        the punctuation; 'dp' or 'pd' for both. Default is 'dp'.
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
    >>> encoded_list = bt.aminocode.encode_list(string_list,detail='dp')
    >>> print(encoded_list)
    ['HYELLYQ', 'YWYQRLD', 'YPW']
    """
    
    list_size = len(string_list)
    selectedEncoder = lambda x: encode_string(x,detail=detail)

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

def decode_list(input_list,detail='dp',verbose=False):
    """
    Decodes all strings in a list with reverse AMINOcode.	
    
    Parameters
    ----------
    string_list : list
        List of string encoded with aminocode.
    detail : string
        Set details in coding. 'd' for details in digits; 'p' for details on 
        the punctuation; 'dp' or 'pd' for both. Default is 'dp'.
    verbose  : bool
        If True displays progress.

    Returns
    -------
    decoded_list : list of string
        List with all decoded text.
        
    Example
    -------
    Descode the strings in a list and view the result with a loop.

    >>> import biotext as bt
    >>> encoded_list = ['HYELLYQ', 'YWYQRLD', 'YPW']
    >>> decoded_list = bt.aminocode.decode_list(encoded_list,detail='dp')
    >>> print(decoded_list)
    ['hello', 'world', '!']
    """
    
    list_size = len(input_list)
    selectedEncoder = lambda x: decode_string(x,detail=detail)
    
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
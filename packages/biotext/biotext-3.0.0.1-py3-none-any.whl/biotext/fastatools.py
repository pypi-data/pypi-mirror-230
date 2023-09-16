#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
This module provides functions for working with FASTA files and performing
sequence alignment.

Functions:
- import_fasta: Import a FASTA file using Biopython.
- export_fasta: Export a SeqRecord list as a FASTA file.
- create_seqrecord_list: Create a SeqRecord list from a string list.
- run_clustalo: Run Clustal Omega multiple sequence alignment.
- get_consensus: Get the consensus sequence from a list of sequences.
- get_header: Get the headers from a list of SeqRecord objects.
- get_seq: Get the sequences from a list of SeqRecord objects.
- fasta_to_mat: Convert FASTA sequences to a matrix representation using SWeeP.

Author: Diogo de J. S. Machado
Date: 13/07/2023
"""
import tempfile
import os
from Bio import AlignIO, SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import re
import numpy as np
from scipy import stats
import codecs
from sweep import fas2sweep
import subprocess
from scipy.sparse import lil_matrix, isspmatrix_lil
    
def import_fasta(input_file_name):
    """
    Uses biopython to import a FASTA file.
    
    Parameters
    ----------
    input_file_name : string (valid file name)
        Input fasta file name.

    Returns
    -------
    seqrecord_list : list of SeqRecord
        List of SeqRecord imported from file.
        
    Example
    -------
    Import a FASTA file named 'sequences.fasta'.

    >>> import biotext as bt
    >>> input_file = 'sequences.fasta'
    >>> fasta = bt.fastatools.import_fasta(input_file)
    >>> print(fasta[0]) # print first sequence in input file
    ID: 1
    Name: 1
    Description: 1
    Number of features: 0
    Seq('HYELLYQYSYWYQRLD')
    """
    
    with codecs.open(input_file_name,'r','utf-8') as f:
        seqrecord_list = list(SeqIO.parse(f, "fasta"))
    return seqrecord_list
    
def export_fasta(seqrecord_list, output_file_name, header=None):
    """
    Create a file using a SeqRecord (Biopython object) list.
    
    Parameters
    ----------
    output_file_name : string
        Output fasta file name.
    seqrecord_list : list of SeqRecord
        List of SeqRecord.
        
    Example
    --------
    Export a SeqRecord list as FASTA file named 'sequences.fasta'.

    >>> import biotext as bt
    >>> seq_list = ['ACTG','GTCA']
    >>> seqrecord_list = bt.fastatools.create_seqrecord_list(seq_list)
    >>> bt.fastatools.export_fasta(seqrecord_list,'sequences.fasta')
    """
    
    seqrecord_list = list(seqrecord_list)
    
    if header != None: 
        seqrecord_list = create_seqrecord_list([str(i.seq) for i in seqrecord_list],header=header)
    
    outputFile = codecs.open(output_file_name,'w','utf-8')
    for i in seqrecord_list:
        if len(i.seq) > 0:
            outputFile.write('>'+i.description+'\n')
            seq = str(i.seq)
            seq = re.findall('[\w-]{0,'+str(100)+'}',seq)
            seq = '\n'.join(seq)
            outputFile.write(seq)
    outputFile.close()
    
def create_seqrecord_list(seq_list,header_list=None):
    """
    Create a list of SeqRecord (Biopython object) with a string list.
    
    Parameters
    ----------
    seq_list : list of string
        List of biological sequences in string format.
    header : list of string
        List of headers in string format, if set to 'None' the headers will 
        be automatically defined with numbers in increasing order.

    Returns
    -------
    seqrecord_list : list of SeqRecord
        List of SeqRecord.
        
    Example
    -------
    Decode a string.

    >>> import biotext as bt
    >>> seq_list = ['ACTG','GTCA']
    >>> seqrecord_list = bt.fastatools.create_seqrecord_list(seq_list)
    >>> for i in seqrecord_list:
    >>>     print (i)
    ID: 1
    Name: <unknown name>
    Description: 1
    Number of features: 0
    Seq('ACTG')
    ID: 2
    Name: <unknown name>
    Description: 2
    Number of features: 0
    Seq('GTCA')
    """
    if header_list == None:
        header_list = list(range(1,len(seq_list)+1))
    seqrecord_list = []
    for i in range(0,len(seq_list)):
        description = str(header_list[i])
        ident = re.split('\s+',description)[0]
        record = SeqRecord(Seq(seq_list[i]), description=description,
                           id=ident)
        seqrecord_list.append(record)
    return seqrecord_list
    
def run_clustalo(input_file_name, args=""):
    """
    Run Clustal Omega multiple sequence alignment on the input file.

    Parameters
    ----------
    input_file_name : str
        Path to the input file containing the sequences to align.
    args : str, optional
        Additional arguments to pass to Clustal Omega. Defaults to an empty string.

    Output
    ------
    align : Bio.Align.MultipleSeqAlignment
        Aligned sequences in the Clustal format.

    Example
    -------
    Perform multiple sequence alignment using Clustal Omega:

    >>> import biotext as bt
    >>> input_file = 'sequences.fasta'
    >>> alignment = bt.fastatools.run_clustalo(input_file)
    >>> print(alignment)
    Alignment with 3 rows and 16 columns
    HYELLYQYSYWYQRLD 1
    HYELLYQ--------- 2
    ---------YWYQRLD 3
    """
    # Create a temporary file to store the Clustal output
    fp = tempfile.TemporaryFile(mode='w', delete=False)

    # Build the Clustal Omega command string
    cmd_string = "clustalo -i " + input_file_name + " -o " + fp.name + " --auto --outfmt clu --force"
    cmd_string += " " + args

    # Execute the Clustal Omega command
    subprocess.call(cmd_string, shell=True)

    # Read the aligned sequences from the temporary file
    align = AlignIO.read(fp.name, "clustal")

    # Close and remove the temporary file
    fp.close()
    os.unlink(fp.name)

    # Return the aligned sequences
    return align
    
def get_consensus(seq_list, preserve_gap=False):
    """
    Get the consensus sequence from a list of sequences.

    Parameters
    ----------
    seq_list : list
        List of sequences in SeqRecord object format or as strings.
    preserve_gap : bool, optional
        If True, the consensus sequence may contain gaps ("-") based on the majority characters and the gaps present in the aligned sequences. 
        If False, the consensus sequence is determined without gaps by considering only the majority characters.

    Returns
    -------
    consensus : str
        Consensus sequence based on the majority characters, with or without gaps ("-") depending on the `preserve_gap` parameter.
    align : list
        List of aligned sequences.

    Example
    -------
    Calculate the consensus sequence from a list of sequences:

    >>> import biotext as bt
    >>> seq_list = ['ACTG', 'ACTC', 'ACCC', 'ACC']
    >>> consensus, align = bt.fastatools.get_consensus(seq_list, preserve_gap=True)
    >>> print('Consensus: ', consensus)
    >>> print('Alignment: ', align)
    Consensus:  ACCC
    Alignment:  ['ACTG', 'ACTC', 'ACCC', 'ACC-']
    """
    seq_list = list(seq_list)

    # Check if the input is in SeqRecord object format, if not, do the conversion
    try:
        seq_list[0].description
    except AttributeError:
        seq_list = create_seqrecord_list(seq_list)

    # Create a temporary file to store the sequences in FASTA format
    fastaText = tempfile.TemporaryFile(mode='w', delete=False)
    for i in seq_list:
        fastaText.write('>' + str(i.description) + '\n' + str(i.seq) + '\n')
    fastaText.close()

    align = []
    if len(seq_list) > 1:
        align1 = run_clustalo(fastaText.name)
        align2 = []
        for i in align1:
            align2.append(list(i.seq))
            align.append(str(i.seq))
        align2 = np.array(align2)
        m = stats.mode(align2, keepdims=False)  # Determine mode
        m = m[0][m[1] >= 0]  # Filter characters by minimal occurrence
        consensus = ''.join(m)
        if not preserve_gap:
            consensus = re.sub('\-+', '', consensus)
    else:
        consensus = str(seq_list[0].seq)
        align.append(consensus)

    os.unlink(fastaText.name)

    return consensus, align

def get_header(seqrecord_list):
    """
    Get the header from all items in a list of SeqRecord (Biopython object).
    
    Parameters
    ----------
    seqrecord_list : list of SeqRecord
        List of SeqRecord.

    Returns
    -------
    header_list : list of string
        List of all headers extracted from input.
        
    Example
    -------
    Create seqrecord_list, extract headers and print it.

    >>> import biotext as bt
    >>> seq_list = ['ACTG','GTCA']
    >>> seqrecord_list = bt.fastatools.create_seqrecord_list(seq_list)
    >>> extracted_header_list = bt.fastatools.get_header(seqrecord_list)
    >>> print(extracted_header_list)
    ['1', '2']
    """
    
    seqrecord_list = list(seqrecord_list)
    header_list = []
    for i in seqrecord_list:
        header = i.description
        header_list.append (header)
    return header_list

def get_seq(seqrecord_list):
    """
    Get the sequences from all items in a list of SeqRecord (Biopython object).
    
    Parameters
    ----------
    seqrecord_list : list of SeqRecord
        List of SeqRecord.

    Returns
    -------
    seq_list : list of string
        List of all sequences extracted from input.
        
    Example
    -------
    Create seqrecord_list, extract sequences and print it.

    >>> import biotext as bt
    >>> seq_list = ['ACTG','GTCA']
    >>> seqrecord_list = bt.fastatools.create_seqrecord_list(seq_list)
    >>> extracted_seq_list = bt.fastatools.get_seq(seqrecord_list)
    >>> print(extracted_seq_list)
    ['ACTG', 'GTCA']
    """
    
    seqrecord_list = list(seqrecord_list)
    seq_list = []
    for i in seqrecord_list:
        seq = i.seq
        seq_list.append (str(seq))
    return seq_list

def fasta_to_mat(fasta,mask=[2,1,2],**kwargs):
    """
    Convert FASTA sequences to a matrix representation using SWeeP method.

    Parameters
    ----------
    fasta : list
        List of sequences in SeqRecord object format or as strings.
    mask : list, optional
        A list specifying the mask values. Defaults to [2, 1, 2].
    **kwargs : dict, optional
        Additional keyword arguments to pass to the `fas2sweep` function.

    Returns
    -------
    mat : numpy.ndarray or scipy.sparse.lil_matrix
        Matrix representation of the sequences.

    Example
    -------
    Convert FASTA sequences to a matrix representation:

    >>> import biotext as bt
    >>> seq_list = ['HYELLYQYSYWYQRLD', 'HYELLYQ', 'YWYQRLD']
    >>> matrix = bt.fastatools.fasta_to_mat(seq_list)
    >>> print(matrix.shape)
    (3, 600)
    """
    
    try:
        fasta[0].seq
    except AttributeError:
        fasta=create_seqrecord_list(fasta)
    fasta_aux=[]
    min_size=[]
    for i in fasta:
        if len(str(i.seq)) >= sum(mask):
            fasta_aux.append(i)
            min_size.append(True)
        else:
            min_size.append(False)

    mat_aux = fas2sweep(fasta_aux,mask=mask,**kwargs)
    out_type = type(mat_aux[0,0])
    if isspmatrix_lil(mat_aux):
        mat = lil_matrix((len(fasta),mat_aux.shape[1]),dtype=out_type)
    else:
        mat = np.zeros((len(fasta),mat_aux.shape[1]),dtype=out_type)
    mat[min_size] = mat_aux

    return mat

# Biotext

---

The biotext library offers resources for natural language processing based on
bioinformatics tools. With biotext, it is possible to use native bioinformatics
methods to create text mining strategies. The biotext process starts by
encoding natural language texts in a format based on biological sequences,
which are usable in alignment and vectorization approaches.

---

---

# Features

---

## AMINOcode (biotext.aminocode)
- `biotext.aminocode.encode_string`: Encodes a string using AMINOcode.
- `biotext.aminocode.encode_list`: Encodes all strings in a list using
                                   AMINOcode.
- `biotext.aminocode.decode_string`: Decodes a string encoded with AMINOcode.
- `biotext.aminocode.decode_list`: Decodes all strings in a list encoded with
                                   AMINOcode.

## DNAbits (biotext.dnabits)
- `biotext.dnabits.encode_string`: Encodes a string using DNAbits.
- `biotext.dnabits.decode_string`: Decodes a string encoded with DNAbits.
- `biotext.dnabits.encode_list`: Encodes all strings in a list using DNAbits.
- `biotext.dnabits.decode_list`: Decodes all strings in a list encoded with
                                 DNAbits.

## FASTA Tools (biotext.fastatools)
- `biotext.fastatools.import_fasta`: Imports a FASTA file.
- `biotext.fastatools.export_fasta`: Creates a FASTA file from a list of
                                     sequences.
- `biotext.fastatools.create_seqrecord_list`: Creates a list of SeqRecord
                                              objects from a list of sequences.
- `biotext.fastatools.run_clustalo`: Performs multiple sequence alignment using
                                     Clustal Omega.
- `biotext.fastatools.get_consensus`: Retrieves the consensus sequence from a
                                      set of sequences.
- `biotext.fastatools.get_header`: Retrieves the headers from a list of
                                   SeqRecord objects.
- `biotext.fastatools.get_seq`: Retrieves the sequences from a list of
                                SeqRecord objects.
- `biotext.fastatools.fasta_to_mat`: Converts FASTA sequences to a vectorial
                                     representation.

## Word Embedding Tools (biotext.wordembtools)
- `biotext.wordembtools.WordEmbedding`: A class for generating word embeddings
                                        from a collection of texts.

---

---

# Installation

You can install BioText using pip:

    pip install biotext
---

---

# Functions

---

## AMINOcode (aminocode)

---
### `biotext.aminocode.encode_string`
Encodes a string with AMINOcode.

**Parameters**

- `input_string` : str
    - Natural language text string to be encoded.
- `detail` : str
    - Set details in coding.
    - 'd' for details in digits; 'p' for details on the punctuation;
    'dp' or 'pd' for both.
    - Default is 'dp'.
    
**Returns**

- `encoded_string` : string
  - Encoded text.
    
**Example**

Encode a string.
```python
import biotext as bt
input_string = "Hello world!"
encoded_string = bt.aminocode.encode_string(input_string,'dp')
print(encoded_string)
# HYELLYQYSYWYQRLDYPW
```
---
### `biotext.aminocode.encode_list`
Encodes all strings in a list with AMINOcode.

**Parameters**

- `string_list` : list
    - List of string to be encoded.
- `detail` : str
    - Set details in coding.'d' for details in digits; 'p' for details
    on the punctuation; 'dp' or 'pd' for both.
    - Default is 'dp'.
- `verbose`  : bool
    - If True displays progress.

**Returns**

- `encoded_list` : list
    - List with all encoded text in string format.
    
**Example**

Encode the strings in a list and view the result of the first item.
```python
import biotext as bt
string_list = ['Hello','world','!']
encoded_list = bt.aminocode.encode_list(string_list,detail='dp')
print(encoded_list)
# ['HYELLYQ', 'YWYQRLD', 'YPW']
```
---
### `biotext.aminocode.decode_string`
Decodes a string with AMINOcode reverse.

**Parameters**

- `input_string` : str
    - Text string encoded with AMINOcode.
- `detail` : str
    - Set details in coding. 'd' for details in digits; 'p' for details on 
    the punctuation; 'dp' or 'pd' for both.
    - Default is 'dp'.

**Returns**

- `decoded_string` : str
    - Decoded text.
    
**Example**

Deconde a string.
```python
import biotext as bt
encoded_string = "HYELLYQYSYWYQRLDYPW"
decoded_string = bt.aminocode.decode_string(encoded_string,'dp')
print(decoded_string)
# hello world!
```
---
### `biotext.aminocode.decode_list`
Decodes all strings in a list with reverse AMINOcode.	

**Parameters**

- `string_list` : list
    - List of string encoded with aminocode.
- `detail` : str
    - Set details in coding. 'd' for details in digits; 'p' for details on 
    the punctuation; 'dp' or 'pd' for both.
    - Default is 'dp'.
- `verbose`  : bool
    - If True displays progress.

**Returns**

- `decoded_list` : list of string
    - List with all decoded text.
    
**Example**

Descode the strings in a list and view the result with a loop.
```python
import biotext as bt
encoded_list = ['HYELLYQ', 'YWYQRLD', 'YPW']
decoded_list = bt.aminocode.decode_list(encoded_list,detail='dp')
print(decoded_list)
# ['hello', 'world', '!']
```
---

## DNAbits (dnabits)

---
### `biotext.dnabits.encode_string`
Encodes a string with DNAbits.

**Parameters**

- `input_string` : string
    - Natural language text string to be encoded.
    
**Returns**

- `encoded_string` : string
    - Encoded text.
    
**Example**

Encode a string.
```python
import biotext as bt
input_string = "Hello world!"
encoded_string = bt.dnabits.encode_string(input_string)
print(encoded_string)
# AGACCCGCATGCATGCTTGCAAGATCTCTTGCGATCATGCACGCCAGA
```
---
### `biotext.dnabits.decode_string`
Decodes a string with DNAbits reverse.	

**Parameters**

- `input_string` : string
    - Text string encoded with DNAbits.

**Returns**

- `decoded_string` : string
    - Decoded text.
    
**Example**

Decode a string.
```python
import biotext as bt
encoded_string = "AGACCCGCATGCATGCTTGCAAGATCTCTTGCGATCATGCACGCCAGA"
decoded_string = bt.dnabits.decode_string(encoded_string)
print(decoded_string)
# Hello world!
```
---
### `biotext.dnabits.encode_list`
Encodes all strings in a list with DNAbits.	

**Parameters**

- `string_list` : list
    - List of string to be encoded.
- `verbose`  : bool
    - If True displays progress.

**Returns**

- `encoded_list` : list
    - List with all encoded text in string format.
    
**Example**

Encode the strings in a list and view the result of the first item.
```python
import biotext as bt
string_list = ['Hello','world','!']
encoded_list = bt.dnabits.encode_list(string_list)
print(encoded_list)
# ['AGACCCGCATGCATGCTTGC', 'TCTCTTGCGATCATGCACGC', 'CAGA']
```
---
### `biotext.dnabits.decode_list`
Decodes all strings in a list with reverse DNAbits.	

**Parameters**

- `string_list` : list
    - List of string encoded with DNAbits.
`verbose`  : bool
    - If True displays progress.

**Returns**

`decoded_list` : list of string
    - List with all decoded text.
    
**Example**

Decode the strings in a list and view the result with a loop.
```python
import biotext as bt
encoded_list = ['AGACCCGCATGCATGCTTGC', 'TCTCTTGCGATCATGCACGC', 'CAGA']
decoded_list = bt.dnabits.decode_list(encoded_list)
print(decoded_list)
# ['Hello', 'world', '!']
```
---

## FASTA Tools (fastatools)

---
### `biotext.fastatools.import_fasta`
Uses biopython to import a FASTA file.

**Parameters**

- `input_file_name` : string (valid file name)
    - Input fasta file name.

**Returns**

- `seqrecord_list` : list of SeqRecord
    - List of SeqRecord imported from file.
    
**Example**

Import a FASTA file named 'sequences.fasta'.
```python
import biotext as bt
input_file = 'sequences.fasta'
fasta = bt.fastatools.import_fasta(input_file)
# print first sequence in input file
print(fasta[0])
# ID: 1
# Name: 1
# Description: 1
# Number of features: 0
# Seq('HYELLYQYSYWYQRLD')
```
---
### `biotext.fastatools.export_fasta`
Create a file using a SeqRecord (Biopython object) list.

**Parameters**

- `output_file_name` : string
    - Output fasta file name.
- `seqrecord_list` : list of SeqRecord
    - List of SeqRecord.
    
**Example**

Export a SeqRecord list as FASTA file named 'sequences.fasta'.
```python
import biotext as bt
seq_list = ['ACTG','GTCA']
seqrecord_list = bt.fastatools.create_seqrecord_list(seq_list)
bt.fastatools.export_fasta(seqrecord_list,'sequences.fasta')
```
---
### `biotext.fastatools.create_seqrecord_list`
Create a list of SeqRecord (Biopython object) with a string list.

**Parameters**

- `seq_list` : list of string
    - List of biological sequences in string format.
- `header` : list of string
    - List of headers in string format, if set to 'None' the headers will 
    be automatically defined with numbers in increasing order.

**Returns**

- `seqrecord_list` : list of SeqRecord
    - List of SeqRecord.
    
**Example**

Decode a string.
```python
import biotext as bt
seq_list = ['ACTG','GTCA']
seqrecord_list = bt.fastatools.create_seqrecord_list(seq_list)
for i in seqrecord_list:
    print (i)
# ID: 1
# Name: <unknown name>
# Description: 1
# Number of features: 0
# Seq('ACTG')
# ID: 2
# Name: <unknown name>
# Description: 2
# Number of features: 0
# Seq('GTCA')
```
---
### `biotext.fastatools.run_clustalo`
Run Clustal Omega multiple sequence alignment on the input file.

**Parameters**

- `input_file_name` : str
    - Path to the input file containing the sequences to align.
- `args` : str, optional
    - Additional arguments to pass to Clustal Omega. Defaults to an empty string.

**Returns**

- `align` : Bio.Align.MultipleSeqAlignment
    - Aligned sequences in the Clustal format.

**Example**

Perform multiple sequence alignment using Clustal Omega:
```python
import biotext as bt
input_file = 'sequences.fasta'
alignment = bt.fastatools.run_clustalo(input_file)
print(alignment)
# Alignment with 3 rows and 16 columns
# HYELLYQYSYWYQRLD 1
# HYELLYQ--------- 2
# ---------YWYQRLD 3
```
---
### biotext.fastatools.get_consensus
Get the consensus sequence from a list of sequences.

**Parameters**

- `seq_list` : list
    - List of sequences in SeqRecord object format or as strings.
- `preserve_gap` : bool, optional
    - If True, the consensus sequence may contain gaps ("-") based
	on the majority characters and the gaps present in the aligned sequences. 
    - If False, the consensus sequence is determined without gaps
	by considering only the majority characters.

**Returns**

- `consensus` : str
    - Consensus sequence based on the majority characters, with or without
	gaps ("-") depending on the `preserve_gap` parameter.
- `align` : list
    - List of aligned sequences.

**Example**

Calculate the consensus sequence from a list of sequences:
```python
import biotext as bt
seq_list = ['ACTG', 'ACTC', 'ACCC', 'ACC']
consensus, align = bt.fastatools.get_consensus(seq_list)
print('Consensus: ', consensus)
print('Alignment: ', align)
# Consensus:  ACCC
# Alignment:  ['ACTG', 'ACTC', 'ACCC', 'ACC-']
```
---
### `biotext.fastatools.get_header`
Get the header from all items in a list of SeqRecord (Biopython object).

**Parameters**

- `seqrecord_list` : list of SeqRecord
    - List of SeqRecord.

**Returns**

- `header_list` : list of string
    - List of all headers extracted from input.
    
**Example**

Create seqrecord_list, extract headers and print it.
```python
import biotext as bt
seq_list = ['ACTG','GTCA']
seqrecord_list = bt.fastatools.create_seqrecord_list(seq_list)
extracted_header_list = bt.fastatools.get_header(seqrecord_list)
print(extracted_header_list)
# ['1', '2']
```
---
### `biotext.fastatools.get_seq`
Get the sequences from all items in a list of SeqRecord (Biopython object).

**Parameters**

- `seqrecord_list` : list of SeqRecord
    - List of SeqRecord.

**Returns**

- `seq_list` : list of string
    - List of all sequences extracted from input.
    
**Example**

Create seqrecord_list, extract sequences and print it.
```python
import biotext as bt
seq_list = ['ACTG','GTCA']
seqrecord_list = bt.fastatools.create_seqrecord_list(seq_list)
extracted_seq_list = bt.fastatools.get_seq(seqrecord_list)
print(extracted_seq_list)
# ['ACTG', 'GTCA']
```
---
### `biotext.fastatools.fasta_to_mat`
Convert FASTA sequences to a matrix representation using SWeeP method.

**Parameters**

- `fasta` : list
    - List of sequences in SeqRecord object format or as strings.
- `mask` : list, optional
    - A list specifying the mask values. Defaults to [2, 1, 2].
- `**kwargs` : dict, optional
    - Additional keyword arguments to pass to the `fas2sweep` function.

**Returns**

- `mat` : numpy.ndarray or scipy.sparse.lil_matrix
    - Matrix representation of the sequences.

**Example**

Convert FASTA sequences to a matrix representation:
```python
import biotext as bt
seq_list = ['HYELLYQYSYWYQRLD', 'HYELLYQ', 'YWYQRLD']
matrix = bt.fastatools.fasta_to_mat(seq_list)
print(matrix.shape)
# (3, 600)
```
---

---

## Word Embedding Tools (wordembtools)

---
### `wordembtools`

A class for generating word embeddings from a collection of texts.

**Parameters**

- `data_set` : list or pandas.Series
    - The collection of texts to generate embeddings.
- `word_set` : list, optional
    - A pre-defined set of words to use for the embedding. Defaults to None.
- `remove_stopwords` : bool, optional
    - Whether to remove stop words from the texts. Defaults to False.
- `stopwords_list` : list, optional
    - Custom list of stop words to remove from the texts. Defaults to None.
- `min_occ_to_use` : int, optional
    - The minimum number of occurrences of a word in the collection of texts
    to include it in the embedding. Defaults to 100.
- `max_words` : int, optional
    - The maximum number of words to include in the word set. Defaults to
    10,000.
- `word_tokenizer_fun` : function, optional
    - Custom function for tokenizing words in each text. Defaults to None.
- `sweep_projection_mat` : numpy.ndarray, optional
    - The projection matrix for SWeeP vectorization. Defaults to None.
- `sweep_mask` : list, optional
    - The mask to apply during SWeeP vectorization. Defaults to [2, 1, 2].
- `sweep_dtype` : dtype, optional
    - The data type for SWeeP vectorization. Defaults to None.
- `sweep_composition` : str, optional
    - The composition mode for SWeeP vectorization. Defaults to 'binary'.
- `preserve_data_set_splited` : bool, optional
    - Whether to preserve the split data set object. Defaults to False.
- `preserve_data_set_sweeped` : bool, optional
    - Whether to preserve the swept data set object. Defaults to False.
- `n_jobs` : int, optional
    - The number of jobs to use for parallelization. Defaults to 1.
- `chunk_size` : int, optional
    - The size of each chunk for parallelization. Defaults to 1000.
- `sweep_n_jobs` : int, optional
    - The number of jobs to use for SWeeP vectorization. Defaults to None.
    - If None, it receives the value of n_jobs.
- `sweep_chunk_size` : int, optional
    - The size of each chunk for SWeeP vectorization. Defaults to None.
    - If None, it receives the value of chunk_size.
- `verbose` : bool, optional
    - Whether to print progress messages. Defaults to True.

**Attributes**

- `word_set` : list
    - Set of unique words.
- `word_embedding` : numpy.ndarray
    - Word embeddings for the words in the word_set.
- `elapsed_time` : list
    - Elapsed time for each step of the process.

**Example**
```python
import biotext as bt
texts = []
with open ('texts.txt', 'r') as file:
    for line in file:
        texts.append(line)
we = bt.wordembtools.WordEmbedding(data_set = texts)
embeddings = we.word_embedding
```

---

---

# Usage Examples

## Encoding with AMINOcode
```python
import biotext as bt

input_string = "Hello world!"
encoded_string = bt.aminocode.encode_string(input_string, 'dp')
print(encoded_string)
# HYELLYQYSYWYQRLDYPW

string_list = ['Hello', 'world', '!']
encoded_list = bt.aminocode.encode_list(string_list, detail='dp')
print(encoded_list)
# ['HYELLYQ', 'YWYQRLD', 'YPW']
```
## Decoding with AMINOcode
```python
import biotext as bt

encoded_string = "HYELLYQYSYWYQRLDYPW"
decoded_string = bt.aminocode.decode_string(encoded_string, 'dp')
print(decoded_string)
# hello world!

encoded_list = ['HYELLYQ', 'YWYQRLD', 'YPW']
decoded_list = bt.aminocode.decode_list(encoded_list, detail='dp')
print(decoded_list)
# ['hello', 'world', '!']
```
## Importing and Exporting FASTA Files
```python
import biotext as bt

input_file = 'sequences.fasta'
fasta = bt.fastatools.import_fasta(input_file)
print(fasta[0])  # Print the first sequence in the input file

seq_list = ['ACTG', 'GTCA']
seqrecord_list = bt.fastatools.create_seqrecord_list(seq_list)
bt.fastatools.export_fasta(seqrecord_list, 'sequences.fasta')
```
## Generating Word Embeddings
```python
import biotext as bt

texts = [
    'This is the first text.',
    'This is the second text.',
    'And this is the third text.'
]

we = bt.wordembtools.WordEmbedding(data_set=texts, min_occ_to_use=0)
embeddings = we.word_embedding
print(embeddings)
```
## Vectorizing FASTA Sequence
```python
import biotext as bt

seq_list = ['HYELLYQ', 'YWYQRLD', 'YPW']
matrix = bt.fastatools.fasta_to_mat(seq_list)
print(matrix.shape)
# (3, 600)
```
## Encoding Text with AMINOcode and Vectorizing
```python
import biotext as bt

texts = [
    'This is the first text.',
    'This is the second text.',
    'And this is the third text.'
]
encoded_texts = bt.aminocode.encode_list(texts, 'dp')
matrix = bt.fastatools.fasta_to_mat([encoded_texts])
print(matrix.shape)
# (3, 600)
```

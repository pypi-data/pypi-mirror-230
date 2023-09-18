# Triplix
[![PyPI version](https://badge.fury.io/py/triplix.svg)](https://badge.fury.io/py/triplix)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/triplix.svg)
[![MIT](https://img.shields.io/pypi/l/triplix.svg?color=green)](https://opensource.org/licenses/MIT)

A python package to efficiently process, store and retrieve spatial genomics multi-contact data.

## Introduction:
Triplix provides access to multi-contact data, that could be stored in three different spaces (i.e., resolution): 
1. **Concatemers**: An HDF5 container that stores multi-contact data in a table-like format. 
Each row in this table is an alignment that is captured by a particular `concatemer` (i.e., a sequenced long `read`). 
There is an index (i.e., `read_idx`) column in this table that specifies alignments that originate from each specific `concatemer`.

2. **Tri-alignments**:
Every possible three cis-alignments of each `concatemer` is stored in the Tri-alignment file. Each three cis-alignment is called a `tri-alignment`. 
Such a data structure facilitates 3-way interaction analyses, and allow random-access. 
To this end, `Triplix` has a simple wrapper around [pairix](https://github.com/4dn-dcic/pairix).
In particular, the relevant `tri-alignments` are loaded by checking the first two given coordinates using `pairix`, and then filtering for the third coordinate via an ordinary overlap check.

3. **Triplets**:
Triples are essentially Tri-alignment files, where `tri-alignments` are aggregated into genomic bins. 
This not only reduces the disk (and memory) footprint, but also facilitates random-access. Considering the sparcity of the multi-contact data, most (if not all) multi-contact analyses are done in this "binned" space (rather than `alignment` space).

## Installation
You may run the following commands in your command line to install Triplix.
```bash
pip3 install triplix

# or
python3 -m pip install triplix
```

## Extracting data:
`triplix` works in three types of data: `Concatermers`, `Tri-Alignments` and `Triplets`.
Below, you can see how you can extract each type of data.

### 1. `Concatemer` space  (*.concatemers.h5)
Provides random-access to read (i.e., `Concatemer`) level data.
In order to have access to the content of a `Concatemers` container, a handle should be initialized via:
```python
import triplix

concatemers_path = './concatemers/mESC.MC-HiC.concatemers.h5'
concatemers_container = triplix.ConcatemersContainer(file_path=concatemers_path)
```

Then, we can access the content, by requesting a specific concatemer/read index, or range of concatemer indices:
```python
print(concatemers_container[6])
# <Concatemers>
#    read_idx  chrom_num     start       end  strand  map_quality  flag  seq_start  seq_end                             read_name  read_length
# 0         6          9  28049720  28051533      -1           60  2064         22     1833  000a9e3e-5a06-4691-acf7-f71c0b707bc9         8538
# 1         6          9  27993951  27996370       1           60     0       2233     4617  000a9e3e-5a06-4691-acf7-f71c0b707bc9         8538
# 2         6          9  28001381  28003048      -1           60  2064       4602     6245  000a9e3e-5a06-4691-acf7-f71c0b707bc9         8538
# 3         6          9  28003034  28003230      -1           60  2064       6429     6621  000a9e3e-5a06-4691-acf7-f71c0b707bc9         8538
# 4         6          9  34934155  34935542       1           60  2048       6615     7929  000a9e3e-5a06-4691-acf7-f71c0b707bc9         8538
# 5         6          9  36134828  36135055      -1           42  2064       7925     8149  000a9e3e-5a06-4691-acf7-f71c0b707bc9         8538
# 6         6         15  48738095  48738498      -1           60  2064       8145     8536  000a9e3e-5a06-4691-acf7-f71c0b707bc9         8538
# 7         7          2  63927407  63930186       1           60  2048         23     2803  000a76b2-216e-4c40-b0f5-35c7ce10d30c         8151
# 8         7          2  64210922  64221347       1           60     0       2793     8134  000a76b2-216e-4c40-b0f5-35c7ce10d30c         8151


print(concatemers_container[6:9])
# <Concatemers>
#     read_idx  chrom_num      start        end  strand  map_quality  flag  seq_start  seq_end                             read_name  read_length
# 0          6          9   28049720   28051533      -1           60  2064         22     1833  000a9e3e-5a06-4691-acf7-f71c0b707bc9         8538
# 1          6          9   27993951   27996370       1           60     0       2233     4617  000a9e3e-5a06-4691-acf7-f71c0b707bc9         8538
# 2          6          9   28001381   28003048      -1           60  2064       4602     6245  000a9e3e-5a06-4691-acf7-f71c0b707bc9         8538
# 3          6          9   28003034   28003230      -1           60  2064       6429     6621  000a9e3e-5a06-4691-acf7-f71c0b707bc9         8538
# 4          6          9   34934155   34935542       1           60  2048       6615     7929  000a9e3e-5a06-4691-acf7-f71c0b707bc9         8538
# 5          6          9   36134828   36135055      -1           42  2064       7925     8149  000a9e3e-5a06-4691-acf7-f71c0b707bc9         8538
# 6          6         15   48738095   48738498      -1           60  2064       8145     8536  000a9e3e-5a06-4691-acf7-f71c0b707bc9         8538
# 7          7          2   63927407   63930186       1           60  2048         23     2803  000a76b2-216e-4c40-b0f5-35c7ce10d30c         8151
# 8          7          2   64210922   64221347       1           60     0       2793     8134  000a76b2-216e-4c40-b0f5-35c7ce10d30c         8151
# 9          8         10  103377945  103378320       1           60  2048         25      391  000a93a0-5d61-42a1-81e2-848b7b197f60         3710
# 10         8         10  105640948  105642721      -1           60    16        387     2134  000a93a0-5d61-42a1-81e2-848b7b197f60         3710
# 11         8         15   43523758   43523837      -1           38  2064       2130     2209  000a93a0-5d61-42a1-81e2-848b7b197f60         3710
# 12         8         13    4296589    4296895       1           60  2048       2205     2501  000a93a0-5d61-42a1-81e2-848b7b197f60         3710
# 13         8         19   48817930   48819166       1            1  2048       2497     3708  000a93a0-5d61-42a1-81e2-848b7b197f60         3710
```

Alternatively, one can iterate over all `concatemers`:
```python
import pandas as pd
concatemers_iter = concatemers_container.iter(return_name=True, return_length=True)
n_concatemer = len(concatemers_container)
for idx, concatemer in enumerate(concatemers_iter):
    df = pd.DataFrame(concatemer)
    print(df[['chrom_num', 'start', 'strand', 'read_name']])
    if idx > 0:
        break

#    chrom_num     start  strand                             read_name
# 0          6  19951796       1  0000b7ad-14d7-4285-a1a3-65a87eef213d
# 1          6  18571279       1  0000b7ad-14d7-4285-a1a3-65a87eef213d
# 2          6  19944712      -1  0000b7ad-14d7-4285-a1a3-65a87eef213d
# 3          6  18954688      -1  0000b7ad-14d7-4285-a1a3-65a87eef213d
# 4          6  18958868       1  0000b7ad-14d7-4285-a1a3-65a87eef213d
# 5          6  20007053      -1  0000b7ad-14d7-4285-a1a3-65a87eef213d
# 6          6  19139306       1  0000b7ad-14d7-4285-a1a3-65a87eef213d
# 7         11  74436453      -1  0000b7ad-14d7-4285-a1a3-65a87eef213d
#    chrom_num     start  strand                             read_name
# 0          5  92933191      -1  0000eea6-4554-40c3-b4ab-ecaa5cf5795b
# 1          5  23899224       1  0000eea6-4554-40c3-b4ab-ecaa5cf5795b
# 2          5  33962641      -1  0000eea6-4554-40c3-b4ab-ecaa5cf5795b
# 
```

#### Description of stored columns:
  * `read_idx`: A Concatemer index (staring from 0). All alignments originating from a particular Concatemer (i.e. sequenced read) are annotated with an identical index.
  * `chrom_num`: A numeric value for the chromosome that the current alignment is mapped to (e.g. `chr1`=1, `chr2`=2, etc.). 
    The ordered list of chromosomes is available in the HDF5 container's attributes (i.e. `concatemers_container.h5_file['concatemers'].attrs['chrom_names']`)

  * `start`: The first basepair that the alignment is mapped to in the reference genome
  * `end`: The last basepair that the alignment is mapped to in the reference genome
  * `strand`: The strand in which the alignment is mapped to
  * `map_quality`: The mapping quality that is assigned by the mapper to this alignment. Note that mappers have a different range of mapping qualities (e.g. minimap2 may assign a value between [0 - 60], while bwa-sw assigns a value between [0 - 255])
  * `flag`: A series of bit-wise flags. These bits are assigned by the mapper, following [SAM file specifications](https://doi.org/10.1093/gigascience/giab008).
  * `seq_start`: The first nucleotide over the sequenced read from which the alignment is collected from. 
  * `seq_end`: The last nucleotide over the sequenced read from which the alignment is collected from.
  * `read_name`: The name of the sequenced read (aka. `read id`) that is defined by the sequence machine.
  * `read_length`: Length of the read (in terms of basepairs) from which the alignment is originating from.

### 2. `Tri-alignment` space (*.tri-alignments.tsv.bgz):
Provides access to alignment (i.e., `tri-alignments`) level data. 
These files are essentially formatted as compressed [pairix files](https://github.com/4dn-dcic/pairix). The difference is that they contain three coordinates instead of two coordinates (as is the case for regular pairix files)

> **Note:** The tri-alignment files need to be indexed if you like to have random access to them. You can do this using `triplix index --input=input-file.tri-alignments.tsv.bgz`

An example of this usage is as follows:

```python
import triplix

tri_aln_path = './tri-alignments/GM12878.Merged.tri-alignments.tsv.bgz'
tri_container = triplix.TriAlignmentsContainer(trialn_path=tri_aln_path)

tri_alignments_iter = tri_container.fetch(chrom_a='chrY', start_a=0e6, end_a=10e6, batch_size=10)
for idx, tri_alignments in enumerate(tri_alignments_iter):
    df = tri_alignments.to_dataframe()
    print(df[['read_name', 'chrom_A', 'start_A', 'start_B', 'start_C']])
    if idx > 0:
        break
#                               read_name chrom_A  start_A  start_B  start_C
# 0  b9129419-3e9d-47ea-8ae3-bf65c468ef43    chrY    10710   363575   363575
# 1  b9129419-3e9d-47ea-8ae3-bf65c468ef43    chrY    10710   363575   449218
# 2  b9129419-3e9d-47ea-8ae3-bf65c468ef43    chrY    10710   363575   449218
# 3  689000cd-3deb-47f9-8c8d-64eb039d0be1    chrY    10710  1203147  1302472
# 4                  SRR11589401.15490287    chrY    11129  1774864  1806803
# 5                  SRR11589391.12389645    chrY    13063   493484  1644842
# 6  998d7719-0d64-4202-ba7e-0a4b9d49284e    chrY    13337   310549   672618
# 7  998d7719-0d64-4202-ba7e-0a4b9d49284e    chrY    13337   310549   754824
# 8  998d7719-0d64-4202-ba7e-0a4b9d49284e    chrY    13337   672618   754824
#                               read_name chrom_A  start_A  start_B  start_C
# 0  e7603585-2e15-423e-a26f-8b114d6bab87    chrY    13338    17122   266818
# 1                  SRR11589390.11433849    chrY    13394    13813  2515291
# 2  e7f93e28-9540-462b-817c-d8acd563b94a    chrY    13394    13844   318989
# 3                   SRR11589394.4086145    chrY    13441  1231515  2705073
# 4  429af33b-3260-4dc5-9cf3-fc7b96f0b932    chrY    13508   252336   323450
# 5  0f526116-e8fc-459b-aac9-d9d6d2843289    chrY    13584   278514   364567
# 6  0f526116-e8fc-459b-aac9-d9d6d2843289    chrY    13584   278514   366665
# 7  6589f1d9-cd7d-4cba-bfc9-06f123956157    chrY    13584   282655   440783
# 8  0f526116-e8fc-459b-aac9-d9d6d2843289    chrY    13584   364567   366665
# 9  11f46754-fbfe-4f9f-8aa6-7f03c7db48df    chrY    13584  1180971  1812799

```

#### Description of stored columns:
In the column names below, the letter `X` refers to either `A`, `B` or `C`. 
For example, by `chrom_X`, we state that each Tri-alignment contains `chrom_A`, `chrom_B` and `chrom_C` columns.
 * `chrom_X`: The chromosome on which the alignment `X` is mapped to.
 * `start_X`: The first basepair on which the alignment `X` is mapped to.
 * `end_X`: The last basepair on which the alignment `X` is mapped to.
 * `strand_X`: The strand on which the alignment `X` is mapped to.
 * `mapq_X`: The mapping quality assigned by the aligner for alignment `X`.
 * `frag_index_X`: An index that refers the order of the alignments collected from the read (sorted by their starting basepair relative to the read). For example, `frag_index_A`=1 indicates that this is the second alignment originating from the read.
 * `read_name`: Name of Concatemer (i.e., sequenced read), as present in the `Concatemers` container.
 * `read_length_nbp`: Length of the read in terms of basepairs.
 * `read_length_nfrag`: Length of the read in terms of number of alignments.
 * `experiment_name`: Name of the experiment, given by the user (or taken from the `Concatemers` filename).


### 3. `Triplet` space (*.triplets.h5):
Provides access to triplet-level data. A usage example is:

```python
import pandas as pd
import triplix

trpl_path = './triplets/GM12878.MC-HiC.hg38.triplets.h5'
trpl_obj = triplix.TripletsContainer(container_path=trpl_path)
triplets = trpl_obj.fetch(
    chrom_a='chr8', start_a=119e6, end_a=120e6,
    columns=['start_A', 'start_B', 'start_C', 'count_ABC'],
)
df = pd.DataFrame(triplets)
print(df)
# output:
#           start_A    start_B    start_C  count_ABC
# 0       119000000  119000000  119000000         73
# 1       119000000  119000000  119025000        136
# 2       119000000  119000000  119050000         82
# 3       119000000  119000000  119075000         55
# 4       119000000  119000000  119100000         54
# ...           ...        ...        ...        ...
# 136156  120000000  121950000  121975000          8
# 136157  120000000  121950000  122000000          2
# 136158  120000000  121975000  121975000          5
# 136159  120000000  121975000  122000000          7
# 136160  120000000  122000000  122000000          6
# 
# [136161 rows x 4 columns]
```

Alternatively, you may iterate over stored [chunks](https://docs.h5py.org/en/stable/high/dataset.html#chunked-storage) of triplets as follows:
```python
for triplets in trpl_obj.iter_chunks():
  print(triplets)
#        flag  start_A  start_B  start_C  distance_AB  ...
# 0         0        0        0        0            0  ...
# 1         0        0        0    25000            0  ...
# 2         0        0        0    50000            0  ...
# 3         0        0        0    75000            0  ...
# 4         0        0        0   100000            0  ...
# ...     ...      ...      ...      ...          ...  ...
```
This will iterate over all stored triplets, chunk by chunk. 
In addition, you can limit the chromosomes or columns that are retured (to improve load speed). This can be done as follows:
```python
for current_chromosome, triplets in trpl_obj.iter_chunks(chroms=['chr3'], columns=['start_A', 'start_B', 'start_C']):
  print(current_chromosome, triplets)
# chr3 Triplets <50000 x 3>:
#       start_A start_B  start_C
# 0           0       0        0
# 1           0       0    25000
# 2           0       0    50000
# 3           0       0    75000
# 4           0       0   100000
# ***       ***     ***      ***
```
Note that the `.iter_chunks()` function returns a tuple of `(current_chromosome, triplets)`.

#### Description of stored columns:
 * `flag`: A set of binary flags (in the range of [0x0000 - 0xffff]) that specify a property of each triplet:
   * `0x0000`: No flag is set. This is the default.
   * `0x0001`: At least one of the anchors coordinate of the Triplet is located out of the chromosome length.
   * `0x0002`: At least one column in the triplet has an `undefined` value.
 * `start_X`: The starting basepair on which the anchor `A` is defined on.
 * `start_B`: The starting basepair on which the anchor `B` is defined on.
 * `start_C`: The starting basepair on which the anchor `C` is defined on.
 * `distance_AB`, `distance_AC` and `distance_BC`: Distance (in terms of base pairs) between anchor `A-B`, `A-C` and `B-C`. 
 * `count_A`, `count_B`, `count_C`: Number of alignments covering anchor `A`, `B` and `C` respectively. This is simply the 1D coverage track at anchor `A`, `B` and `C` respectively.
 * `count_AB`, `count_AC`, `count_BC`: Number of pairwise contacts found between anchors `A-B`, `A-C` and `B-C`. This count is basically the number of interation found in a HiC representation of the multi-contact data.
 * `count_ABC`: Number of times a 3-way contact is found between anchors `A-B-C`.
 * The following columns are assigned after the `transformation` step of the Triplix pipeline:
   + `observed_A`, `observed_B`, `observed_C`: The `counts_A`, `counts_B` or `counts_C` after performing the transformation. The default transformation is `Gaussian`, which smooths the counts in the 3D space of cube.
   + `observed_AB`, `observed_AC`, `observed_BC`: The `count_AB`, `count_AC`, `count_BC` after performing the transformation.
   + `observed_ABC`: The `count_ABC` after performing the transformation.
 * Correction factors: The following columns are assigned after the `KDTree` construction and neighbor search steps of the Triplix pipeline. 
   For the neighbor search, different factors could be considered to perform the neighbor search. For instance:
   + `singletons`: Triplets are considered neighbors (i.e. similar), if they have similar 1D coverages across their anchors (i.e., `observed_A`, `observed_B` and `observed_C`) as well as similar pairwise anchor distances (i.e., `distance_AB`, `distance_AC` and `distance_BC`).
   + `pairs`: Triplets are considered similar if their pairwise contacts are similar (i.e., `observed_AB`, `observed_AC` and `observed_BC`) as well as their pairwise anchor distances.
   + `pairs_surround`: Triplets are similar if their pairwise contacts, pairwise anchor distances as well as their surrounding 3-way contacts (i.e., the `observed_ABC` of adjacent Triplets) are similar.
 * Based on each correction factors, several statistics are estimated. For example, in case the `pairs` correction factor is chosen:
   + `pairs.neighbors_distance_med`: The median of the K-neighbors Euclidean distance to the current triplet, in the high-dimensional space of the constructed KDTree.
   + `pairs.neighbors_distance_std`: The standard deviation of the K-neighbors Euclidean distance to the current triplet, in the high-dimensional space of the constructed KDTree.
   + `pairs.neighbors_expected_avg`: The average of `observed_ABC` across the identified similar triplets (i.e., neighbors).
   + `pairs.neighbors_expected_std`: The standard deviation of `observed_ABC` across the identified similar triplets (i.e., neighbors).
   + `pairs.enrichment`: The enrichment score calculated after comparing the observed and expected number of 3-way contacts (i.e., `observed_ABC` vs. `pairs.neighbors_expected_avg`) while considering the standard deviation of these observations (i.e., `pairs.neighbors_expected_std`)

## Drawing virtual-hic plots (experimental features):
`triplix` can be used to draw virtual-HiC plots. 
Note that this is an experimental feature. So the arguments may change in future releases.
A minimal example of doing this is as follows:

```python
from triplix.core import plot

call = {
  'chrom': 'chr8',
  'start_A': int(119.825e6),
  'start_B': int(120.100e6),
  'start_C': int(120.425e6),
}
ant_coords = [[call['start_B'] - 50e3, call['start_B'] + 75e3, call['start_C'] - 50e3, call['start_C'] + 75e3]]

plot.plot_virtual_hic(
  input_patterns=f"./GM12878.MC-HiC.hg38.triplets.h5",
  view_chrom=call['chrom'], 
  view_start=call['start_A'] - 750e3, 
  view_end=call['start_C'] + 750e3 ,
  view_point=call['start_A'],
  plot_names=(
      'count_ABC', 
      'observed_ABC', 
      'singletons.enrichment',
      'pairs.enrichment',
      'pairs_surround.enrichment',
  ),
  output_dir='./',
  output_name='virtual-hic_example.pdf',
  plot_params={"sin.*enrichment": {"annotations":ant_coords}}
)
```
The above code would produce a plot like below. Notice the black (rectangle) annotation in the middle plot which is drawn
as requested in `plot_params` argument.
![Example of virtual-HiC plot](./examples/virtual-hic_example.png)

#### Description of arguments:
The majority of the arguments are assumed to be self-explanatory, but some may not be clear
* `input_patterns`: Path to `Triplet` container.
* `plot_names`: The column in the `Triplet` container to be used in the plot.
* `plot_params`: Can be used send varied parameters to the plot (see source code for details). 
  Most importantly, you can define (using regular expressions) which plot should be annotated. Annotation format can be seen in the example above.


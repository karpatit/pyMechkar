# pyMechkar
 
Description: Utilities that help researchers in various phases of their research work. 
This package offer a function that automate the exploratory data analysis, a function for
the generation of Table 1 (required on many epidemiological papers) which can be exported
to excel. Additionally, there is a function that generates train/test random partitions 
used for model evaluation that checks for the balance of the partitions.
 
Authors: Tomas Karpati M.D.
ORCID: 0000-0003-2650-6192
[GitHub](https://github.com/karpatit/mechkar)

## Usage

### exploreData
from pyMechkar import exploreData

exploreData(df, y="Class")

### Table1

from pyMechkar.analysis import Table1

tab1 = Table1(df, y="Class")

### train_test

from pyMechkar.analysis import train_test

train, test = train_test(df, prop=0.7, seed=1)


# Computational experiments 
In this directory, you will find the data and the python code used to computationnaly evaluate FAIR-Checker. 

The file [bioschemas-dump.ttl](bioschemas-dump.ttl) contains Schema.org semantic markup associated to http://bio.tools software descriptions. It is regularly updated at [https://github.com/bio-tools/content/blob/master/datasets/bioschemas-dump.ttl](https://github.com/bio-tools/content/blob/master/datasets/bioschemas-dump.ttl). 

## Software environment
Software dependencies are specified in the [environment.yml](../binder/environment.yml) file. 
The software environment is prepared as follows :
```
git clone https://github.com/IFB-ElixirFr/fair-checker.git
cd fair-checker
conda env create --file binder/environment.yml
conda activate fair-checker-experiments
```

## Assessing metadata compliance with Bioschemas profiles and SHACL shapes 
The notebook [biotools_experimental_sudy-bioschemas.ipynb](https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/experiments/biotools_experimental_sudy-bioschemas.ipynb) describes how we evaluate te compliance of http://bio.tools software descriptions with the [Bioschemas Computational Tool profile](https://bioschemas.org/profiles/ComputationalTool/1.0-RELEASE). 


## FAIR assessment of a large collection of software descriptions   
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/IFB-ElixirFr/fair-checker/HEAD?labpath=experiments) 
#### 1. Data pre-processing 
The bioschemas dump is splitted into chunks of ... 
#### 2. FAIR assesment 
#### 3. Data visualization 
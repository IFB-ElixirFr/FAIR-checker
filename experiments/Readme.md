# Computational experiments 
In this directory, you will find the data and the python code used to computationnaly evaluate FAIR-Checker. 

The file [bioschemas-dump.ttl](bioschemas-dump.ttl) contains Schema.org semantic markup associated to http://bio.tools software descriptions. It is regularly updated at [https://github.com/bio-tools/content/blob/master/datasets/bioschemas-dump.ttl](https://github.com/bio-tools/content/blob/master/datasets/bioschemas-dump.ttl). 

## Software environment
Software dependencies are specified in the [environment.yml](../binder/environment.yml) file. 
The software environment is prepared and launched as follows :
```
git clone https://github.com/IFB-ElixirFr/fair-checker.git
cd fair-checker
conda env create --file binder/environment.yml
conda activate fair-checker-experiments
cd experiments
jupyter-notebook
```

## FAIR assessment of a large collection of software descriptions   
The notebook [biotools_25k_sudy.ipynb](https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/experiments/notebooks/biotools_25k_sudy.ipynb) describes how we evaluate FAIR metrics on 25k+ http://bio.tools software descriptions. 

## Assessing metadata compliance with Bioschemas profiles and SHACL shapes 
The notebook [biotools_experimental_sudy-bioschemas.ipynb](https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/experiments/notebooks/biotools_experimental_sudy-bioschemas.ipynb) describes how we evaluate te compliance of http://bio.tools software descriptions with the [Bioschemas Computational Tool profile](https://bioschemas.org/profiles/ComputationalTool/1.0-RELEASE). 

## Comparing the FAIRness data preservation portals
The 3 notebooks 
 - [dryad_expe_data_study.ipynb](https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/experiments/notebooks/biotools_experimental_sudy-bioschemas.ipynb) 
 - [pangaea_expe_data_study.ipynb](https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/experiments/notebooks/pangaea_expe_data_study.ipynb) 
 - [zenodo_expe_data_study.ipynb](https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/experiments/notebooks/zenodo_expe_data_study.ipynb) 
   
evalute the FAIRness of sample data entries hosted by Zenodo, Dryad, and Pangaea. 

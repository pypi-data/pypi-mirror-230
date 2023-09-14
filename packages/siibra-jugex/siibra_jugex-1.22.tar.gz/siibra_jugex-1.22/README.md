# siibra-jugex

## A toolbox for atlas-based differential analysis of gene expressions

*Authors: Big Data Analytics Group and S. Bludau, Institute of Neuroscience and Medicine (INM-1), Forschungszentrum Jülich GmbH*

Copyright 2020-2021, Forschungszentrum Jülich GmbH 

> :warning: **`siibra-jugex` is at an experimental stage.** The software is not yet fully tested. Be aware that you will likely encounter bugs.

JuGEx  (Julich-Brain Gene Expression) is an integrated framework developed to combined the AllenBrain and Julich-Brain atlases for statistical analysis of differential gene expression in the adult human brain.
The framework has been developed by S. Bludau et al. and is described in 

> Sebastian Bludau, Thomas W. Mühleisen, Simon B. Eickhoff, Michael J. Hawrylycz, Sven Cichon, Katrin Amunts. Integration of transcriptomic and cytoarchitectonic data implicates a role for MAOA and TAC1 in the limbic-cortical network. 2018, Brain Structure and Function. [https://doi.org/10.1007/s00429-018-1620-6](https://doi.org/10.1007/s00429-018-1620-6)*.

The original implementation in Matlab can be found [here](https://www.fz-juelich.de/SharedDocs/Downloads/INM/INM-1/DE/jugex.html?nn=2163780).

The basic idea of JuGExis to supplement different levels of information on brain architecture, e.g. structural and functional connectivity, brain activations, and neurotransmitter receptor density by transcriptional information to enlight biological aspects of brain organization and its diseases, spatially referring to the cytoarchitectonic Julich-Brain atlas. This allows analysis beyond approaches which rely on the traditional segregation of the brain into sulci and gyri, thereby combining functionally different microstructural areas. JuGex is publicly available to empower research from basic, cognitive and clinical neuroscience in further brain regions and disease models with regard to gene expression.

`siibra` is a Python client for interacting with "multilevel" brain atlases, which combine multiple brain parcellations, reference coordinate spaces and modalities. See [here](https://siibra.eu) for more details.
This siibra toolbox implements the JuGEx algorithm with siibra, to provide a simple and intuitive implementation in python, as well as an interactive plugin of the 3D atlas viewer of [EBRAINS](https://ebrains.eu/service/human-brain-atlas/).
The analysis is initialized with a siibra atlas object. It will check if the parcellation selected in the atlas is suitable for performing the analysis, which includes to verify that the given atlas object provides maps in the MNI ICBM 152 space. The analysis is configured by specifying some candidate genes of interest, and two regions of interest (ROI) specified by brain area names that the atlas object can resolve. Note that the siibra atlas class does fuzzy string matching to resolve region names, so you can try with a simple name of the regions to see if siibra interprets them.  Also, gene names can easily be looked up and autocompleted in siibra.gene_names.

For the gene expression data, `siibra-jugex` accesses the Allen Brain Atlas API (© 2015 Allen Institute for Brain Science. Allen Brain Atlas API. Available from: brain-map.org/api/index.html).

## Installation

`siibra-python` is available on pypi. To install the latest version, simply run `pip install siibra-jugex`.

## Quick walkthrough

To get familiar with `siibra-jugex`, we recommend to checkout the notebook in the `examples/` subfolder of this repository, which walks you throught the basic idea. You can run it live if you like by visiting mybinder: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/FZJ-INM1-BDA/siibra-jugex/master?filepath=examples%2Fsiibra-jugex.ipynb)


#### Initialize the analysis

The analysis is initialized with a `siibra` atlas object. It will check if the parcellation selected in the atlas is suitable for performing the analysis, which includes to verify that the given atlas object provides maps in the MNI ICBM 152 space. We explicitely select the Julich-Brain probabilistic cytoarchitectonic maps, and  tell the atlas to threshold the probability maps for filtering gene expressions instead of using the simplified labelled volume. 


```python
import siibra, siibra_jugex
```

>    [siibra:INFO]  Version: 0.1a1 \
     [siibra:INFO]  Configuration: siibra-0.1a1 \
     [siibra_jugex:INFO]  Version: 0.1a1


```python
atlas = siibra.atlases.MULTILEVEL_HUMAN_ATLAS
atlas.select_parcellation(siibra.parcellations.JULICH_BRAIN_CYTOARCHITECTONIC_MAPS_2_5)
atlas.threshold_continuous_maps(0.2)

jugex = siibra_jugex.DifferentialGeneExpression(atlas)
```

>    [siibra:INFO]  Multilevel Human Atlas | select "Julich-Brain Cytoarchitectonic Maps 2.5"


#### Configure the experiment with brain regions and candidate genes

The analysis is configured by specifying some candidate genes of interest, and two regions of interest (ROI) specified by brain area names that the atlas object can resolve. Note that the siibra atlas class does fuzzy string matching to resolve region names, so you can try with a simple name of the regions to see if siibra interprets them.  Also, gene names can easily be looked up and autocompleted in siibra.gene_names. 



```python
candidate_regions = ["v1 right","v2 right"]
candidate_genes = ["MAOA","TAC1"]
jugex.add_candidate_genes(candidate_genes)
jugex.define_roi1(candidate_regions[0])
jugex.define_roi2(candidate_regions[1])
```

>    [siibra:INFO]  Multilevel Human Atlas | select "Area hOc1 (V1, 17, CalcS) - right hemisphere" \
    [siibra:INFO]  Retrieving probe ids for gene MAOA


    For retrieving microarray data, siibra connects to the web API of
    the Allen Brain Atlas (© 2015 Allen Institute for Brain Science), available
    from https://brain-map.org/api/index.html. Any use of the microarray data needs
    to be in accordance with their terms of use, as specified at
    https://alleninstitute.org/legal/terms-use/.


>    [siibra:INFO]  Area hOc1 (V1, 17, CalcS) - right hemisphere: Computing mask by thresholding continuous map at 0.2. \
    [siibra:INFO]  Retrieving probe ids for gene TAC1 \
    [siibra_jugex:INFO]  12 samples found for region v1 right. \
    [siibra:INFO]  Multilevel Human Atlas | select "Area hOc2 (V2, 18) - right hemisphere" \
    [siibra:INFO]  Retrieving probe ids for gene MAOA \
    [siibra:INFO]  Area hOc2 (V2, 18) - right hemisphere: Computing mask by thresholding continuous map at 0.2. \
    [siibra:INFO]  Retrieving probe ids for gene TAC1 \
    [siibra_jugex:INFO]  11 samples found for region v2 right.


#### Run the analysis


```python
result = jugex.run(permutations=1000)
print(result['p-values'])
```

>    {'MAOA': 0.96, 'TAC1': 0.441}


The aggregated input parameters can be stored to disk.


```python
jugex.save('jugex_{}_{}.json'.format(
    "_".join(candidate_regions),
    "_".join(candidate_genes) ))
```

>    [siibra_jugex:INFO]  Exported p-values and factors to file jugex_v1 right_v2 right_MAOA_TAC1.json.


#### Look at filtered positions of microarray samples in MNI space

Let's have a look at the sample positions that have been found in the Allen atlas. Since we configured brainscapes to prefer thresholded continuous maps for region filtering over the simplified parcellation map, we also plot the probability maps here.


```python
from nilearn import plotting

for regionname in candidate_regions:
    samples = jugex.get_samples(regionname)
    region = atlas.select_region(regionname)
    pmap = atlas.selected_region.get_regional_map(
        siibra.spaces.MNI152_2009C_NONL_ASYM, 
        siibra.MapType.CONTINUOUS)    
    # we could have also used the simple parcellation map mask as follows:
    # mask = atlas.get_mask(bs.spaces.MNI_152_ICBM_2009C_NONLINEAR_ASYMMETRIC)
    display = plotting.plot_roi(pmap,cmap="jet",title=region.name)
    display.add_markers([s['mnicoord'] for s in samples.values()])
```

    
![png](images/example_12_1.png)
    


    
![png](images/example_12_2.png)
    


## Acknowledgements

This software code is funded from the European Union’s Horizon 2020 Framework
Programme for Research and Innovation under the Specific Grant Agreement No.
945539 (Human Brain Project SGA3).

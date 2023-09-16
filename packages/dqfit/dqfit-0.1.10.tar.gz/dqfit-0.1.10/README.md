## Quickstart:

[Quickstart: dqfit-python.ipynb on Google CoLab](https://colab.research.google.com/drive/11xOKc-sgaIto5wknpdDkJVWugwpM1GEH#scrollTo=ooQS2AdfejTr)

# This is designed for use in the NCQA Bulk FHIR Data Quality Pilot and Accompanied Research # 

- Brad Ryan
- Marc Overhage, MD, PhD
- Aneesh Chopra
- Mike Berger
- Ed Yuricisin
- Ben Hamlin, DrPH
- Rob Currie
- Beau Norgeot, PhD
- Arjun Sanyal
- Dede Ainbinder
- Evan Machusak
- Patrick B
- many many more

Lead Engineer:
- Parker Holcomb

## Developer Quickstart

Package should feel familiar to those familiar with `import pandas as pd` and running an `openai` or `sklearn` model:

```python 
import dqfit as dq
...
model = dq.Index.create(model="dqi-3", context="hello-world")
model.fit(fhir_resources)
```

For an interactive example see:

[Quickstart: dqfit-python.ipynb](https://colab.research.google.com/drive/11xOKc-sgaIto5wknpdDkJVWugwpM1GEH#scrollTo=ooQS2AdfejTr)

To execute the population script:


```bash
    python -m dqfit.population synthea_10 dqi-3 hello-world
```

You can set `FHIR_BASE` as described in `example.env` 

The "population_key" is the directory/prefix to where the population's FHIR is stored.

Use the `--output` to save results

```bash
    python -m dqfit.population synthea_10 dqi-3 hello-world --output . 
```

![model.result](https://github.com/clinicalqualitydata/dqfit-python/blob/main/examples/figures/fig_x_dqfit_cli.png?raw=true)


## Abstract

A pure function implementation of data quality assessment that scores “fitness for use” removes a key blocker to the success of Value Based Contracts: lack of trust in the clinical data used to compute payment. Standards such as HL7 FHIR and the USCDI provide part of the solution, however, measuring data quality must go beyond schema conformance[1]. Here we describe a linear transformation model that takes in a) a Population of FHIR Resources, and b) a set of weighted context dimensions (m) that have been “tuned” for use, where by scoring each data element by Model Dimension (M) such as Conformant, Complete, Plausible, effectively yields an (m, M)-dimensional result that enables stakeholders to empirically determine population-scales data data's clinical quality and fitness for a given context.

[1] Kahn et al 2016


# Background: The Case for High-Quality Data

**Goal**: confident prediction and effective management

**Problem**: low data quality is the enemy of prediction

**How to improve**: hold ourselves, and our partners, accountable to clinical-quality data

**Blocker**: no accountability mechanism for population scale data

**Solution**: work with industry to develop NCQA certified FHIR data quality tests kit [🎯 target process]

**Progress**: Developed a data quality index model based on Kahn [📍 You are here]

### Model Architecture

![Model Architecture](https://github.com/clinicalqualitydata/dqfit-python/blob/main/examples/figures/fig_2_model_architecture.png?raw=true)

### Results: 

"...where by scoring each data element by Model Dimension (M) such as Conformant, Complete, Plausible, effectively yields an (m, M)-dimensional result that enables stakeholders to empirically determine population-scales data data's clinical quality and fitness for a given context."

`model.result`

![model.result](https://github.com/clinicalqualitydata/dqfit-python/blob/main/examples/figures/fig_1_result.png?raw=true)

NB: Results below are created from Synthea Synthetic FHIR, are way "too perfect", and not represntative of the variances

`model.index`

A column score: `model.result['Score'].sum()`

e.g. 18.5



#### Visualizations

We believe that results as intuitive as possible, and special attention should be made to visualizing the results.

`model.visualize()`


![model.visualize](https://github.com/clinicalqualitydata/dqfit-python/blob/main/examples/figures/fig_1a_visualize.png?raw=true)


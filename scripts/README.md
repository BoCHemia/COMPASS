# Content scripts folder 
The scripts folder contains all code and instructions necessary to reproduce the models and the maps in COMPASS.
Developers can use the framework to add their own reference chemical spaces to COMPASS based on their own compound databases .

## 1. Preprocessing

For each database in COMPASS, the download and preprocessing steps are implemented and documented in the `prepare_[database].py` scripts.

## 2. Training t-SNE models

The script `train_tSNE.py` was used to train the tSNE models for each database.

## 3. Transform data for demo and paper

The script `transform.py` takes a model (reference space) as input and transforms selected (preprocessed) target spaces.

## 4. Visualisation

The `visualize_[description].py` scripts reproduce figures from the COMPASS paper (!!! insert doi !!!):

  - **Figure 1:** visualize_reference_spaces.py:    
  - **Figure 2:** visualize_[...].py:             


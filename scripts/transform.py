from modules.modeling import *
from modules.preprocessing import *

# load tSNE model object
reference_file_name = "plastchem_db_v1.01_partial"
model = load_model(reference_file_name, use_joblib=True, from_zip=False)
offset = load_model_offset(reference_file_name)

# load data to plot
datasets = [("AgroTrak", "agrotrak_zhang_2025_partial"),
            ("COCONUT", "coconut_partial"),
            ("DrugBank", "drugbank_5.1.13_partial"),
            ("PFAS", "pfas_nist_partial"),
            ("PlastChem", "plastchem_db_v1.01_partial"),
            ("ZeroPM", "zeropm_partial")
            ]

for folder_name, file_name in datasets:

    print(f"Transforming dataset: {folder_name} - {file_name}")
    
    #folder_name = "PlastChem"
    #file_name = 'plastchem_db_v1.01_partial' # enter here the name of the input data set to transform

    new_fingerprints = load_fingerprints(file_name=file_name, folder_name=folder_name)

    # transform
    coordinates = transform_target(model, new_fingerprints)
    coordinates = coordinates - offset.values # add to app.py

    save_coordinates(coordinates=coordinates,
                    folder_name=folder_name,
                    file_name=file_name,
                    reference_name=reference_file_name)


# Transforming
# AgroTrak: done
# COCONUT: done
# DrugBank: done
# PFAS: done
# PlastChem: 
# ZeroPM: done

import sys
sys.path.append("..")
from modules.modeling import *
from modules.preprocessing import *
import time

# load tSNE model object
reference_file_name = "zeropm_partial"
reference_folder_name = "ZeroPM"
model = load_model(reference_file_name)
offset = load_model_offset(reference_file_name)

# load target data to plot
datasets = [
            # ("AgroTrak", "agrotrak_zhang_2025_partial"),
            # ("COCONUT", "coconut_partial"),
            # ("DrugBank", "drugbank_5.1.13_partial"),
            ("PFAS", "pfas_nist_partial"),
            # ("PlastChem", "plastchem_db_v1.01_partial"),
            # ("ZeroPM", "zeropm_partial")
            ]
for folder_name, file_name in datasets:

    print(f"Transforming dataset: {folder_name} - {file_name}")

    new_fingerprints = load_fingerprints(file_name=file_name, folder_name=folder_name)
    # input_df = load_input_file(file_name=file_name, folder_name=folder_name)
    # new_fingerprints, new_df = calculate_fingerprints(input_df)
    # save_fingerprints(new_fingerprints, folder_name=folder_name, file_name=file_name)


    # lookup only
    start = time.time()
    # load reference data for lookup
    reference_data = load_coordinates(folder_name=reference_folder_name, file_name=reference_file_name)
    coordinates = lookup_target(new_fingerprints, reference_data)
    end = time.time()
    print(f"Lookup took {end - start} seconds")
    save_coordinates(coordinates=coordinates,
                    folder_name=folder_name,
                    file_name=file_name,
                    reference_name=reference_file_name)


    # lookup + transform
    start = time.time()
    coordinates = lookup_or_transform_target(model, new_fingerprints, offset, reference_data)
    end = time.time()
    print(f"Lookup + transform took {end - start} seconds")
    save_coordinates(coordinates=coordinates,
                    folder_name=folder_name,
                    file_name=file_name,
                    reference_name=reference_file_name)

    # transform
    start = time.time()
    coordinates = transform_target(model, new_fingerprints, offset)
    end = time.time()
    print(f"Transformation took {end - start} seconds")

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
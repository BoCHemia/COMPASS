
import sys
sys.path.append("..")
from modules.modeling import *
from modules.preprocessing import *
import time

# load t-SNE model object
reference_file_name = "coconut_partial"
reference_folder_name = "COCONUT"
model = load_model(reference_file_name)
offset = load_model_offset(reference_file_name)

MODE = 'transform'  # other options: 'lookup', 'lookup_transform'

# load target data to plot
datasets = [
            ("AgroTrak", "agrotrak_zhang_2025_partial"),
            # ("COCONUT", "coconut_partial"),
            ("DrugBank", "drugbank_5.1.13_partial"),
            # ("PFAS", "pfas_nist_partial"),
            # ("PlastChem", "plastchem_db_v1.01_partial"),
            # ("ZeroPM", "zeropm_partial"),
            ]
for folder_name, file_name in datasets:

    print(f"Transforming dataset: {folder_name} - {file_name}")

    input_df = load_input_file(file_name=file_name, folder_name=folder_name)
    new_fingerprints, new_df = calculate_fingerprints(input_df)
    save_fingerprints(new_fingerprints, folder_name=folder_name, file_name=file_name)

    # new_fingerprints = load_fingerprints(file_name=file_name, folder_name=folder_name)


    start = time.time()
    # load reference data for lookup
    if MODE == 'transform': # transform all
        coordinates = transform_target(model, new_fingerprints, offset)

    elif MODE == 'lookup': # lookup only
        reference_data = load_coordinates(folder_name=reference_folder_name, file_name=reference_file_name)
        coordinates = lookup_target(new_fingerprints, reference_data)

    elif MODE == 'lookup_transform': # lookup first, transform those not found
        reference_data = load_coordinates(folder_name=reference_folder_name, file_name=reference_file_name)
        coordinates = lookup_or_transform_target(model, new_fingerprints, offset, reference_data)
    else:
        raise ValueError(f"MODE {MODE} not supported. Set it to 'transform', 'lookup' or 'lookup_transform'")
    end = time.time()
    print(f"{MODE} took {end - start} seconds")

    # Save TSNE coordinates to output folder
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
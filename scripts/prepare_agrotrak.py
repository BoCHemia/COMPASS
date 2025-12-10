from modules.preprocessing import *

# -----------------------------
# INPUT
# -----------------------------

input_path = os.path.join(PROJECT_ROOT, "data")
temp_path = os.path.join(PROJECT_ROOT, "temp")

folder_name = "AgroTrak"
file_name = "agrotrak_zhang_2025"

# -----------------------------
# PREPROCESSING
# -----------------------------

print("Getting started ...")

df = pd.read_csv(os.path.join(input_path, folder_name, f"raw_{file_name}.csv"))
df.rename(columns={"Active ingredient, harmonized": "PREFERRED_NAME",
                   "CAS RN": "CASRN",
                   "InChIKey": "INCHIKEY",
                   }, inplace=True)
df_structures = df.dropna(subset=["INCHIKEY"]).reset_index(drop=True)

# drop duplicate INCHIKEYs?
# df_structures = df_structures.drop_duplicates(subset=["INCHIKEY"]).reset_index(drop=True)

# -----------------------------
# GET PUBCHEM DATA
# -----------------------------

print("Retrieving PubChem data ...")

output_file = os.path.join(temp_path, f"{file_name}_pubchem.csv")
pubchem = get_pubchem_data(df_structures, 'INCHIKEY', 'CASRN', 'PREFERRED_NAME', output_file)

df_pubchem = df_structures.merge(pubchem[["CID", "IUPAC", "INCHIKEY", "InChI", "SMILES"]], on="INCHIKEY", how="left")
df_pubchem.fillna({'SMILES': ''}, inplace=True)

# intermediate - without classyfire
df_pubchem = df_pubchem.drop_duplicates()  # - minimizing issue with duplicate INCHIKEYs
df_pubchem.to_csv(os.path.join(input_path, folder_name, f"input_{file_name}.csv"), index=False)

# -----------------------------
# MERGE WITH CLASSYFIRE DATA
# -----------------------------

print("Merging with Classyfire data ...")
classyfire = prepare_classyfire_data()
df_classyfire = pd.merge(df_pubchem, classyfire, on='INCHIKEY', how='left')

# intermediate - partial classyfire
df_classyfire.to_csv(os.path.join(input_path, folder_name, f"input_{file_name}_partial.csv"), index=False)

# -----------------------------
# SAVE OR REQUEST MISSING DATA
# -----------------------------

df_missing = df_classyfire[df_classyfire['Kingdom'].isna()][["INCHIKEY", "SMILES"]]

if len(df_missing)>0:
    n=2000
    n_splits = int(np.ceil(df_missing.shape[0]/n))
    splits = np.array_split(df_missing.to_numpy(), n_splits)

    out_dir = os.path.join(temp_path, "ClassyFire", folder_name, "batches_missing")
    os.makedirs(out_dir, exist_ok=True)

    # Save to .csv
    for n, subset in enumerate(splits):
        batch_path = os.path.join(out_dir, f"cf_batch_{n}.csv")
        pd.DataFrame(subset).to_csv(batch_path, index=False, header=False)

    print(f"{len(df_missing)} entries missing Classyfire data. Please run Classyfire batch mode on the files in {out_dir} and add results to raw_classyfire.csv. Then re-run this script.")

else:
    print(f"Data preparation complete. Saving input_{file_name}.csv.")
    df_classyfire.to_csv(os.path.join(input_path, folder_name, f"input_{file_name}.csv"), index=False)

    print("Shape of Pesticides dataframe:", df_classyfire.shape)

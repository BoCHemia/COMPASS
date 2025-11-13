from modules.preprocessing import *

# -----------------------------
# INPUT
# -----------------------------

input_path = os.path.join(PROJECT_ROOT, "data")
temp_path = os.path.join(PROJECT_ROOT, "temp")

folder_name = "DrugBank"
file_name = "drugbank_5.1.13"

# -----------------------------
# PREPROCESSING
# -----------------------------

print("Getting started ...")

df = pd.read_csv(os.path.join(input_path, folder_name, f"raw_{file_name}.csv"))
df.rename(columns={"Common name": "PREFERRED_NAME",
                   "CAS": "CASRN",
                   "Standard InChI Key": "INCHIKEY",
                   }, inplace=True)
df_structures = df.dropna(subset=["INCHIKEY"]).reset_index(drop=True)

# -----------------------------
# GET PUBCHEM DATA
# -----------------------------

print("Retrieving PubChem data ...")

output_file = os.path.join(temp_path, f"{file_name}_pubchem.csv")
pubchem = get_pubchem_data(df_structures, 'INCHIKEY', 'CASRN', 'PREFERRED_NAME', output_file)

df_pubchem = df_structures.merge(pubchem[["CID", "IUPAC", "INCHIKEY", "InChI", "SMILES"]], on="INCHIKEY", how="left")
df_pubchem.fillna({'SMILES': ''}, inplace=True)

# intermediate - without classyfire
df_pubchem.to_csv(os.path.join(input_path, folder_name, f"input_{file_name}_noCF.csv"), index=False)

# -----------------------------
# MERGE WITH CLASSYFIRE DATA
# -----------------------------

print("Merging with Classyfire data ...")

classyfire_raw = pd.read_csv(os.path.join(input_path, "ClassyFire", "raw_classyfire.csv"))
classyfire = classyfire_raw.drop_duplicates()
classyfire = classyfire_raw.dropna(subset="Kingdom")
classyfire.to_csv(os.path.join(input_path, "ClassyFire", "input_classyfire.csv"), index=False)

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
    print(f"Data preparation complete. Saving input_drugbank_5.1.13.csv.")
    df_classyfire.to_csv(os.path.join(input_path, folder_name, f"input_{file_name}.csv"), index=False)

    print("Shape of DrugBank dataframe:", df_classyfire.shape)

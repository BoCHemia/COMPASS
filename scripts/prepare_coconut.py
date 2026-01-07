from modules.preprocessing import *
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# -----------------------------
# INPUT
# -----------------------------

# Data: COCONUT database of natural products, version 9 (2021)
# The data was downloaded from https://zenodo.org/records/5336447 on 1/10/2025
# Citation: Sorokina and Steinbeck J Cheminform (2020), https://doi.org/10.1186/s13321-020-00424-9
# The downloaded file COCONUT4MetFrag_april.csv was renamed to raw_coconut.csv
# Training a model based on all coconut data takes ~150 mins

input_path = os.path.join(PROJECT_ROOT, "data")
output_path = os.path.join(PROJECT_ROOT, "output")
temp_path = os.path.join(PROJECT_ROOT, "temp")

folder_name = "COCONUT"
file_name = "coconut"

# -----------------------------
# PREPROCESSING
# -----------------------------

df_raw = pd.read_csv(os.path.join(input_path, folder_name, f"raw_{file_name}.csv"))
df_raw.rename(columns={"coconut_id": "COCONUT_ID",
                    "clean_smiles": "SMILES",
                   "inchikey": "INCHIKEY",
                   "inchi": "INCHI",
                   }, inplace=True)
df = df_raw[["COCONUT_ID", "INCHIKEY", "SMILES", "INCHI"]]

df.isna().sum() # no NaN in any column

# -----------------------------
# GET PUBCHEM DATA
# -----------------------------

# Warning: Coconut has >400K substances, hence this part takes ~10 days from scratch
output_file = os.path.join(temp_path, f"{file_name}_pubchem.csv")
pubchem = get_pubchem_data(df, output_file, 'INCHIKEY', search_columns=[('INCHIKEY', 'inchikey')] , resume=True)
df_pubchem = df.merge(pubchem[["CID", "IUPAC", "INCHIKEY", "PREFERRED_NAME"]], on="INCHIKEY", how="left")
df_pubchem.fillna({'PREFERRED_NAME': df_pubchem['INCHIKEY']}, inplace=True)

print("Dropping ", df_pubchem.duplicated().sum(), " duplicate rows.")
df_pubchem = df_pubchem.drop_duplicates().reset_index(drop=True)


# -----------------------------
# Standardize SMILES
# -----------------------------
df_std = standardize_structures(df_pubchem)

print("Dropping ", df_std["standardized SMILES"].isna().sum(), " records with missing structures after standardization.")
df_std = df_std.dropna(subset=["standardized SMILES"]).reset_index(drop=True)

print(df_std.duplicated(subset=["INCHIKEY"]).sum(), " duplicate INCHIKEYs found after standardization.")
print(df_std.duplicated(subset=["standardized SMILES"]).sum(), " duplicate or isomeric structures after standardization.")

# intermediate - without classyfire
# df_noCF = df_std.drop_duplicates(subset=["standardized SMILES"]).reset_index(drop=True)
df_std.to_csv(os.path.join(input_path, folder_name, f"input_{file_name}_noCF.csv"), index=False)

# -----------------------------
# MERGE WITH CLASSYFIRE DATA
# -----------------------------

print("Merging with Classyfire data ...")
classyfire = prepare_classyfire_data()
df_classyfire = pd.merge(df_std, classyfire, on='INCHIKEY', how='left')

# intermediate - partial classyfire
#df_classyfire["num_missing"] = df_classyfire.isna().sum(axis=1)
#df_classyfire = (df_classyfire.sort_values("num_missing").drop_duplicates(subset='standardized SMILES', keep="first").drop(columns="num_missing"))

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
    print(f"Data preparation complete. Saving input_coconut.csv.")

    #df_classyfire["num_missing"] = df_classyfire.isna().sum(axis=1)
    #df_classyfire = (df_classyfire.sort_values("num_missing").drop_duplicates(subset='standardized SMILES', keep="first").drop(columns="num_missing"))

    df_classyfire.to_csv(os.path.join(input_path, folder_name, f"input_{file_name}.csv"), index=False)

    print("Shape of COCONUT dataframe:", df_classyfire.shape)

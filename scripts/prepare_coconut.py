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
# GET PUBCHEM DATA -- get names
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
df_std["standardized SMILES"] = df_std["standardized SMILES"].replace('', np.nan)

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
classyfire = get_classyfire_data(df_std["INCHIKEY"])
df_classyfire = (df_std.assign(INCHIKEY14=df_std["INCHIKEY"].str[:14])
                 .merge(classyfire, on='INCHIKEY14', how='left').drop(columns='INCHIKEY14'))

# -----------------------------
# REPORT MISSING DATA
# -----------------------------

df_missing = df_classyfire[df_classyfire['Kingdom'].isna()][["INCHIKEY", "SMILES"]]

out_dir = os.path.join(temp_path, "ClassyFire")
os.makedirs(out_dir, exist_ok=True)
missing_path = os.path.join(out_dir, f"{file_name}_missing_classyfire.csv")
df_missing.to_csv(missing_path, index=False)

print(f"{len(df_missing)} of {len(df_classyfire)} entries ({len(df_missing)/len(df_classyfire):.1%}) have no ClassyFire classification. List saved in {missing_path}.")

print(f"Data preparation complete. Saving input_{file_name}.csv.")
df_classyfire.to_csv(os.path.join(input_path, folder_name, f"input_{file_name}.csv"), index=False)
print("Shape of COCONUT dataframe:", df_classyfire.shape)

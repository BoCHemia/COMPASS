from modules.preprocessing import *

# -----------------------------
# INPUT
# -----------------------------

input_path = os.path.join(PROJECT_ROOT, "data")
temp_path = os.path.join(PROJECT_ROOT, "temp")

folder_name = "PlastChem"
file_name = "plastchem_db_v1.01"

# -----------------------------
# PREPROCESSING
# -----------------------------

print("Getting started ...")

df_raw = pd.read_csv(os.path.join(input_path, folder_name, f"raw_{file_name}.csv"))
df_raw.rename(columns={"plastchem_ID": "PlastChem_ID",
                        "pubchem_name": "PREFERRED_NAME",
                        "cas_fixed": "CASRN",
                        "isomeric_smiles": "SMILES",
                        "inchi": "INCHI",
                        "inchikey": "INCHIKEY",
                        "exact_mass": "MW"}, inplace=True)

df = df_raw[["PlastChem_ID", "PREFERRED_NAME", "CASRN", "SMILES", "INCHI", "INCHIKEY", "PlastChem_lists"]]

# -----------------------------
# GET PUBCHEM DATA - missing SMILES (no additional found)
# -----------------------------

df_missing = df[df['SMILES'].isna()]

print("Missing ", len(df_missing), " SMILES.")

output_file = os.path.join(temp_path, f"{file_name}_pubchem.csv")
pubchem = get_pubchem_data(df_missing, output_file, 'PlastChem_ID', resume=False)

df_pubchem = df.merge(pubchem[["PlastChem_ID", "PREFERRED_NAME", "SMILES", "INCHI"]], on='PlastChem_ID', how='left', suffixes=("", "_fill"))

df_pubchem.fillna({'PREFERRED_NAME': df_pubchem['PREFERRED_NAME_fill'].fillna(df_pubchem["INCHIKEY"])}, inplace=True)
df_pubchem = df_pubchem.drop(columns='PREFERRED_NAME_fill')

df_pubchem.fillna({'SMILES': df_pubchem['SMILES_fill']}, inplace=True)
df_pubchem = df_pubchem.drop(columns='SMILES_fill')

df_pubchem.fillna({'INCHI': df_pubchem['INCHI_fill']}, inplace=True)
df_pubchem = df_pubchem.drop(columns='INCHI_fill')

print("Remaining missing", df_pubchem['SMILES'].isna().sum(), " SMILES.")

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
print("Shape of PlastChem dataframe:", df_classyfire.shape)

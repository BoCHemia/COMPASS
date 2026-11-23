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

df = pd.read_csv(os.path.join(input_path, folder_name, f"raw_{file_name}.csv")).reset_index()

df.rename(columns={"index": "ID",
                    "Active ingredient, harmonized": "PREFERRED_NAME",
                    "CAS RN": "CASRN",
                    "InChIKey": "INCHIKEY"}, inplace=True)

# -----------------------------
# GET PUBCHEM DATA
# -----------------------------
print("Retrieving PubChem data ...")

output_file = os.path.join(temp_path, f"{file_name}_pubchem.csv")
pubchem = get_pubchem_data(df, output_file, 'ID', resume=True)

df_pubchem = df.merge(pubchem[["ID", "IUPAC", "INCHI", "SMILES"]], on="ID", how="left")

# intermediate - without classyfire
print("Dropping ", df_pubchem.duplicated().sum(), " duplicate rows.")
df_pubchem = df_pubchem.drop_duplicates().reset_index(drop=True)
df_pubchem.to_csv(os.path.join(input_path, folder_name, f"input_{file_name}_noCF.csv"), index=False)


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
print("Shape of AgroTrak dataframe:", df_classyfire.shape)

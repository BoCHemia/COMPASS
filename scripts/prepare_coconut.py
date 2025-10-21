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

input_path = os.path.join(PROJECT_ROOT, "data", "COCONUT")
output_path = os.path.join(PROJECT_ROOT, "output")
temp_path = os.path.join(PROJECT_ROOT, "temp")

name_tag = "coconut"

input_file_name = f"raw_{name_tag}.csv"


# -----------------------------
# PREPROCESSING
# -----------------------------

df = pd.read_csv(os.path.join(input_path, input_file_name))
df.rename(columns={"clean_smiles": "SMILES",
                   "inchikey": "INCHIKEY",
                   }, inplace=True)

df_structures = df.dropna(subset=["SMILES"]).reset_index(drop=True) # should not remove anything
print(df_structures.describe())

# -----------------------------
# GET PUBCHEM DATA
# -----------------------------

output_file = os.path.join(temp_path, f"{name_tag}_pubchem.csv")
# df_structures = df_structures[:50]
# Warning: Coconut has >400K substances, hence this part takes ~10 days to run
df_pubchem = get_pubchem_data(df_structures, col_inchikey='INCHIKEY', output_file=output_file, resume=True)


# -----------------------------
# MERGE AND SAVE
# -----------------------------
# Minimal requirements: PREFERRED_NAME,INCHIKEY,SMILES
df_out = df_structures.merge(df_pubchem[["CID", "IUPAC", "INCHIKEY", "PREFERRED_NAME"]], on="INCHIKEY", how="left")
df_out.drop(columns=["coconut_id", "molecular_formula", "inchi", "coconut_id.1"], inplace=True)
df_out.fillna({'SMILES': ''}, inplace=True)
df_out.to_csv(os.path.join(input_path, f"input_{name_tag}.csv"), index=False)
print("Shape of COCONUT dataframe:", df_structures.shape)

# df_out = pd.read_csv(os.path.join(input_path, f"input_{name_tag}.csv")
# df
# print("Shape of COCONUT dataframe, only :", df_structures.shape)
from modules.preprocessing import *
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# -----------------------------
# INPUT
# -----------------------------

# Data: NIST List of Possible Per- and Polyfluoroalkyl Substances (PFAS)
# The data was downloaded from https://data.nist.gov/od/id/mds2-2387 in summer 2025
# More information on https://github.com/usnistgov/NISTPFAS/tree/main/suspectlist
# The downloaded file was renamed to raw_pfas_nist.tsv

input_path = os.path.join(PROJECT_ROOT, "data", "PFAS")
output_path = os.path.join(PROJECT_ROOT, "output")
temp_path = os.path.join(PROJECT_ROOT, "temp")

name_tag = "pfas_nist"

input_file_name = f"raw_{name_tag}.tsv"


# -----------------------------
# PREPROCESSING
# -----------------------------

df = pd.read_csv(os.path.join(input_path, input_file_name), sep='\t')
df.rename(columns={"CHEMICAL_NAME": "PREFERRED_NAME",
                   }, inplace=True)
df_structures = df.dropna(subset=["INCHIKEY"]).reset_index(drop=True)

# -----------------------------
# GET PUBCHEM DATA
# -----------------------------
# What do we really need here --> minimum data requirements?
# Suggestion: PREFERRED_NAME,INCHIKEY,SMILES    Optional: CASRN,CID,IUPAC,InChI
# output_file = os.path.join(temp_path, f"{name_tag}_pubchem.csv")
# df_pubchem = get_pubchem_data(df_structures, 'INCHIKEY', 'CASRN', 'PREFERRED_NAME',
#                               output_file, resume=False)

# -----------------------------
# MERGE AND SAVE
# -----------------------------

# df_out = df_structures.merge(df_pubchem[["CID", "IUPAC", "INCHIKEY", "InChI", "SMILES"]], on="INCHIKEY", how="left")
df_out = df_structures[["PREFERRED_NAME", "INCHIKEY", "SMILES"]]
df_out.fillna({'SMILES': ''}, inplace=True)
df_out.to_csv(os.path.join(input_path, f"input_{name_tag}.csv"), index=False)
print("Shape of PFAS dataframe:", df_out.shape)
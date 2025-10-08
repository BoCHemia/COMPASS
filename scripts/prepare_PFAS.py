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

name_tag = "pfas_nist"

input_file_name = f"raw_{name_tag}.tsv"


# -----------------------------
# PREPROCESSING
# -----------------------------

df = pd.read_csv(os.path.join(input_path, input_file_name), sep='\t')
df.rename(columns={"CHEMICAL_NAME": "PREFERRED_NAME",
                   }, inplace=True)
df_structures = df.dropna(subset=["SMILES"]).reset_index(drop=True)


# -----------------------------
# MERGE AND SAVE
# -----------------------------
# Minimal requirements: PREFERRED_NAME,INCHIKEY,SMILES
df_out = df_structures[["PREFERRED_NAME", "INCHIKEY", "SMILES"]]
df_out.fillna({'SMILES': ''}, inplace=True)
df_out.to_csv(os.path.join(input_path, f"input_{name_tag}.csv"), index=False)
print("Shape of PFAS dataframe:", df_out.shape)
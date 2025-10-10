from modules.preprocessing import *
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# -----------------------------
# INPUT
# -----------------------------

# Data: ZeroPM database of marketed chemicals
# The data was downloaded via https://pubchem.ncbi.nlm.nih.gov/source/25168 on 10/10/2025
# Query for ZeroPM substances :
# --> https://pubchem.ncbi.nlm.nih.gov//#query=Sg3v6Dv9XkFpa1xy3goVVMyEgOSUWaHQ2_W6nMDkqJ3A_ZQ&selected_id_type=cid
# Query for ZeroPM compounds :
# --> https://www.ncbi.nlm.nih.gov/pccompound?cmd=HistorySearch&hinit=true&query_key=8&WebEnv=MCID_68e8e425746347fdcf94f5e6
# The 140,161 ZeroPM substances were linked to 137,915 unique PubChem compounds (due to duplicate CID entries in ZeroPM list)
# Link to git repository: github.com/ZeroPM-H2020/global-chemical-inventory-database
# The downloaded file PubChem_compound_cache_46RGTSiBTT16E8UKR3KMLFXwgJC3R6Z-3Fu9MsdKrzPHU5M.csv was renamed to raw_zeropm.csv
# Citation: to be added

input_path = os.path.join(PROJECT_ROOT, "data", "ZeroPM")
output_path = os.path.join(PROJECT_ROOT, "output")
temp_path = os.path.join(PROJECT_ROOT, "temp")

name_tag = "zeropm"

input_file_name = f"raw_{name_tag}.csv"


# -----------------------------
# PREPROCESSING
# -----------------------------

df = pd.read_csv(os.path.join(input_path, input_file_name))
df_structures = df.dropna(subset=["SMILES"]).reset_index(drop=True) # should not remove anything
print(df_structures.describe())


# -----------------------------
# SAVE
# -----------------------------
# Minimal requirements: PREFERRED_NAME,INCHIKEY,SMILES
df_structures = df_structures.rename(columns = {"Name": "PREFERRED_NAME",
                                                "IUPAC_Name": "IUPAC",
                                                "InChIKey": "INCHIKEY",
                                                "InChI": "INCHI_STRING",
                                                })
df_out = df_structures[["PREFERRED_NAME", "IUPAC", "INCHIKEY", "SMILES", "Molecular_Formula", "INCHI_STRING"]]
df_structures.to_csv(os.path.join(input_path, f"input_{name_tag}.csv"), index=False)
print("Shape of ZeroPM dataframe:", df_structures.shape)
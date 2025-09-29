from modules.preprocessing import *

# -----------------------------
# INPUT
# -----------------------------

input_path = "data/DrugBank/"
output_path = "output/"
temp_path = "temp/"

input_file_name = "raw_drugbank_5.1.13.csv"

# -----------------------------
# PREPROCESSING
# -----------------------------

df = pd.read_csv(os.path.join(input_path, input_file_name))
df.rename(columns={"Common name": "PREFERRED_NAME",
                   "CAS": "CASRN",
                   "Standard InChI Key": "INCHIKEY",
                   }, inplace=True)
df_structures = df.dropna(subset=["INCHIKEY"]).reset_index(drop=True)

# -----------------------------
# GET PUBCHEM DATA
# -----------------------------

output_file = os.path.join(temp_path, "drugbank_5.1.13_pubchem.csv")
df_pubchem = get_pubchem_data(df_structures, 'INCHIKEY', 'CASRN', 'PREFERRED_NAME', output_file, resume=False)

# -----------------------------
# MERGE AND SAVE
# -----------------------------

df_out = df_structures.merge(df_pubchem[["CID", "IUPAC", "INCHIKEY", "InChI", "SMILES"]], on="INCHIKEY", how="left")
df_out.fillna({'SMILES': ''}, inplace=True)
df_out.to_csv(os.path.join(input_path, "input_drugbank_5.1.13.csv"), index=False)

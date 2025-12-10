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

input_path = os.path.join(PROJECT_ROOT, "data")
temp_path = os.path.join(PROJECT_ROOT, "temp")

folder_name = "ZeroPM"
file_name = "zeropm"


# -----------------------------
# PREPROCESSING
# -----------------------------

df = pd.read_csv(os.path.join(input_path, folder_name, f"raw_{file_name}.csv"))
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
df_structures.to_csv(os.path.join(input_path, folder_name, f"input_{file_name}_noCF.csv"), index=False)

# -----------------------------
# MERGE WITH CLASSYFIRE DATA
# -----------------------------

print("Merging with Classyfire data ...")
classyfire = prepare_classyfire_data()
df_classyfire = pd.merge(df_structures, classyfire, on='INCHIKEY', how='left')

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

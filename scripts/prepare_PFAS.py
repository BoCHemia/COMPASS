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

input_path = os.path.join(PROJECT_ROOT, "data")
temp_path = os.path.join(PROJECT_ROOT, "temp")

folder_name = "PFAS"
file_name = "pfas_nist"

# -----------------------------
# PREPROCESSING
# -----------------------------

df_raw = pd.read_csv(os.path.join(input_path, folder_name, f"raw_{file_name}.tsv"), sep='\t')
df_raw.rename(columns={"CHEMICAL_NAME": "PREFERRED_NAME",
                   }, inplace=True)
df = df_raw[["SUSPECTID", "PREFERRED_NAME", "INCHIKEY", "SMILES", "INCHI"]]

df.isna().sum() # no NaN in any column

print("Dropping ", df.duplicated().sum(), " duplicate rows.")
df = df.drop_duplicates().reset_index(drop=True)

# -----------------------------
# Standardize SMILES
# -----------------------------
df_std= standardize_structures(df)
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
    print(f"Data preparation complete. Saving input_pfas_nist.csv.")

    #df_classyfire["num_missing"] = df_classyfire.isna().sum(axis=1)
    #df_classyfire = (df_classyfire.sort_values("num_missing").drop_duplicates(subset='standardized SMILES', keep="first").drop(columns="num_missing"))

    df_classyfire.to_csv(os.path.join(input_path, folder_name, f"input_{file_name}.csv"), index=False)

    print("Shape of PFAS dataframe:", df_classyfire.shape)

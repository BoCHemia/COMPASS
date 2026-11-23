from modules.preprocessing import *
from pathlib import Path
import re
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# -----------------------------
# INPUT
# -----------------------------

# Data: ClassyFire classifications (classyfire.v4.tsv) and ChemOnt ontology (ChemOnt_2_1.obo)
# Source: https://doi.org/10.5281/zenodo.20514155, version v4 (June 2, 2026)
# classyfire.v4.tsv: one row per InChIKey (~73 million rows, ~24.5 GB). The column chemont_tree_json holds
# the ChemOnt ids of [Kingdom, Superclass, Class, Subclass, Direct parent]. Levels that are not assigned
# are either 'null' or repeat the deepest assigned node.
# ChemOnt_2_1.obo: ChemOnt ontology (version 2.1), used to translate ChemOnt ids to class names.
#
# Output: input_classyfire.parquet, a look-up table with one row per first InChIKey block
# (first 14 characters, connectivity layer) and the most frequent classification (Kingdom to Subclass)
# among all InChIKeys sharing this block (e.g. stereoisomers, isotopologues, protonation states).

input_path = os.path.join(PROJECT_ROOT, "data")
folder_name = "ClassyFire"

hierarchy = ["Kingdom", "Superclass", "Class", "Subclass"]

# -----------------------------
# COUNT CLASSIFICATIONS PER FIRST INCHIKEY BLOCK
# -----------------------------

print("Reading classyfire.v4.tsv ...")
reader = pv.open_csv(
    os.path.join(input_path, folder_name, "classyfire.v4.tsv"),
    read_options=pv.ReadOptions(block_size=256 << 20),
    parse_options=pv.ParseOptions(delimiter="\t", quote_char=False),
    convert_options=pv.ConvertOptions(include_columns=["inchikey", "chemont_tree_json"]),
)

counts = []
for batch in reader:
    inchikey14 = pc.utf8_slice_codeunits(batch.column("inchikey"), 0, 14)
    # keep the first four levels (Kingdom to Subclass): "[0,12,3909,324,1095]" -> "0,12,3909,324"
    tree4 = pc.replace_substring_regex(batch.column("chemont_tree_json"),
                                       r"^\[([^,]*,[^,]*,[^,]*,[^,]*),.*$", r"\1")
    counts.append(pa.table({"INCHIKEY14": inchikey14, "tree4": tree4})
                  .group_by(["INCHIKEY14", "tree4"]).aggregate([("tree4", "count")]))

counts = (pa.concat_tables(counts)
          .group_by(["INCHIKEY14", "tree4"]).aggregate([("tree4_count", "sum")]))

# -----------------------------
# MOST FREQUENT CLASSIFICATION PER FIRST INCHIKEY BLOCK
# -----------------------------

# ties are resolved reproducibly by the (alphabetically) first ChemOnt id string
counts = counts.sort_by([("INCHIKEY14", "ascending"), ("tree4_count_sum", "descending"),
                         ("tree4", "ascending")])
inchikey14 = counts.column("INCHIKEY14").to_numpy(zero_copy_only=False)
is_first = np.r_[True, inchikey14[1:] != inchikey14[:-1]]
majority = counts.filter(pa.array(is_first))

print(f"{counts.num_rows:,} combinations of first InChIKey block and classification; "
      f"{majority.num_rows:,} unique first InChIKey blocks.")

# -----------------------------
# CHEMONT IDS TO NAMES
# -----------------------------

with open(os.path.join(input_path, folder_name, "ChemOnt_2_1.obo"), encoding="utf-8") as f:
    terms = f.read().split("[Term]")[1:]
chemont = {int(re.search(r"^id: CHEMONTID:(\d+)", t, re.M).group(1)):
           re.search(r"^name: (.*)$", t, re.M).group(1).strip() for t in terms}

ids = majority.column("tree4").to_pandas().str.split(",", expand=True)
ids = pd.DataFrame({level: pd.to_numeric(ids[i], errors="coerce")  # 'null' -> NaN
                    for i, level in enumerate(hierarchy)})

# levels that repeat a higher level are not assigned -> NaN
for i in range(1, len(hierarchy)):
    row_mask = ids[hierarchy[:i]].eq(ids[hierarchy[i]], axis=0).any(axis=1)
    ids.loc[row_mask, hierarchy[i]] = np.nan

missing_ids = set(ids.stack().astype(int)) - set(chemont)
if missing_ids:
    raise ValueError(f"ChemOnt ids not found in ChemOnt_2_1.obo: {sorted(missing_ids)}")

classyfire = pd.DataFrame({"INCHIKEY14": majority.column("INCHIKEY14").to_pandas()})
for level in hierarchy:
    classyfire[level] = ids[level].map(chemont).astype("category")

# -----------------------------
# SAVE
# -----------------------------

classyfire.to_parquet(os.path.join(input_path, folder_name, "input_classyfire.parquet"),
                      index=False, compression="zstd", row_group_size=1_000_000)

print("Saving input_classyfire.parquet.")
print("Shape of ClassyFire look-up table:", classyfire.shape)

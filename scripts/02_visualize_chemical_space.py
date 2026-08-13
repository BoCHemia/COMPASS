import sys
sys.path.append(r"C:\global-chemical-space")

from modules.modeling import *
from modules.visualizing import *

# Load reference space (ZeroPM)
reference_folder = 'ZeroPM'
reference_file = 'zeropm_partial'
reference_coordinates = load_coordinates(reference_folder, reference_file)

# Load YOUR compounds mapped onto the reference
input_folder = 'input'
input_file = '20260420_input_unclassified'
new_coordinates = load_coordinates(folder_name=input_folder, file_name=input_file, reference_data=reference_file)

# ── Enrich coordinates with Source and Compartments from input CSV ─────────────
input_csv = pd.read_csv(r"C:\global-chemical-space\data\input\compiled_datasheet_final.csv")
new_coordinates = new_coordinates.merge(
    input_csv[["INCHIKEY", "Source", "Compartments"]],
    on="INCHIKEY",
    how="left"
)

# Add dummy CASRN column to avoid the hardcoded hover_data error
reference_coordinates["CASRN"] = ""

# ── Compartment filter ────────────────────────────────────────────────────────
# Set to None to load all compartments, or specify a list of compartments to include.
# Example: COMPARTMENT_FILTER = ["Air", "Water"]
COMPARTMENT_FILTER = None  # <-- edit this line

if COMPARTMENT_FILTER is not None:
    before = len(new_coordinates)
    new_coordinates = new_coordinates[
        new_coordinates["Compartments"].isin(COMPARTMENT_FILTER)
    ]
    after = len(new_coordinates)
    print(f"Compartment filter applied: {COMPARTMENT_FILTER}")
    print(f"  Compounds before filter: {before:,}")
    print(f"  Compounds after filter:  {after:,}")
else:
    print("No compartment filter applied — all compartments loaded.")

# Print available compartments (useful for deciding what to filter on)
print(f"\nCompartments present in data:\n  {sorted(new_coordinates['Compartments'].dropna().unique())}")

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\nTotal compounds visualized: {len(new_coordinates):,}")
print(f"Reference space compounds:  {len(reference_coordinates):,}")

# ── Colour option ─────────────────────────────────────────────────────────────
COLOR_BY = "Kingdom"   # change to "Compartments" or "Source" as needed

# ── Plot ──────────────────────────────────────────────────────────────────────
figure = chemical_space_plot_grey(reference_coordinates, opacity=0.5)
figure = map_input_data(
    figure,
    new_coordinates,
    nametag="My compounds",
    hover_name="PREFERRED_NAME",
    hover_data=["INCHIKEY", "SMILES", "Source", "Compartments", "Kingdom"],
    column_for_color_map=COLOR_BY
)
figure.show()
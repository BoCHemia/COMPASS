import streamlit as st


st.set_page_config(
    page_title="COMPASS app",
    page_icon="🧭",
    layout="wide"
)

st.title("🧭 COMPASS app")
st.markdown("""
COMPASS (**COMPA**rative chemical **S**pace **S**ystem) is an interactive tool for visualizing,
navigating, and comparing chemical spaces.

The application allows users to map chemical datasets onto harmonized reference spaces,
helping to locate and explore chemical data sets in relation to known chemical landscapes.

You can provide your own data set or select from pre-defined target spaces.
""")

st.divider()

# -------------------------------------------------------------------------------------
# Getting Started
# -------------------------------------------------------------------------------------

st.header("🚀 Getting started")


with st.expander("1️⃣ Select a reference chemical space", expanded=False):
    st.markdown("""
Available reference spaces include:

- **DrugBank** – pharmaceuticals and drug-like molecules
- **PFAS** – per- and polyfluoroalkyl substances
- **PlastChem** – plastic-related chemicals
- **ZeroPM**
- **COCONUT** – natural products
- **AgroTrak** – agrochemicals

The selected reference space defines the landscape onto which target compounds are visualized.
""")

with st.expander("2️⃣ Select target chemicals"):
    st.markdown("""
Target compounds can be:

- A predefined dataset
- Your own dataset (full version only: see https://github.com/BoCHemia/COMPASS)

Target compounds are projected into the selected reference space and displayed alongside the reference chemicals.
""")

with st.expander("3️⃣ Generate the mapping"):
    st.markdown("""
After selecting a reference and target dataset:

✅ Click **Get chemical space mapping**

COMPASS will calculate the 2D coordinates and generate the visualization.
""")

st.divider()

# -------------------------------------------------------------------------------------
# Main Visualization
# -------------------------------------------------------------------------------------

st.header("🗺️ Chemical Space Map")

st.markdown("""
The main visualization is an interactive two-dimensional map of chemical space. 
Chemically similar structures tend to be clustered together.
""")

col1, col2 = st.columns(2)

with col1:
    left = st.container(border=True)
    left.write("""
**Reference compounds**

• Displayed as circles  
• Grey by default  
• Can be colored by taxonomy or similarity
""")

with col2:
    right = st.container(border=True)
    right.write("""
**Target compounds**

• Displayed as diamonds  
• Black/white by default  
• Can be colored independently
""")

st.markdown("""Tick the dark mode box if your browser runs in dark mode.""")
st.divider()

# -------------------------------------------------------------------------------------
# Display Controls
# -------------------------------------------------------------------------------------

st.header("🎨 Display Controls")

with st.expander("Dataset Coloring", expanded=True):
    st.markdown("""
**Choose a dataset to customize coloring**:
""")

    st.markdown("""
By default, Classyfire classes are provided for coloring:

- Kingdom
- Superclass
- Class
- Subclass

When mapping your own data, columns in the uploaded table are available for coloring in addition.
""")

with st.expander("Advanced Display Settings"):
    st.markdown("""
Open **Display settings → Advanced** to customize marker settings.

Control 
- **marker size** 
- **opacity** 
- **color palette**
independently for both reference and target compounds.

""")

st.divider()

# -------------------------------------------------------------------------------------
# Molecule Inspection
# -------------------------------------------------------------------------------------

st.header("🔍 Molecule Inspection")

st.markdown("""
Enable **Visualize selected molecule** to show structure of selected molecule.

Displayed information includes:
- Structure image
- Preferred name
- SMILES
- InChIKey
- Dataset origin
""")

st.divider()

# -------------------------------------------------------------------------------------
# Similarity
# -------------------------------------------------------------------------------------

st.header("🧪 Similarity Analysis (Full Version)")

st.markdown("""
Similarity calculations are available only in the full version of COMPASS.
""")

with st.expander("Nearest-Neighbor Similarity"):
    st.markdown("""
Enable **Include similarity calculation** to compute nearest-neighbor similarity metrics.

The analysis compares:
- Target compounds against reference compounds
- Target compounds against other target compounds
""")

with st.expander("Similarity Parameters"):
    st.markdown("""
### Number of nearest neighbors (k)

Examples:

- **k = 1** → closest neighbor only
- **k = 5** → average of five neighbors
- **k = 10** → broader neighborhood

### Similarity threshold

Three options are available:

- None
- Default
- Custom

Thresholds can be used to classify compounds as being inside or outside a desired similarity domain.
""")

with st.expander("Additional Similarity Visualizations"):
    st.markdown("""
When similarity calculations are enabled, COMPASS generates:

- Similarity distribution histograms
- Threshold-based pie charts (when threshold is selected)
- Similarity coloring on the chemical space map 
""")

st.divider()

# -------------------------------------------------------------------------------------
# Treemap
# -------------------------------------------------------------------------------------

st.header("🌳 ClassyFire Treemap")

st.markdown("""
COMPASS can visualize the taxonomic composition of datasets using a hierarchical treemap.
""")

st.markdown("""
Required columns:

- Superclass
- Class
- Subclass
""")

st.markdown("""
Treemaps help users:

- Assess chemical diversity
- Compare datasets
- Identify dominant chemical classes
""")

st.divider()

# -------------------------------------------------------------------------------------
# User Dataset Upload
# -------------------------------------------------------------------------------------

st.header("📂 Upload Your Own Dataset")

st.markdown("""
Available only in the full version.
""")

with st.expander("Required File Format", expanded=True):
    st.markdown("""
Input files must be CSV files containing at least:

- `SMILES`
- `PREFERRED_NAME`
""")

    st.code(
        """PREFERRED_NAME,SMILES
Caffeine,CN1C(=O)N(C)c2ncn(C)c2C1=O
Aspirin,CC(=O)OC1=CC=CC=C1C(=O)O""",
        language="text"
    )

with st.expander("Optional data", expanded=True):
    st.markdown("""
Additional data columns may be provided, including:

- "CASRN"
- "INCHIKEY"
- ClassyFire classes: "Kingdom", "Superclass", "Class", "Subclass"
- Any other columns with categorical or continuous data

Additional columns can later be used for coloring and filtering.
""")

st.divider()

# -------------------------------------------------------------------------------------
# Demo vs Full version
# -------------------------------------------------------------------------------------

st.header("⚠️ Demo vs full version")

st.warning("""
The public demo version contains a subset of COMPASS functionality.
""")

st.markdown("""
Features are currently only in the full version:

- Uploading custom datasets including
    - Generation of new coordinate mappings
    - Providing your own ClassyFire annotations (e.g., if ClassyFire coverage by COMPASS is not satisfactory)
- Similarity calculations
""")

st.divider()

# -------------------------------------------------------------------------------------
# Privacy
# -------------------------------------------------------------------------------------

st.header("🔒 Data Privacy")

st.markdown("""
When running the full version locally:

- Uploaded files remain on your machine
- User data, calculated TSNE coordinates and ClassyFire classifications are stored in `data/_USER/`
""")

st.divider()

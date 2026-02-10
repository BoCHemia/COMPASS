from modules.preprocessing import *
from modules.modeling import *
from modules.visualizing import *

from openTSNE.sklearn import TSNE #as TSNE_sklearn
#from openTSNE.tsne import TSNE

import matplotlib.colors as mcolors


# -----------------------------
# INPUT
# -----------------------------

input_file_name = "data_market_tsne.csv"
col_smiles = "SMILES"
col_index = "INCHIKEY"
suffix = "_pc"  # to append to output file names

input_path = "data/"
output_path = "output/"

# -----------------------------
# PREPROCESSING
# -----------------------------

# Standardization
df = pd.read_csv(os.path.join(input_path, input_file_name))
df['standardized SMILES'] = standardize_smiles_df(df, col_smiles)

# Fingerprint caculation
fingerprints = calculate_descriptors_morgan_df(df, 'standardized SMILES', radius=2, fpSize=1024)
df_fingerprints = pd.concat([df, fingerprints], axis=1)
fps = np.array(df_fingerprints.iloc[:, -1024:].astype('bool'))

# -----------------------------
# MODELLING
# -----------------------------
hyperparameters = dict(n_components=2, perplexity=100, n_iter=2000, learning_rate='auto', neighbors='pynndescent', initialization='pca', metric='jaccard', random_state=42,  n_jobs=-1, verbose=True)

# ORIGINAL FIT 
tsne = TSNE(**hyperparameters)
df_tsne_fit = pd.DataFrame(tsne.fit_transform(fps), columns=['TSNE1', 'TSNE2'])
df_tsne_fit.index = df_fingerprints[col_index]
df_tsne_fit.to_csv(os.path.join(output_path, "df_tsne_fit_{suffix}.csv".format(suffix=suffix)), index=True)

# TRANSFORM
df_tsne_transform = pd.DataFrame(tsne.transform(fps), columns = ['TSNE1', 'TSNE2'])
df_tsne_transform.index = df_fingerprints[col_index]
df_tsne_transform.to_csv(os.path.join(output_path, "df_tsne_transform_{suffix}.csv".format(suffix=suffix)), index=True)

# -----------------------------
# VISUALIZATION
# -----------------------------

# ORIGINAL FIT
df_tsne_fit = pd.merge(df.drop(columns=['TSNE1', 'TSNE2']), df_tsne_fit, on=col_index) 

top15 = df_tsne_fit.groupby('Superclass').count()['TSNE1'].sort_values(ascending=False).index[:15]
df_tsne_fit['Superclass (top 15)'] = df_tsne_fit['Superclass'].where(df_tsne_fit['Superclass'].isin(top15), 'Other')

hue_order = top15.sort_values().to_list() + ['Other']
palette = ['darkslategrey', 'teal', 'aquamarine', 'darkred', 'orangered', 'mediumpurple', 'darkorchid',
            'mediumblue', 'royalblue', 'skyblue', 'darkgoldenrod', 'darkorange', 'gold',  'lightpink', 'hotpink',
            'lightgrey']

palette_hex = [mcolors.to_hex(c) for c in palette]
color_map = dict(zip(hue_order, palette_hex)) 

fig = plot_chemical_space(df_tsne_fit, 'Superclass (top 15)', color_map)
fig.update_layout(
    paper_bgcolor='white',
    plot_bgcolor='white',
    font_color='black'
)

fig.write_html(os.path.join(output_path, 'img_chemical_space_fit{suffix}.html'.format(suffix=suffix)))

# TRANSFORM
df_tsne_transform = pd.merge(df.drop(columns=['TSNE1', 'TSNE2']), df_tsne_transform, on=col_index)

top15 = df_tsne_transform.groupby('Superclass').count()['TSNE1'].sort_values(ascending=False).index[:15]
df_tsne_transform['Superclass (top 15)'] = df_tsne_transform['Superclass'].where(df_tsne_transform['Superclass'].isin(top15), 'Other')

hue_order = top15.sort_values().to_list() + ['Other']
palette = ['darkslategrey', 'teal', 'aquamarine', 'darkred', 'orangered', 'mediumpurple', 'darkorchid',
            'mediumblue', 'royalblue', 'skyblue', 'darkgoldenrod', 'darkorange', 'gold',  'lightpink', 'hotpink',
            'lightgrey']

palette_hex = [mcolors.to_hex(c) for c in palette]
color_map = dict(zip(hue_order, palette_hex)) 

fig = plot_chemical_space(df_tsne_transform, 'Superclass (top 15)', color_map)
fig.update_layout(
    paper_bgcolor='white',
    plot_bgcolor='white',
    font_color='black'
)

fig.write_html(os.path.join(output_path, 'img_chemical_space_transform{suffix}.html'.format(suffix=suffix)))

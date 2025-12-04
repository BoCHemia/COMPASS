from modules.modeling import *
from modules.preprocessing import *
from modules.visualizing import *
from sklearn import metrics
import seaborn as sns

# surrogate model based on zeropm
folder_name = 'ZeroPM'
file_name =  'zeropm'

# print
# zeropm_fingerprints = load_fingerprints(file_name)
# m1, m2 = build_surrogate_model(folder_name, file_name, df_fingerprints = zeropm_fingerprints)
# save_surrogate_model(m1, m2, file_name)

m1, m2 = load_surrogate_model(file_name)

# test on nist_pfas
file_name_test = 'pfas_nist'
folder_name_test = 'PFAS'
test_fingerprints = load_fingerprints(file_name_test)
coordinates_surrogate = transform_target_surrogate(m1, m2, test_fingerprints)

# load tsne coordinates
tsne_model_file = 'ZeroPM'

# tsne_model = load_model(tsne_model_file)
# coordinates_tsne = transform_target(tsne_model, test_fingerprints)
# save_coordinates(coordinates_tsne, 'input', file_name_test, reference_data="ZeroPM")
coordinates_tsne = load_coordinates( 'input', file_name_test, reference_data="ZeroPM")

# map coordinates based on inchikeys
coordinates_tsne.rename(columns={'TSNE1':'TSNE1_original', 'TSNE2':'TSNE2_original'}, inplace=True)
coordinates_surrogate.rename(columns={'TSNE1': 'TSNE1_surrogate', 'TSNE2': 'TSNE2_surrogate'}, inplace=True)
df = coordinates_tsne.merge(coordinates_surrogate, on='INCHIKEY')
df.dropna(subset=['TSNE1_original','TSNE1_surrogate','TSNE1_surrogate','TSNE2_surrogate'], inplace=True)

# tsne 1
rmse_1 = metrics.root_mean_squared_error(df['TSNE1_original'], df['TSNE1_surrogate'])
r2_1 = metrics.r2_score(df['TSNE1_original'], df['TSNE1_surrogate'])

# tsne 2
rmse_2 = metrics.root_mean_squared_error(df['TSNE2_original'], df['TSNE2_surrogate'])
r2_2 = metrics.r2_score(df['TSNE2_original'], df['TSNE2_surrogate'])

print('RMSE:', rmse_1, rmse_2,
      '\nR2:', r2_1, r2_2)

sns.scatterplot(df, x='TSNE1_original', y='TSNE1_surrogate')
plt.show()

sns.scatterplot(df, x='TSNE2_original', y='TSNE2_surrogate')
plt.show()


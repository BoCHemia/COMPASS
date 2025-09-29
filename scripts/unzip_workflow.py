import zipfile
import pickle

def unzip_and_load_pkl():
    with zipfile.ZipFile(os.path.join("..", "temp","data_market_trained_tSNE.zip")) as z:
        # List files
        print(z.namelist())

        # Grab the first (and only) entry
        info = z.infolist()[1]

        # with z.read(info) as f:
        #     print(type(f))
        
        #     # obj = pickle.load(f)  

        f = z.open(info)
        print(type(f))
        
        obj = pickle.load(f)
    return obj


pkl = unzip_and_load_pkl()
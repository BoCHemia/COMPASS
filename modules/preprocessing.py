import os
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
import pubchempy as pcp
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from rdkit.Chem import rdFingerprintGenerator
from rdkit.Chem.MolStandardize import rdMolStandardize



# -----------------------------
# Data and model loading
# -----------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent 

def load_training_array(filename, use_subset=False, subset_n=6000):

    """
    Loads the von Borries training fingerprints, converts to boolean,
    optionally subsets, and caches the boolean array.

    """
    # load fingerprints
    fingerprints_file = os.path.join(PROJECT_ROOT, "data", "fingerprints", filename + '_fingerprints.csv')
    fingerprints = pd.read_csv(fingerprints_file)

    # ensure that there is not NA in the data
    assert fingerprints.isna().sum().sum() == 0, "There are NaNs in the data"
    print("Loaded fingerprints data size:", fingerprints.shape)

    # obtain training data
    X = np.array(fingerprints).astype('bool')  # full data
    X = X[:subset_n] if use_subset else X
    print("Size of training array:", X.size)

    return X

def preprocess_data(filename):
    """
    Wrapper function to load dataframe, standardize SMILES, and calculate fingerprints
    :param filename: name tag
    :return: pandas DataFrame of fingerprints
    """
    input_df_path = os.path.join(PROJECT_ROOT, "data", "input", filename + ".csv")
    df = pd.read_csv(input_df_path)
    df['standardized SMILES'] = standardize_smiles_df(df, 'SMILES')
    df_fingerprints = pd.DataFrame(calculate_descriptors_morgan_df(df, 'standardized SMILES'))
    return df_fingerprints

def save_fingerprints(fingerprints, filename):
    """
    Save fingerprints to .csv file
    :param fingerprints: fingerprints dataframe
    :param filename: name tag
    """

    out_dir = os.path.join(PROJECT_ROOT, "temp", "fingerprints")
    os.makedirs(out_dir, exist_ok=True)

    fingerprints_df_path = os.path.join(out_dir, filename + "_fingerprints.csv")
    fingerprints.to_csv(fingerprints_df_path)
    print("Fingerprints saved to ", fingerprints_df_path)

def load_fingerprints(filename):
    """

    :param filename:
    :return:
    """
    fingerprints_df_path = os.path.join(PROJECT_ROOT, "temp", "fingerprints", filename + "_fingerprints.csv")
    fingerprints = pd.read_csv(fingerprints_df_path)
    return fingerprints

# -----------------------------
# Structures and features
# -----------------------------


def get_pubchem_data(df, col_inchikey, col_cas, col_name, output_file, resume=False):
    """ Fetches IUPAC name, SMILES, and InChI strings from PubChem for a list of chemicals 
    provided in dataframe with their InChIKeys, CAS numbers and chemical names, saving regularly to avoid data loss.
    Allows to resume from last saved compound.

    Inputs
    ----------
    df : pandas dataframe, mandatory
        Dataframe containing a list of chemicals with columns for CAS numbers and chemical names
    col_inchikey: str, mandatory
        column name containing InChI keys
    col_cas: str, mandatory
        column name containing CAS numbers
    col_name: str, mandatory
        column name containing chemical names
    output_file: str, mandatory
        path to output csv file
    resume: bool, optional, default=False
        if True and output_file exists, resume from last saved compound

    Outputs
    ----------
    df_out: pandas dataframe
        dataframe with CAS, chemical name, foundby (CAS or name), PubChem ID (CID), IUPAC name, 
        isomeric and caonical SMILES, InChI key and InChI strings
    """

    if resume & os.path.exists(output_file):
        df_out = pd.read_csv(output_file)
        done_set = set(df_out[col_inchikey])
        print(f"Resuming: {len(done_set)} compounds already processed.")
    else:
        df_out = pd.DataFrame(columns=[col_cas, col_name, col_inchikey, 'Found by', 'CID', 'IUPAC', 'InChI', 'SMILES'])
        done_set = set()


    for i, (cas, name, inchikey) in enumerate(zip(df[col_cas], df[col_name], df[col_inchikey])):

        if inchikey in done_set:  
            continue

        compound_data = None
        foundby = None

        try:
            results = pcp.get_compounds(inchikey, 'inchikey')
            if results:
                compound_data, foundby = results[0], 'InChIKey'
        except:
            pass

        if compound_data is None:
            try:
                results = pcp.get_compounds(cas, 'name')
                if results:
                    compound_data, foundby = results[0], 'CAS'
            except:
                pass

        if compound_data is None:
            try:
                results = pcp.get_compounds(name, 'name')
                if results:
                    compound_data, foundby = results[0], 'name'
            except:
                pass

        if compound_data:
            row = pd.DataFrame([[cas, name, inchikey, foundby,
                                compound_data.cid,
                                compound_data.iupac_name,
                                compound_data.inchi,
                                compound_data.smiles]],
                            columns=df_out.columns)
        else:
            row = pd.DataFrame([[cas, name, inchikey, "not found", None, None, None, None]],
                            columns=df_out.columns)

        df_out = pd.concat([df_out, row], ignore_index=True)

        if i % 50 == 0:
            df_out.to_csv(output_file, index=False)
            print(f"Progress saved at index {i} ({cas}, {name})")

        time.sleep(0.2)

    df_out.to_csv(output_file, index=False)

    return df_out


def myMolFromSmiles(smiles):
    """ Function to create mol object from SMILES performing partial sanitization when necessary

    Inputs
    ----------
    smiles : str, mandatory
        SMILES string

    Outputs
    ----------
    mol: object
        RDKit mol object

    """
    
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:  # try partial sanitization
        try:
            mol = Chem.MolFromSmiles(smiles, sanitize=False)
            mol.UpdatePropertyCache(strict=False)
            Chem.SanitizeMol(mol,
                             Chem.SanitizeFlags.SANITIZE_FINDRADICALS | Chem.SanitizeFlags.SANITIZE_KEKULIZE |
                             Chem.SanitizeFlags.SANITIZE_SETAROMATICITY | Chem.SanitizeFlags.SANITIZE_SETCONJUGATION |
                             Chem.SanitizeFlags.SANITIZE_SETHYBRIDIZATION | Chem.SanitizeFlags.SANITIZE_SYMMRINGS,
                             catchErrors=True)
            print('Partial sanitization: ' + smiles)
        except:
            print('Partial sanitization failed - return none: ' + smiles)

    return mol


def remove_stereochemistry(smiles):
    """ Support function to remove stereochemical information from SMILES

    Inputs
    ----------
    smiles : str, mandatory
        SMILES string

    Outputs
    ----------
    res_smiles: str
        SMILES string without stereochemical information

    """

    mol = myMolFromSmiles(smiles)

    if mol is None:
        res_smiles = ""
    else:
        Chem.RemoveStereochemistry(mol) 
        res_smiles = Chem.MolToSmiles(mol)

    return res_smiles


def create_tautomer_smiles(smiles):
    """ Function creates tautomer SMILES 

    Inputs
    ----------
    smiles : str, mandatory
        SMILES string

    Outputs
    ----------
    tautomer_smiles : str
        tautomer SMILES string

    """

    if myMolFromSmiles(smiles) is None:
        new_mol = None
    else:
        mod_smi = Chem.MolToSmiles(myMolFromSmiles(smiles))
        new_mol = myMolFromSmiles(mod_smi)

    if new_mol is None:  # return empty string if still no mol
        print('No mol: ' + smiles)
        return ''
    else:
        # Tautomerize
        try:
            enumerator = rdMolStandardize.TautomerEnumerator()
            new_mol = enumerator.Canonicalize(new_mol)
        except:
            print('No tautomerization:' + smiles)


        tautomer_smiles = Chem.MolToSmiles(new_mol)
        return tautomer_smiles


def standardize_smiles(smiles, tautomerize=False):
    """ Wrapper function that standardizes SMILES by removing stereochemistry and optional tautomerizing 
    Inputs
    ----------
    smiles : str, mandatory
        The SMILES string

    Outputs
    ----------
    smiles_std: str,
        The standardized SMILES string
    """ 
    if tautomerize:
        smiles = create_tautomer_smiles(smiles)

    smiles_std = remove_stereochemistry(smiles)

    return smiles_std


def standardize_smiles_df(df, col_smiles, **kwargs):
    """ Wrapper function that calculates Morgan fingerprints for a series of SMILES

    Inputs
    ----------
    df : pandas dataframe, mandatory
        The dataframe containing the series of SMILES
    col_smiles: string, mandatory
        The column name containing the SMILES
    **kwargs: optional
        Pass in any arguments taken by rdkit.Chem.rdMolDescriptors.GetMorganFingerprintAsBitVect such as radius and nBits

    Outputs
    ----------
    series of standardized SMILES
    """

    smiles_df = df[col_smiles].apply(standardize_smiles, **kwargs)
    return smiles_df


def calculate_descriptors_morgan(smiles, **kwargs):
    """ Wrapper function that calculates Morgan fingerprints for a single SMILES

    Inputs
    ----------
    smiles : str, mandatory
        The SMILES string
    **kwargs: optional
        Pass in any arguments taken by rdkit.Chem.rdMolDescriptors.GetMorganFingerprintAsBitVect such as radius and fpSize

    Outputs
    ----------
    array of calculated Morgan fingerprints
    """

    mol = myMolFromSmiles(smiles)
    gen = rdFingerprintGenerator.GetMorganGenerator(**kwargs)
    fp = gen.GetFingerprint(mol)
    arr = np.zeros((fp.GetNumBits(),), dtype=bool)
    DataStructs.ConvertToNumpyArray(fp, arr)

    return arr


def calculate_descriptors_morgan_df(df, col_smiles, **kwargs):
    """ Wrapper function that calculates Morgan fingerprints for a series of SMILES

    Inputs
    ----------
    df : pandas dataframe, mandatory
        The dataframe containing the series of SMILES
    col_smiles: string, mandatory
        The column name containing the SMILES
    **kwargs: optional
        Pass in any arguments taken by rdkit.Chem.rdMolDescriptors.GetMorganFingerprintAsBitVect such as radius and nBits

    Outputs
    ----------
    dataframe of calculated Morgan fingerprints
    """

    d = df[col_smiles].apply(calculate_descriptors_morgan, **kwargs)
    return pd.DataFrame.from_records(d)
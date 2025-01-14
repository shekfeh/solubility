#!/usr/bin/env python
# Auhor: Pawel Gniewek, 2019-


import sys
import logging

import numpy as np
from rdkit.Chem import AllChem
from sklearn.ensemble import RandomForestRegressor
from rdkit import Chem
from rdkit.Chem import MACCSkeys

from predictor import Predictor
from model_utils import get_training_data
from model_utils import parse_args

class RFPredictor(Predictor):
    """
    TODO:
    """

    def __init__(self, fp_type='ecfp', radius=3, fp_length=1024, n_ests=500):
        super().__init__()
        self._name = "RFRegressor"
        self._fp_type = fp_type
        self._fp_r = radius
        self._fp_length = fp_length
        self._n_estimators = n_ests
        self.model = None

    def fit(self, smiles_list, logS_list):
        X = self.smiles_to_fps(smiles_list)
        y = [logS for logS in logS_list]

        self.model = RandomForestRegressor(n_estimators=self._n_estimators, random_state=1123, max_features="auto")
        self.model.fit(X, y)

    def smiles_to_fps(self, smiles_list):
        fps = []
        for smiles in smiles_list:
            molecule = Chem.MolFromSmiles(smiles)
            if self._fp_type == 'ecfp':
                fp = AllChem.GetMorganFingerprintAsBitVect(molecule, self._fp_r, nBits=self._fp_length, useChirality=False)
            elif self._fp_type == 'maccs':
                fp = MACCSkeys.GenMACCSKeys(molecule)
            else:
                logging.error("No valid fingerpring specified")
                sys.exit(1)

            fps.append(fp.ToBitString())

        fps = np.array(fps)
        fps = np.array([list(fp) for fp in fps], dtype=np.float32)
        return fps

    def predict(self, smiles_list):
        X = self.smiles_to_fps(smiles_list)
        y_pred = self.model.predict(X)
        return y_pred


if __name__ == "__main__":
    args = parse_args()
    train_file = args.input
    results_file = args.output

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    smiles_list, logS_list = get_training_data(train_file)
    rf_regression = RFPredictor()
    print(rf_regression.train(smiles_list, logS_list, fname=results_file, y_randomization=args.y_rand))
    rf_regression.plot()

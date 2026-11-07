import numpy as np                                   # tableaux
import pytest                                        # tests
from sklearn.metrics import mean_squared_error       # RMSE de référence (scikit-learn)

from modele import rmse                              # ta fonction
from exceptions import DonneeInvalideError


def test_rmse_egal_scikit_learn():
    # cas usuel : ton RMSE NumPy = celui de scikit-learn
    reels = np.array([10.0, 20.0, 30.0])
    predits = np.array([12.0, 18.0, 33.0])
    attendu = np.sqrt(mean_squared_error(reels, predits))
    assert rmse(reels, predits) == pytest.approx(attendu)


def test_rmse_nul_si_predictions_parfaites():
    # cas limite : aucune erreur -> RMSE = 0
    valeurs = np.array([5.0, 10.0, 15.0])
    assert rmse(valeurs, valeurs) == pytest.approx(0.0)


def test_rmse_tailles_differentes():
    # cas d'erreur : tableaux de tailles différentes
    with pytest.raises(DonneeInvalideError):
        rmse(np.array([1.0, 2.0]), np.array([1.0]))
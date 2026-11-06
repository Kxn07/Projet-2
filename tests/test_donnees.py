import pytest
from donnees import VariableNumerique, VariableCategorielle, JeuDeDonnees
from exceptions import DonneeInvalideError

def test_valider_annee_hors_intervalle():
    variable = VariableNumerique("year", 1996, 2026)
    with pytest.raises(DonneeInvalideError):
        variable.valider("2060")

def test_valider_annee_valide():
    variable = VariableNumerique("year", 1996, 2026)
    resultat = variable.valider("2018")
    assert resultat == 2018.0

def test_valider_champ_vide():
    variable = VariableNumerique("year", 1996, 2026)
    with pytest.raises(DonneeInvalideError):
        variable.valider("")

def test_valider_texte_non_numerique():
    variable = VariableNumerique("year", 1996, 2026)
    with pytest.raises(DonneeInvalideError):
        variable.valider("abc")

def test_categorielle_valeur_inconnue():
    variable = VariableCategorielle("fuelType", ["Petrol", "Diesel"])
    with pytest.raises(DonneeInvalideError):    
        variable.valider("Electrique")

def test_str_variable_numerique():
    variable = VariableNumerique("year", 1996, 2026)
    assert str(variable) == "year (numérique, 1996 à 2026)"
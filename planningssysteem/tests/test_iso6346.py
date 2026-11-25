"""Test 1 uit het testplan: containernummer volgens ISO 6346."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.rules.iso6346 import bereken_controlecijfer, controleer_containernummer


def test_voorbeeld_uit_opdracht_is_geldig():
    uit = controleer_containernummer("CSQU3054383")
    assert uit.geldig
    assert bereken_controlecijfer("CSQU305438") == 3


def test_verkeerd_controlecijfer_is_ongeldig():
    uit = controleer_containernummer("CSQU3054384")
    assert not uit.geldig
    assert "moet 3 zijn" in uit.melding


@pytest.mark.parametrize("nummer, stukje_melding", [
    ("CSQU305438", "11 tekens"),        # te kort
    ("CSQU30543833", "11 tekens"),      # te lang
    ("CSQA3054383", "Verkeerde opbouw"),  # 4e letter moet U, J of Z zijn
    ("CS1U3054383", "Verkeerde opbouw"),  # cijfer op de plek van een letter
    ("", "11 tekens"),
])
def test_foute_invoer_geeft_duidelijke_fout(nummer, stukje_melding):
    uit = controleer_containernummer(nummer)
    assert not uit.geldig
    assert stukje_melding in uit.melding


def test_spaties_en_kleine_letters_mogen():
    uit = controleer_containernummer("csqu 305438-3")
    assert uit.geldig and uit.genormaliseerd == "CSQU3054383"


@given(st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=3, max_size=3),
       st.sampled_from("UJZ"), st.integers(0, 999999))
def test_elk_berekend_nummer_is_geldig_en_elk_ander_cijfer_niet(eigenaar, cat, serie):
    basis = f"{eigenaar}{cat}{serie:06d}"
    goed = bereken_controlecijfer(basis)
    assert controleer_containernummer(basis + str(goed)).geldig
    fout = (goed + 1) % 10
    assert not controleer_containernummer(basis + str(fout)).geldig

import pytest
import pandas as pd
import spacy

from zix.understandability import (
    _additional_metrics,
    _punctuate_lines,
    _extract_features,
    _calculate_score,
    get_zix,
    get_cefr,
)

nlp_pipeline = spacy.load("de_core_news_sm")

cols = [
    "sentence_length_mean",
    "rix",
    "vocab_a1",
    "vocab_a2",
    "vocab_b1",
    "common_word_score",
    "rix_cws",
    "rix_vocab_a1",
    "rix_vocab_a2",
    "rix_vocab_b1",
    "slm_cws",
    "slm_vocab_a1",
    "slm_vocab_a2",
    "slm_vocab_b1",
]
values = [[7.0, 2.0, 1.0, 1.0, 1.0, 9.84, 19.68, 2.0, 2.0, 2.0, 68.88, 7.0, 7.0, 7.0]]
test_data = pd.DataFrame(values, columns=cols)


def test_additional_metrics():
    doc = nlp_pipeline("Das ist ein einfacher Satz auf Deutsch.")
    doc = _additional_metrics(doc)
    for feature in cols:
        assert doc.user_data[feature]


def test_punctuate_lines():
    assert (
        _punctuate_lines(
            """
            Das ist ein Satz ohne Punkt
            Das ist ein    Satz mit     überflüssigen     Leerzeichen
            Dies ist eine Liste ohne Punkte am Ende:
                - Ich gehe spazieren
                - Die Sonne scheint
                • Es ist warm"""
        )
        == """Das ist ein Satz ohne Punkt. Das ist ein Satz mit überflüssigen Leerzeichen. Dies ist eine Liste ohne Punkte am Ende:. Ich gehe spazieren. Die Sonne scheint. Es ist warm."""
    )


def test_extract_features():
    text = """Das ist ein einfacher Satz auf Deutsch."""
    result = _extract_features(text)
    assert result.shape == (1, 14)
    assert isinstance(result, pd.DataFrame)
    assert result.values.tolist() == [
        [7.0, 2.0, 1.0, 1.0, 1.0, 9.84, 19.68, 2.0, 2.0, 2.0, 68.88, 7.0, 7.0, 7.0]
    ]


def test_calculate_score():
    assert _calculate_score(test_data) == 7.979886902287279


def test_get_zix():
    text = "Das ist ein einfacher Text. Der Text sollte mehr als ZIX 0 ergeben. Ich gehe spazieren. Die Sonne scheint. Es ist warm."
    score = get_zix(text)
    assert score > 0
    # Check if an error is raised when the text is too long.
    with pytest.raises(ValueError) as excinfo:
        get_zix("Wort " * 300_000)


def test_get_cefr():
    with pytest.raises(TypeError) as excinfo:
        get_cefr("5")
    with pytest.raises(TypeError) as excinfo:
        get_cefr(None)
    with pytest.raises(TypeError) as excinfo:
        get_cefr("Dies ist ein Text, der kein ZIX Score ist.")
    assert get_cefr(4.0) == "A1"
    assert get_cefr(2.0) == "A2"
    assert get_cefr(1.0) == "B1"
    assert get_cefr(-2) == "B2"
    assert get_cefr(-4) == "C1"
    assert get_cefr(-10) == "C2"
    assert get_cefr(-20) == "C2"

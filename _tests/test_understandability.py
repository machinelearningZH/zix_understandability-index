import pytest
import pandas as pd
from zix import get_zix, get_cefr
from zix.understandability import _punctuate_lines, _calculate_score, _extract_features


def test_punctuate_lines():
    """Test the _punctuate_lines function with various input scenarios."""
    # Test basic punctuation addition
    assert _punctuate_lines("Das ist ein Satz ohne Punkt") == "Das ist ein Satz ohne Punkt."
    
    # Test multiple spaces removal
    assert _punctuate_lines("Das ist ein    Satz mit     überflüssigen     Leerzeichen") == "Das ist ein Satz mit überflüssigen Leerzeichen."
    
    # Test bullet point removal with dash
    assert _punctuate_lines("- Ich gehe spazieren") == "Ich gehe spazieren."
    
    # Test bullet point removal with bullet
    assert _punctuate_lines("• Es ist warm") == "Es ist warm."
    
    # Test multi-line with list
    input_text = """
            Das ist ein Satz ohne Punkt
            Das ist ein    Satz mit     überflüssigen     Leerzeichen
            Dies ist eine Liste ohne Punkte am Ende:
                - Ich gehe spazieren
                - Die Sonne scheint
                • Es ist warm"""
    expected = "Das ist ein Satz ohne Punkt. Das ist ein Satz mit überflüssigen Leerzeichen. Dies ist eine Liste ohne Punkte am Ende:. Ich gehe spazieren. Die Sonne scheint. Es ist warm."
    assert _punctuate_lines(input_text) == expected
    
    # Test sentences that already have punctuation
    assert _punctuate_lines("Das ist ein Satz.") == "Das ist ein Satz."
    assert _punctuate_lines("Ist das ein Satz?") == "Ist das ein Satz?"
    assert _punctuate_lines("Das ist toll!") == "Das ist toll!"
    
    # Test empty lines are removed
    assert _punctuate_lines("Erste Zeile\n\n\nZweite Zeile") == "Erste Zeile. Zweite Zeile."


def test_calculate_score():
    """Test the _calculate_score function with various feature DataFrames."""
    # Test with moderate features
    features = pd.DataFrame({
        "sentence_length_mean": [7.0],
        "rix": [2.0],
        "vocab_a1": [0.7],
        "vocab_a2": [0.8],
        "vocab_b1": [0.9],
        "common_word_score": [0.05]
    })
    score = _calculate_score(features)
    assert isinstance(score, (float, int))
    assert -10 <= score <= 10
    
    # Test with high complexity features (should result in lower/negative score)
    complex_features = pd.DataFrame({
        "sentence_length_mean": [15.0],
        "rix": [5.0],
        "vocab_a1": [0.3],
        "vocab_a2": [0.5],
        "vocab_b1": [0.7],
        "common_word_score": [0.03]
    })
    complex_score = _calculate_score(complex_features)
    assert isinstance(complex_score, (float, int))
    assert -10 <= complex_score <= 10
    
    # Test with low complexity features (should result in higher/positive score)
    simple_features = pd.DataFrame({
        "sentence_length_mean": [5.0],
        "rix": [1.0],
        "vocab_a1": [0.85],
        "vocab_a2": [0.90],
        "vocab_b1": [0.95],
        "common_word_score": [0.07]
    })
    simple_score = _calculate_score(simple_features)
    assert isinstance(simple_score, (float, int))
    assert -10 <= simple_score <= 10
    assert simple_score >= complex_score  # Simple text should have higher or equal score
    
    # Test that score is clipped to valid range
    # Even with extreme values, score should be within [-10, 10]
    extreme_features = pd.DataFrame({
        "sentence_length_mean": [100.0],
        "rix": [50.0],
        "vocab_a1": [0.0],
        "vocab_a2": [0.0],
        "vocab_b1": [0.0],
        "common_word_score": [0.0]
    })
    extreme_score = _calculate_score(extreme_features)
    assert -10 <= extreme_score <= 10
    assert extreme_score == -10  # Should be clipped to minimum


def test_extract_features():
    """Test the _extract_features function with various German texts."""
    # Test with a simple German sentence
    text = "Das ist ein einfacher Satz."
    result = _extract_features(text)
    
    # Check return type and shape
    assert isinstance(result, pd.DataFrame)
    assert result.shape[0] == 1  # One row
    assert result.shape[1] == 6  # Six features
    
    # Check that all expected columns are present
    expected_columns = ["sentence_length_mean", "rix", "vocab_a1", "vocab_a2", "vocab_b1", "common_word_score"]
    for col in expected_columns:
        assert col in result.columns
    
    # Check that all values are numeric and not null
    assert result.notnull().all().all()
    for col in expected_columns:
        assert isinstance(result[col].iloc[0], (int, float))
    
    # Test with a longer text with multiple sentences
    long_text = "Das ist ein Text. Er hat mehrere Sätze. Die Sätze sind unterschiedlich lang."
    result_long = _extract_features(long_text)
    assert isinstance(result_long, pd.DataFrame)
    assert result_long.shape == (1, 6)
    assert result_long.notnull().all().all()
    
    # Test with text containing complex words (should have higher RIX)
    complex_text = "Die Wirtschaftsentwicklung und Innovationsförderung sind entscheidend."
    result_complex = _extract_features(complex_text)
    assert result_complex["rix"].iloc[0] > 0
    
    # Test with very simple text (high A1 vocabulary ratio)
    simple_text = "Ich bin hier. Du bist da. Wir sind zusammen."
    result_simple = _extract_features(simple_text)
    assert result_simple["vocab_a1"].iloc[0] > 0
    
    # Test that sentence_length_mean is calculated correctly for known text
    known_text = "Das ist gut."  # 3 words (excluding punctuation)
    result_known = _extract_features(known_text)
    assert result_known["sentence_length_mean"].iloc[0] == 3.0


def test_get_zix():
    text = "Das ist ein einfacher Text. Der Text sollte mehr als ZIX 0 ergeben. Ich gehe spazieren. Die Sonne scheint. Es ist warm."
    score = get_zix(text)
    assert score > 0
    # Check if an error is raised when the text is too long.
    with pytest.raises(ValueError):
        get_zix("Wort " * 300_000)


def test_get_cefr():
    # Test None input
    assert get_cefr(None) is None
    
    # Test valid ZIX scores
    assert get_cefr(4.0) == "A1"
    assert get_cefr(2.0) == "A2"
    assert get_cefr(1.0) == "B1"
    assert get_cefr(-2) == "B2"
    assert get_cefr(-4) == "C1"
    assert get_cefr(-10) == "C2"
    assert get_cefr(-20) == "C2"
    
    # Test edge cases
    assert get_cefr(5.0) == "A1"
    assert get_cefr(3.0) == "A2"
    assert get_cefr(0) == "B1"
    assert get_cefr(-1) == "B2"
    assert get_cefr(-3) == "C1"

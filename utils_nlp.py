# These utilities are only used in the notebooks.
# The functions for the pip installable package are in the respective package folder ("zix").

import pandas as pd
import re
import spacy
from spacy.language import Language
import textdescriptives as td

SOURCE_DIR = "zix/data/"

FEATURE_COLS = [
    "sentence_length_std",
    "vocab_a1",
    "vocab_a2",
    "vocab_b1",
    "common_word_score",
    "rix",
]

cefr_vocab = pd.read_parquet(SOURCE_DIR + "cefr_vocab.parq")
vocab_a1 = cefr_vocab[cefr_vocab["level"] == "A1"]["lemma_ch"].values
vocab_a2 = cefr_vocab[cefr_vocab["level"] == "A2"]["lemma_ch"].values
vocab_b1 = cefr_vocab[cefr_vocab["level"] == "B1"]["lemma_ch"].values

word_scores = pd.read_parquet(SOURCE_DIR + "word_scores_final_0728.parq")
word_scores = dict(zip(word_scores["lemma"], word_scores["score"]))


@Language.component("additional_metrics")
def additional_metrics(doc):
    """Add additional metrics to doc.user_data."""

    # Calculate ratio of words that are in CEFR vocabularies.
    doc_len = len([token for token in doc if not token.is_punct and not token.like_num])

    # Counters for B1, A2, A1 vocabularies.
    vocab_scores = [0, 0, 0]

    # Counter for common word score.
    doc_word_scores = 0

    for token in doc:
        lemma = token.lemma_.lower()

        # A word in vocab A1 is also part of the vocabulary of A2 and B1.
        if lemma in vocab_a1:
            vocab_scores[0] += 1  # B1
            vocab_scores[1] += 1  # A2
            vocab_scores[2] += 1  # A1
        elif lemma in vocab_a2:
            vocab_scores[0] += 1  # B1
            vocab_scores[1] += 1  # A2
        elif lemma in vocab_b1:
            vocab_scores[0] += 1  # B1

        if lemma in word_scores:
            doc_word_scores += word_scores[lemma]

    # Normalize scores by document length.
    vocab_scores = list(map(lambda x: x / doc_len, vocab_scores))
    doc_word_scores = doc_word_scores / doc_len

    doc.user_data["vocab_b1"] = vocab_scores[0]
    doc.user_data["vocab_a2"] = vocab_scores[1]
    doc.user_data["vocab_a1"] = vocab_scores[2]
    doc.user_data["common_word_score"] = doc_word_scores / 1000

    return doc


nlp_pipeline = spacy.load("de_core_news_sm")
nlp_pipeline.add_pipe("textdescriptives/descriptive_stats")
nlp_pipeline.add_pipe("textdescriptives/readability")
nlp_pipeline.add_pipe("additional_metrics")


def extract_text_features(text):
    """Extract text features from text."""
    doc = nlp_pipeline(text)
    row_metrics = td.extractors.extract_dict(
        doc,
        metrics=[
            "descriptive_stats",
            "readability",
        ],
        include_text=False,
    )
    for metric in [
        "vocab_a1",
        "vocab_a2",
        "vocab_b1",
        "common_word_score",
    ]:
        row_metrics[0][metric] = doc.user_data[metric]
    return pd.DataFrame.from_dict(row_metrics)


def punctuate_lines(text):
    """Add a dot to lines that do not end with a dot.
    Remove bullet points, multiple spaces and line breaks.

    Args:
        text (str): The text to be fixed.

    Returns:
        str: The fixed text with proper punctuation.
    """
    lines = text.splitlines()
    lines = [x.strip() for x in lines]
    lines = [x for x in lines if x != ""]
    lines_punct = []
    for line in lines:
        # Properly punctuate lines.
        if line[-1] not in [".", "?", "!"]:
            line = line + "."
        # Remove bullet points.
        if line[0] in ["-", "•"]:
            line = line[1:].strip()
        # Remove multiple spaces.
        line = re.sub(r"\s+", " ", line)
        lines_punct.append(line)

    return " ".join(lines_punct)
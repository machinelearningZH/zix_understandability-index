# Software Design Review — `zix` package

**Lens:** John Ousterhout, *A Philosophy of Software Design*. Working code is not enough; the goal is to reduce apparent complexity — change amplification, cognitive load, and unknown-unknowns.

**Scope:** the installable package only — [zix/understandability.py](zix/understandability.py), [zix/__init__.py](zix/__init__.py), [pyproject.toml](pyproject.toml), and [_tests/test_understandability.py](_tests/test_understandability.py). Notebooks and `utils_*.py` were read only to understand how the index was built; they are out of scope.

**What the module is.** A genuinely *deep* module: a tiny interface (`get_zix(text) -> float`, `get_cefr(score) -> str`) hiding a substantial implementation (spaCy pipeline + CEFR vocabularies + a fitted scaler and Ridge regressor). The shape is right. The problems are at the seams: the public surface, import-time behavior, and the failure contract.

---

## Findings (ordered by severity)

```text
zix/__init__.py:1 - Information hiding / distinct layers - The package root exports nothing; the public functions live in zix.understandability, so every caller writes `from zix.understandability import get_zix`, leaking the internal module name. The test does `from zix import get_zix` (the natural form) and fails. - All tests fail to *collect* (the README's `uv run pytest _tests/` is broken right now); and renaming/splitting understandability.py would break every caller. The package name `zix` — the natural stable interface — is dead. - Re-export `get_zix`/`get_cefr` from `__init__.py` and define `__all__`; demote `zix.understandability` to a private detail.
```

```text
zix/understandability.py:24-46,122-134 - Pull complexity down / unknown-unknowns / security - Importing the module unpickles two models, reads two parquet files, loads spaCy, registers a global pipeline component, and — if the model is missing — runs `os.system("pip install <wheel>")`. The model version `3.8.0` is hardcoded here *and* in pyproject.toml. - `import zix` is slow, can raise, mutates the environment, and cannot be deferred or mocked; the shell-out is an operational/supply-chain smell (AGENTS.md flags unjustified shell execution); the os.system branch is dead-but-dangerous because the model is already a declared dependency. - Move resource/model/pipeline construction behind a lazily-initialized scorer (e.g. an `@lru_cache` `_get_scorer()` built on first `get_zix` call). Delete the os.system fallback; rely on the declared dependency and raise one clear, actionable error if the model is absent.
```

```text
zix/understandability.py:199-241 - Define errors out of existence / pull complexity down - get_zix has four inconsistent failure contracts: non-string -> warn + None (211); empty string -> warn + None (~216); too long -> raise ValueError (230); null features -> silent None (238); short text -> warn + return a score (221). The docstring promises `float`. - Callers cannot trust the return type: they must None-check every call, catch ValueError, and optionally parse warnings. The None values then force get_cefr to special-case None too, spreading the same complexity across two functions. The README formats the result as `f"{score:.1f}"` with no guard — one None slips through and it crashes. - Pick one contract. Treat empty/whitespace/non-string like the too-long case (raise ValueError) or normalize them away; keep "too short" as the *only* warning (still return a score); make null-features impossible or raise. Then the type is honestly `float` and get_cefr needs no None branch.
```

```text
zix/understandability.py:14-20,137-152,182-196 - Information hiding / names and comments - FEATURES is a dict whose values are always None, used only for its ordered keys. _extract_features builds a DataFrame in that key order; _calculate_score's `scaler.transform` depends on that column order matching training. Reordering FEATURES silently produces wrong scores — a safety-critical invariant with no comment, obscured by the dict-of-None idiom. - A future edit that adds or reorders a feature corrupts predictions with no error; the None values mislead readers into thinking the dict carries data. - Replace with an explicit ordered tuple, e.g. `FEATURE_NAMES = (...)`, plus a one-line comment: "order must match the fitted scaler/regressor." Optionally assert the order or pass names to the model.
```

```text
zix/understandability.py:189,244-266 - Names and comments / change amplification - _calculate_score spreads/shifts the prediction with magic constants (`* 2.0 + 5.5`, clip ±10) whose comment ("shift it to a range from -10 to 10") does not match the arithmetic; get_cefr maps the score with separate magic thresholds (4/2/0/-2/-4). The two sets of constants must stay coordinated but live apart with no link. - Nobody can retune the scale without reverse-engineering both functions; the calibration is one decision smeared across two places. - Name the constants (`_SCORE_SPREAD`, `_SCORE_CENTER`, `_SCORE_CLIP`) with a note pointing to notebook 04; co-locate or cross-reference the CEFR thresholds so the calibration is one owned decision.
```

```text
_tests/test_understandability.py:4 - Tests mirror private implementation - Tests import `_punctuate_lines`, `_calculate_score`, `_extract_features` and assert exact internal outputs (that `_punctuate_lines` yields `"...Ende:. ..."`, that a clipped score `== -10`, that a DataFrame is `(1, 6)`). They lock in private behavior — including a quirk — and, because the public import is broken, none of them run. - False safety now (they don't execute) and, once the import is fixed, brittle resistance to legitimate refactoring of internals. - Test public behavior and invariants of get_zix/get_cefr (output range, monotonicity, CEFR mapping). Keep at most one or two focused tests on genuinely stable helpers. (Unblocked by the __init__ fix.)
```

```text
pyproject.toml:15 - Pull complexity down / dependency surface - `textdescriptives` is a *core* runtime dependency, but the package never imports it: the RIX formula is reimplemented inline (understandability.py:108-112) with only a source-link comment, and the only real importer is the notebook util utils_nlp.py. - Every `pip install zix` pulls a heavy, transitively-large dependency used by no package code — slower/fragile resolution and extra supply-chain surface for all users. - Move `textdescriptives` to the `[project.optional-dependencies].notebooks` group; keep the inline RIX in the package.
```

```text
zix/understandability.py:154-180 - Information hiding - _punctuate_lines silently rewrites the input before scoring: it force-appends "." to non-terminated lines (turning a heading "…am Ende:" into "…am Ende:.") and joins everything into one paragraph. The transformation is invisible to the caller and changes what is measured. - Minor scoring distortion the caller can neither see nor control; the current test enshrines the awkward `Ende:.` output. Low impact for a pragmatic index, but it is a hidden decision. - Acceptable as an internal normalization, but document the intent ("normalize messy bullet/line input into sentence-like units"), and avoid letting tests pin the cosmetic quirk.
```

---

## Open questions / assumptions

- **Is the os.system pip fallback ever expected to run?** Since `de-core-news-sm` is pinned in pyproject.toml, the fallback should be unreachable in a correct install. If it exists to support *non-uv* `pip install` of a source tree, a clear error message ("run `python -m spacy download de_core_news_sm`") is safer than shelling out.
- **Should empty/None inputs be domain-valid?** If upstream callers routinely pass empty strings (e.g. blank form fields), a defined sentinel may be justified — but then it should be one explicit, documented return type, not an undocumented `None` mixed with warnings.

## Residual risks / test gaps

- **Latent divide-by-zero / empty-stats:** `rix = long_words / n_sentences` (line 112) and `mean(sentence_lengths)` (line 107) assume at least one sentence. The only guard is `doc_len == 0` (non-punct, non-number tokens), which is a *different* condition than "has sentence boundaries." A doc with tokens but no `doc.sents` would raise `ZeroDivisionError`/`StatisticsError`. No test covers this.
- **No test exercises the real model end-to-end across difficulty levels** beyond one "score > 0" assertion; the monotonicity claim (simpler text scores higher) is only checked on hand-built feature vectors, not on text.

## Strong design decisions worth preserving

- `get_zix`/`get_cefr` are honestly *deep*: minimal interface over a real ML pipeline. Keep that two-function surface.
- `importlib.resources.files("zix")` for packaged data is the correct, install-location-independent choice.
- The private pipeline (`_punctuate_lines` -> `_extract_features` -> `_calculate_score`) is split by *concept*, not just execution order; each step owns a real responsibility. This is fine — don't add layers.

## Highest-leverage refactor sequence

1. **Export the public API** in `__init__.py` (+ `__all__`) and fix the test imports. *Unblocks the entire test suite — do this first.*
2. **Lazy scorer boundary:** move data/model/pipeline init behind `_get_scorer()`; **delete** the `os.system` pip fallback. *Removes import-time side effects, the shell-out, and the duplicated model version.*
3. **Unify the get_zix failure contract** to a single honest `float` return + `ValueError`; drop the None-threading so `get_cefr` becomes total over the real score range.
4. **Name the invariants:** `FEATURE_NAMES` tuple with the ordering comment; named calibration constants linked to the CEFR thresholds.
5. **Rebase tests** onto public behavior/invariants; **move `textdescriptives`** to the notebooks extra.

> Steps 1–2 remove the unknown-unknowns (broken tests, surprising import effects). Steps 3–4 remove the cognitive load and change-amplification. Step 5 hardens the result.

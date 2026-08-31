# Test convention examples

Concrete before/after snippets for each rule in SKILL.md.

## Test classes, no docstrings, public API only

```python
# yes.
class TestComputeDiscount:
    def test_applies_rate_to_price(self):
        result = compute_discount(price=100.0, rate=0.2)

        assert result == 80.0

    def test_zero_rate_returns_original_price(self):
        result = compute_discount(price=100.0, rate=0.0)

        assert result == 100.0


# no — top-level test function, a docstring restating the test name,
# and reaching into a private helper instead of the public function.
def test_compute_discount():
    """Test that compute_discount applies the rate to the price."""
    assert _apply_rate(100.0, 0.2) == 80.0
```

## Naming: one class per object, not one class per method

```python
# yes — every SQLWrapper behavior lives in one class; method names
# carry only scenario + outcome.
class TestSQLWrapper:
    def test_invalid_suffix_raises(self, tmp_path):
        ...

    def test_applies_schema(self, tmp_path, schema_sql):
        ...

    def test_backup_creates_missing_parent_directories(self, tmp_path):
        ...

    def test_execute_sql_ddl_returns_negative_one(self, tmp_path):
        ...


# no — five classes for one object, most with only 2-3 methods each,
# forcing a reader to jump around to see the full picture of
# SQLWrapper's behavior.
class TestSQLWrapperInit: ...
class TestSQLWrapperInitialize: ...
class TestSQLWrapperBackup: ...
class TestSQLWrapperExecuteSql: ...
class TestSQLWrapperExecuteScript: ...
```

A split is still correct when a cluster is a genuinely distinct
scenario, not a method fragment — keep `TestVersionBoundary` (a
specific edge-case flow) separate from `TestApplyVersionFile` (the
everyday path), and keep one class per CLI subcommand
(`TestMainPull`, `TestMainExport`) since each is its own unit.

## Testing objects: isinstance and key fields, not full equality

```python
# yes.
def test_full_parse(self, resource):
    vocabulary = load_labels(resource("labels.toml"))

    assert isinstance(vocabulary, LabelVocabulary)
    assert len(vocabulary.label_sets) == 1
    assert len(vocabulary.labels) == 2
    assert vocabulary.label_sets[0].name == "Gender Encoding"
    assert vocabulary.labels[0].label == "Male"


# no — reconstructs the whole nested object graph, which mostly
# re-asserts the loader's field-mapping rather than the behavior
# under test, and breaks on any unrelated field addition to the type.
def test_full_parse(self, resource):
    vocabulary = load_labels(resource("labels.toml"))

    assert vocabulary == LabelVocabulary(
        label_sets=[LabelSetDef(name="Gender Encoding")],
        labels=[
            LabelDef(label_set="Gender Encoding", value=1, label="Male"),
            LabelDef(label_set="Gender Encoding", value=2, label="Female"),
        ],
    )
```

## Resources: extract the happy path, and repeated error shapes

Say a project loads a `pricing.toml` file shaped like this in
production. A "full parse" test is the canonical, reusable case —
pull it out to `tests/resources/pricing.toml`:

```toml
# tests/resources/pricing.toml
[[tiers]]
name = "standard"
rate = 0.2

[[tiers]]
name = "premium"
rate = 0.35
```

```python
# yes — loads the checked-in sample, which also documents the shape
# of pricing.toml for anyone who opens tests/resources/.
class TestLoadPricing:
    def test_full_parse(self, resource):
        config = load_pricing(resource("pricing.toml"))

        assert isinstance(config, PricingConfig)
        assert len(config.tiers) == 2
        assert config.tiers[0].name == "standard"
```

An end-to-end test that also needs a valid `pricing.toml` should
reuse the same resource rather than writing its own copy:

```python
class TestEndToEndPricing:
    def test_apply_pricing_to_order(self, resource, repo):
        config = load_pricing(resource("pricing.toml"))

        apply_pricing(config, repo)
        ...
```

A single one-off error case stays inline — it exists to probe one
validation branch and will never be reused, so a resource file would
add a file without adding documentation value:

```python
# yes — one broken variant, used by one test, stays inline.
class TestLoadPricing:
    def test_unknown_tier_reference_raises(self, tmp_path):
        path = write_toml(
            tmp_path / "pricing.toml",
            """
            [[tiers]]
            name = "standard"
            rate = 2.0
            """,
        )

        with pytest.raises(PricingError, match="rate"):
            load_pricing(path)
```

But once a class accumulates 2+ error-path variants of the same
broken shape, extract each into a named resource and collapse the
tests into one parametrized test — the same "3+ variants" logic as
`pytest.mark.parametrize`, just with the inputs as files:

```
tests/resources/pricing/
    negative_rate.toml
    duplicate_tier_name.toml
    missing_required_field.toml
```

```python
# yes — three broken variants sharing one class, extracted and
# collapsed into one parametrized test.
class TestLoadPricing:
    @pytest.mark.parametrize(
        ["filename", "match"],
        [
            ("negative_rate.toml", "rate"),
            ("duplicate_tier_name.toml", "duplicate"),
            ("missing_required_field.toml", "name"),
        ],
        ids=["negative-rate", "duplicate-name", "missing-field"],
    )
    def test_invalid_raises(self, resource, filename, match):
        with pytest.raises(PricingError, match=match):
            load_pricing(resource(f"pricing/{filename}"))


# no — three near-identical inline TOML blocks as three separate
# tests; each is a small, unique variant of the exact same shape,
# which is exactly what the parametrize threshold exists to collapse.
```

## conftest.py: fixtures only, direct data-access over pipelines

```python
# tests/conftest.py
# yes.
import pytest


@pytest.fixture
def resources_dir():
    return Path(__file__).parent / "resources"


@pytest.fixture
def resource(resources_dir):
    def _resource(name):
        return resources_dir / name

    return _resource


# yes — sets up DB state through direct repo calls, not by routing
# through a higher-level import/ingest pipeline that happens to
# produce the same rows as a side effect.
@pytest.fixture
def make_target_survey(repo):
    def _make(*, question_text="A new question"):
        question_id = repo.questions.upsert_question(
            canonical_name="Real Question", dtype="text", is_core=True
        )
        survey_id = repo.surveys.upsert(
            qualtrics_survey_id="SV_1", name="v2", field_start="2024-01-05"
        )
        instance_id = repo.questions.upsert_instance(
            survey_id=survey_id,
            question_id=question_id,
            qid="QID_X_REAL",
            raw_id="Q_X",
            question_text=question_text,
        )
        return survey_id, instance_id

    return _make


# no — a plain helper function with no pytest.fixture decorator
# doesn't belong in conftest.py, even if several tests need it.
def _write_toml(path, content):
    path.write_text(content)
    return path
```

## tests/utils.py: shared helpers, never private, never domain seeding

```python
# tests/utils.py
# yes — public name, and a pure format-conversion helper with no
# domain-seeding logic of its own.
from pandas import DataFrame, MultiIndex


def build_export_dataframe(columns, rows) -> DataFrame:
    return DataFrame(rows, columns=MultiIndex.from_tuples(columns))
```

```python
# test_pricing.py
# yes.
from utils import build_export_dataframe

# no — leading underscore on something imported across module
# boundaries, and importing a helper out of conftest.py instead of
# tests/utils.py.
from conftest import _write_toml

# no — a domain-seeding helper (upserts a whole survey + questions)
# living as a plain function in utils.py instead of a conftest.py
# fixture; it loses dependency injection and per-test override, and
# every call site has to thread `repo` through by hand.
def seed_target_survey(repo, *, question_text="A new question"):
    ...
```

## Whitespace: setup, blank, invocation, blank, assertions

```python
# yes.
def test_foo(self, tmp_path):
    wrapper = SQLWrapper(tmp_path / "dcs.db")
    wrapper.execute_script("CREATE TABLE t (id INTEGER)")

    result = wrapper.execute_sql("INSERT INTO t (id) VALUES (1)")

    assert result == 1

    columns, rows = wrapper.execute_sql("SELECT id FROM t")
    assert [tuple(row) for row in rows] == [(1,)]
```

The second blank line separates a post-invocation fetch (getting more
data needed for one specific assertion) from the assertion(s) above
it — it's setup for that check, not part of the original invocation.

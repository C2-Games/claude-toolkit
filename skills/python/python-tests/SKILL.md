---
name: python-tests
description: Enforces this user's pytest conventions — test classes over flat test functions grouped at object/module granularity (not one class per method), terse names, no test docstrings, never testing private members directly, isinstance-plus-partial-field assertions over full dataclass equality, pushing sample data (including repeated error-shape variants) out of inline test code into tests/resources/, oversized fixtures becoming text resources, conftest.py reserved for fixtures only, direct-data-access-layer fixtures over pipeline-routed setup, shared helper functions (never leading-underscore) living in tests/utils.py, test files mirroring the src package tree under tests/unit/, class-carries-unit/method-carries-scenario naming, shared Fake* collaborator classes in tests/utils.py, a consistent setup/invocation/assertion whitespace grouping, and a 3+-variants threshold for parametrize. Use this whenever writing, editing, reviewing, or refactoring any pytest test file (test_*.py, conftest.py, tests/utils.py), including new tests, fixtures, or fixes to existing tests — even a single test case. Also use it when the user asks to "clean up," "dedupe," or "refactor" tests, or asks about test structure, fixtures, or sample/fixture files. This is the test-specific companion to the python-style-guide skill — general Python style rules (typing, docstrings, formatting, naming, etc.) live there; this skill only covers test-writing conventions.
---

# Python test conventions

Apply every rule below to any pytest test code you write or edit for
this user. General Python style (docstrings, typing, formatting,
naming, comments) is covered by the `python-style-guide` skill — this
skill is scoped to test-specific conventions only.

For a worked before/after of the resource-extraction pattern, read
`references/examples.md`.

## Structure

Write tests with `pytest`, not `unittest`. Within a test module, group
the tests for a given unit (function, method, or class) into a test
class rather than a flat list of top-level `test_*` functions —
`class TestComputeDiscount:` with `test_`-prefixed methods inside it,
one class per unit under test. Use plain `assert` statements (pytest
rewrites them for readable failure output) rather than
`self.assertEqual`-style methods, and use fixtures/
`pytest.mark.parametrize` rather than hand-rolled setup or loops over
cases.

Don't add docstrings to test classes or test methods — the test name
should say what's being verified, and a docstring restating
`test_returns_none_for_missing_user` in prose is redundant. This is
one of the few places the style guide's docstring rules don't apply.

Never test private methods, functions, or classes (leading
underscore) directly — test only through the public API. A private
member's contract is free to change as an implementation detail; a
test that calls it directly breaks on refactors that don't change any
observable behavior, and locks in internals that were never meant to
be a contract. If a private code path matters enough to need direct
coverage, that's a sign it should either be reachable through the
public surface you're already testing, or promoted to public.

## Sample data: resources over inline literals

When a test needs sample content for a real artifact the project
reads or writes — a config file, a schema, a JSON payload, a CSV
export, a version/manifest file — prefer a static file under
`tests/resources/` over building the same content inline (e.g. via a
`tmp_path`-writing helper) in every test that needs it. A checked-in
sample file does double duty: it's fixture data, and it's
documentation of what that file format actually looks like.

Two conditions both need to hold before something earns a resource
file:

- **In scope**: it represents a real artifact the application
  consumes or produces — not a synthetic shape invented purely to
  drive one validation branch. If the format doesn't exist as a
  concept outside the test suite, it doesn't belong in
  `tests/resources/`.
- **Reusable / canonical**: it's the "successful", full-shape example
  of that artifact — the one that documents the complete structure —
  and/or it's used by more than one test (e.g. a "full parse" unit
  test and an end-to-end test that composes several such files
  together). A one-off variant used by exactly one test doesn't
  justify a checked-in file.

Concretely: a happy-path "parses the full file" test is almost always
a good candidate.

Error-path tests (malformed syntax, a missing required field, a
duplicate key, an out-of-range enum) are usually one-off and stay
inline — a single deliberately-broken variant that exists to probe
one validation branch doesn't earn a checked-in file by itself. But
when a *class* accumulates 2+ error-path variants of the same broken
shape (e.g. `TestLoadVocabulary` testing a duplicate canonical name,
an invalid dtype, and a missing required field — three separate
broken TOML files of the same general shape), extract each into a
named resource under a subdirectory scoped to that area
(`tests/resources/versions/questions/duplicate_canonical_name.toml`,
`.../invalid_dtype.toml`, ...) and collapse the tests into one
`@pytest.mark.parametrize` over `(filename, expected_exception_match)`
per the three-variant threshold below — this is the same
"3+ variants become one parametrized test" rule, just with the inputs
living as files instead of inline strings. The trigger is reuse
count, not "is this an error case": one broken variant used by one
test stays as a small inline literal (via the `tests/utils.py` helper
below); a cluster of them sharing a class gets extracted and
parametrized together.

## conftest.py holds fixtures only

A `conftest.py` holds `@pytest.fixture`-decorated fixtures shared
across two or more test modules — nothing else. Don't put test logic,
helper functions, or one-off fixtures used by a single module in
`conftest.py`.

Common fixtures worth centralizing there once more than one test
module needs them:

- A path/loader fixture over `tests/resources/` (e.g. `resource`,
  returning a `Path` for the caller to load, or parsed content for
  well-known formats like JSON) so tests reference sample files by
  name instead of re-deriving `Path(__file__).parent / "resources"`
  in each module.
- Shared setup fixtures (an in-memory DB connection, a repository
  bound to it, an API client) that multiple test modules currently
  duplicate.

If a fixture is only used by one test module, leave it in that
module — promote it to `conftest.py` the moment a second module needs
the same thing, not preemptively.

Watch fixture size, too. A fixture that's grown past roughly 150
lines, or that's duplicating another fixture's heavy setup under a
different name, is a sign the setup belongs in a resource file
instead of being rebuilt from Python on every call — same reasoning
as the sample-data rule above, just applied to fixtures. Keep the
resource text-based (TOML/CSV/SQL — whatever the fixture is
constructing), never a binary artifact like a `.db` file: a binary
resource can't be diffed or read as documentation, which defeats the
point. When two fixtures in different modules are converging on the
same 150+-line shape, that's also usually the moment to promote one
shared version to `conftest.py` rather than trimming both
independently.

## Fixture architecture: build through the lowest layer that fits

Default to setting up test state through the most direct layer
available — direct calls against the data-access layer under test
(e.g. `repo.things.upsert(...)`) — rather than routing setup through
a higher-level pipeline (an ingest routine, a CLI command, a full
import flow) that happens to produce the same rows as a side effect.
The pipeline-routed version is slower, harder to read (the fixture's
intent is buried in pipeline mechanics), and breaks for reasons
unrelated to the test using it. Reserve pipeline-routed fixtures for
tests that are actually verifying that pipeline's behavior — those
still need the real thing.

When different call sites need the same shape with a couple of
different parameters (a different label, a different date), reach for
a factory fixture — a fixture that returns a callable — instead of
either duplicating the fixture per-variant or forcing every caller
into one fixed shape:

```python
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
```

## Plain helper functions go in tests/utils.py

Not every shared piece of test code is a fixture — a plain function
like "write this string to a file and return the path" doesn't need
pytest's dependency injection, it just needs to be callable. Put
these in a `tests/utils.py` module and `import` them explicitly into
whichever test files need them (`from utils import write_toml`), not
in `conftest.py`.

Never name one of these a leading-underscore ("private") function.
Once a function is imported into another module, it's part of that
module's public surface by definition — a leading underscore signals
"internal to this file, don't reach in from outside," which is
already false the moment a second file imports it. Name it plainly
(`write_toml`, not `_write_toml`) and let the module boundary
(`tests/utils.py` vs. each test file) be the thing that communicates
"this is shared test infrastructure, not a test case."

The same no-underscore rule applies to helpers used by only one test
module: they live module-level in that test file, plainly named
(`build_config`, `build_apply_versions`), and move to `tests/utils.py`
only when a second module needs them.

Keep `tests/utils.py` to genuinely cross-file shared surface: a
shared `Fake*` collaborator (below) and pure format-conversion
helpers with no domain-seeding logic of their own (a CSV loader, a
DataFrame builder). Don't put module-level constants or type aliases
in test code anywhere (no `METADATA_CANONICAL_NAMES`-style tuples, no
bare `type QuestionDtype = Literal[...]`) — inline the literal at its
one use site, or promote it to a fixture the moment 2+ files need the
identical value. And don't let domain-seeding helpers (a function
that upserts a whole survey + questions + instances to set up DB
state) accumulate here either — per the fixture-architecture section
above, those belong in `conftest.py` as fixtures (plain or factory)
once shared, not as plain functions in `utils.py`: a fixture gets
dependency injection and per-test override for free, a plain function
just gets called with the same repo threaded through by hand at every
site.

## Mirror the src package tree

Test files live under `tests/unit/`, mirroring the source package
layout: `src/pkg/services/ingest.py` → `tests/unit/services/
test_ingest.py`, root-level modules at `tests/unit/test_<name>.py`.
Sample data stays at `tests/resources/`. Underscore-prefixed src
modules map to un-prefixed test names (`_client.py` →
`test_client.py`). No `__init__.py` files anywhere in `tests/`.

Two gotchas this layout creates:

- **Duplicate basenames**: two src modules with the same name in
  different subpackages (`services/export.py` and
  `resources/survey/export.py`) would both want `test_export.py`,
  which pytest's default import mode rejects ("import file mismatch")
  without `__init__.py` packages. Give those test files unique names
  instead (`test_export_service.py`, `test_export_resource.py`).
- **`from utils import ...` breaks from nested dirs**: pytest inserts
  each test file's own directory on `sys.path`, not the tests root,
  so nested files can't see `tests/utils.py`. Add the tests root to
  `[tool.pytest.ini_options] pythonpath` (e.g.
  `pythonpath = ["src", "tests"]`) to make it deterministic.

## Naming: class carries the unit, method carries the scenario

Default to one class per object or module under test — `TestConfig`
for everything exercising `Config`, `TestSQLWrapper` for everything
exercising `SQLWrapper` — not one class per method
(`TestSQLWrapperInit`, `TestSQLWrapperBackup`,
`TestSQLWrapperExecuteSql`, ...). Splitting by method looks organized
but it's really just fragmentation: a reader has to jump between
several same-sized classes to see the full picture of one object, and
most of those classes end up with only 2-3 methods each.

Split into a separate class only when a cluster is a genuinely
distinct *behavior scenario* — usually a specific edge case or
end-to-end path — large or hairy enough that folding it into the main
class would bloat it past being skimmable. `TestApplyVersionFile`
covering the everyday apply/reapply/idempotency cases, with
`TestVersionBoundary` split out for the boundary-reassignment edge
cases it triggers, is a legitimate split — that's a distinct scenario
cluster, not a method fragment. Likewise, when one module exposes
several genuinely different top-level behaviors (a CLI's
`pull`/`export`/`surveys` subcommands), one class per behavior
(`TestMainPull`, `TestMainExport`, `TestMainSurveys`) is correct —
each subcommand is its own unit, not a method slice of one shared
object.

Method names carry only scenario + outcome, never repeating the
class's context: `TestSQLWrapper::test_backup_creates_missing_
parent_directories`, not `test_sql_wrapper_backup_creates_missing_
parent_directories`. Keep the outcome word (`_raises`,
`_quarantines`, `_returns_none`) — it states the assertion; drop
everything the class name already says.

Beyond that, keep names terse. Cut words that don't change what's
being verified — hedge words, restated obviousness, anything a reader
could infer from the class name or the code under test:
`test_bare_invocation_requires_subcommand` → `test_requires_
subcommand`; `test_client_construction_error_prints_clean_error` →
`test_prints_clean_err`; `TestApplyVersionFileBoundaryReassignment` →
`TestVersionBoundary`; `TestEndToEndLabelsQuestionsAndVersionFile` →
`TestEndToEnd`. The test is A test in its class already — don't
re-describe the class in the method name, and don't pad the class
name past what's needed to disambiguate it from its siblings in the
file. Failure output should still read as a clear sentence; terse
isn't the same as cryptic.

## Shared fakes: one named Fake* class in tests/utils.py

When two or more test modules hand-roll the same fake collaborator,
replace the copies with one named `Fake*` class in `tests/utils.py`
(e.g. `FakeClient`). Its constructor takes only the surface the code
under test actually touches, with keyword defaults for the rest:

```python
class FakeClient:
    def __init__(self, repo, *, config=None, qualtrics=None): ...
```

Construct it inline in tests (`FakeClient(repo)`) rather than wrapping
it in a fixture — explicit construction shows each test's setup at
the call site, and a test needing a variant passes it as a kwarg
instead of mutating a fixture-provided instance after the fact. The
constructor signature doubles as documentation of exactly which
collaborator surface the code under test depends on. Beware defaults
with side effects: a default that constructs a real object (e.g. a
`Config()` that silently reads a `config.toml` from cwd) belongs
behind an inert stand-in (`SimpleNamespace(export=ExportConfig())`).

## Testing objects: isinstance and key fields, not full equality

When a test produces a dataclass or other structured object, prefer
checking its type and a handful of the fields the test actually cares
about over asserting full equality against a freshly-constructed
expected object:

```python
# yes.
def test_full_parse(self, resource):
    vocabulary = load_labels(resource("labels.toml"))

    assert isinstance(vocabulary, LabelVocabulary)
    assert len(vocabulary.label_sets) == 1
    assert len(vocabulary.labels) == 2
    assert vocabulary.label_sets[0].name == "Gender Encoding"
    assert vocabulary.labels[0].label == "Male"


# no — reconstructs the entire nested object graph in the test,
# which mostly just re-asserts the loader's field-mapping rather than
# the behavior under test, and breaks on any unrelated field addition.
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

Full equality has a real cost beyond verbosity: it couples the test
to every field on the dataclass, so an unrelated field added later
means updating every full-equality test that touches that type,
whether or not the new field is relevant to what that test verifies.
`isinstance` plus targeted field/length checks verifies the same
behavior — the loader produced the right shape with the right values
— without that coupling. Reach for full equality only when there's
genuinely no reasonable partial check (e.g. the object is a single
scalar-like value being compared against another instance of the
same type with no natural "important fields" subset).

## Parametrize threshold: three data-only variants

When 3+ test methods differ only in input data and expected output,
collapse them into one `@pytest.mark.parametrize` with explicit
`ids=` (kebab-case, e.g. `ids=["core-only", "noncore-only", "all"]`).
Below three variants — or whenever the variants differ in setup,
mocking, or which assertions run — keep separate methods; a
parametrized test whose body branches on its parameters is worse than
the copies it replaced. Never parametrize across different units
under test (e.g. the "same" malformed-input case for three different
loader functions stays as one small test per loader's class). This is
the same threshold that drives resource-file extraction for repeated
error-shape variants — see "Sample data" above.

## Whitespace: group setup, invocation, assertions

Within a test body, group by role and separate the groups with a
single blank line: setup lines first, then one blank line, then the
line that invokes the code under test (usually assigned to a result
variable), then one blank line, then the assertions:

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

Note the second blank line before the last two lines: when an
assertion needs more data fetched *after* the main invocation (here,
reading back the row to check it landed), that fetch stays grouped
with the assertion it supports, separated from the earlier
assertion(s) by its own blank line — it's setup for one specific
check, not part of the original invocation. Don't add blank lines
inside a single logical group (e.g. between consecutive setup calls,
or between two assertions that check the same result) — the blank
line marks a role change, not just any line break.

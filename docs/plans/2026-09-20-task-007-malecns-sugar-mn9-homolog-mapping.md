# Task 007 - MaleCNS v1.0 Sugar/MN9 Homolog Mapping

Status: complete for the identity/homology scope; implementation and
validation are committed for review and reuse.

## Scope and gate

Task 006 is required to be the committed `HEAD` on `master` with a clean
working tree before this task starts. This task is an identity/homology task
only. It must not stimulate the MaleCNS graph, run a LIF sweep, tune model
parameters, or make a conserved-behavior claim.

The identity boundary is:

```text
Shiu/FlyWire v630 root
  -> versioned FlyWire annotation/type evidence
  -> optional public segmentation lineage evidence
  -> cross-brain/type and MaleCNS annotation evidence
  -> MaleCNS body candidate(s)
  -> explicit mapping status and provenance
```

An old FlyWire root is never treated as a MaleCNS body ID.

## Planned evidence sources

- Task 006's pinned Shiu companion repository commit and notebook location.
- `flyconnectome/flywire_annotations` tag `v1.0.0`, the release principally
  based on FlyWire segmentation/materialization 630, for the version-matched
  annotation rows.
- A later tagged annotation release only where its release, commit, and root
  overlap or absence are recorded explicitly; it cannot silently replace the
  v630 evidence.
- The locally validated MaleCNS v1.0 annotation Feather and neurotransmitter
  Feather, using `flywireType` as the cross-brain type field and preserving
  all requested identity metadata.
- Public FlyWire/CAVE lineage tooling only if it is available without private
  credentials. Failure to obtain such evidence is recorded, not hidden.
- The local curated MaleCNS structural graph for path availability only.

## Representation

Add an immutable, deterministic mapping model with:

- exact string-preserved reference IDs;
- `EXACT`, `TYPE_LEVEL`, `AMBIGUOUS`, and `UNRESOLVED` statuses;
- ordered, de-duplicated MaleCNS candidate records;
- explicit evidence-source and evidence-note fields;
- separate sugar-population and MN9-readout definitions;
- stable reference, mapping, population, and structural-result fingerprints.

The model will reject duplicate candidate IDs, preserve side values without
guessing, retain missing/ambiguous lineage, and keep identity evidence
independent of graph connectivity or later simulation outcomes.

## Execution phases

1. Freeze the 21 sugar and MN9 v630 IDs and fingerprint them.
2. Materialize compact, tracked v630 annotation evidence for all 22 IDs.
3. Record later-release overlap and any public lineage/update result, with
   one-to-many changes left ambiguous.
4. Resolve the FlyWire sugar type(s) and MN9 motor type from actual rows.
5. Derive MaleCNS candidates through `flywireType`, then validate sugar
   biology through superclass/class, receptor, nerve, side, and NT metadata.
6. Define per-reference mappings, the later sugar input population, and the
   MN9 readout without running dynamics.
7. Run structural direct-edge/first-hop/reachability checks without using
   their results to select identities.
8. Run the real mapping pipeline twice and require identical serialized
   output and fingerprints.

## Validation

Required commands:

```text
uv run python -m pytest -v
uv run python -m compileall src
git diff --check
git status --short
git diff --stat
```

Offline tests must cover exact-ID preservation, all mapping statuses,
one-to-one and one-to-many mappings, ambiguity/unresolved cases, side and
provenance preservation, deduplication, deterministic ordering/fingerprints,
sugar-population derivation, MN9 readout definition, structural path helpers,
and independence from expected simulation results.

## Nonclaims

FlyWire v630 is a female brain dataset and MaleCNS v1.0 is a male complete-CNS
dataset. Homologous type does not imply identical connectivity or firing.
Root continuity is not cross-sex biological identity; morphology alone is not
identity. Type-level mappings can represent multiple bodies. Dimorphic or
sex-specific neurons require special handling. Unresolved cases remain
unresolved.

## Execution record

Status: COMPLETE for the Task 007 identity/homology scope. The closure commit
contains these changes; no push, tag, or Task 008 experiment was performed.

### 1. Task 006 reference identities

The initial gate was verified before work began: branch `master`, clean tree,
and Task 006 at `d9b55c378ebdfb651020232fa6d970721168bed7` (`test: reproduce
Shiu sugar-to-MN9 experiment`). The baseline command
`uv run python -m pytest -q` reported `82 passed in 2.11s`.

The pinned source is `philshiu/Drosophila_brain_model@91bdd1e7dcf193f3e7ca5a8933497fcef63b7960`,
with `neu_sugar` in `example.ipynb` and MN9 root `720575940660219265`.
The exact 21 sugar roots and MN9 root are string-preserved in
`data/provenance/task007-flywire-evidence.json`. The population fingerprint
is `8db73a8d0aae2e7a4ab3075b3592d2ccfa83c8eb565ca8e57905e90c8c2eb184`.

### 2. FlyWire annotation/version sources

The version-matched source is `flyconnectome/flywire_annotations` tag
`v1.0.0`, commit `847a711ce3b6e3cc675cf9ef9c843ba564bba1b5`, based on
materialization 630. All 22 roots occur there. Sugar rows are
`flow=afferent`, `super_class=sensory`, `cell_class=gustatory`,
`nerve=MxLbN`; MN9 is `flow=efferent`, `super_class=motor`,
`cell_class=motor`, `nerve=PhN`.

Later typed overlap uses tag `v3.0.0`, commit
`a92610ef4cb86653aaf2b337eaf466b22f3ebd23`, based on the 783-era release.
It reports 20 sugar roots as `LB3` / `sugar/water` and MN9 as `CB0701` /
`ingestion_motor_neuron`. Root `720575940620900446` is absent from that
later table. This later source is explicit overlap/absence evidence, not a
silent replacement for v630.

### 3. Root-lineage method

No updated FlyWire root was admitted. A public CAVE/fafbseg lineage query was
not run because no authenticated private API or token was admitted and the
task must not depend on credentials. The later table therefore provides
same-root overlap for 20 roots and an absence observation for one, not a
claim that any old root is current or that the absent root has one successor.
One-to-many split ambiguity remains uncollapsed.

### 4. FlyWire cell types

The v630-era rows have no formal `cell_type` for the 21 sugar roots or MN9.
Later evidence resolves 20 sugar roots to repeated `LB3` / `sugar/water`
and MN9 to `CB0701`. The absent root remains without defensible typed
evidence. The 21 inputs were not treated as identical merely because the
experiment stimulated them as one functional group.

### 5. MaleCNS cross-brain mapping fields

The validated local sources are the v1.0 body-annotation and
body-neurotransmitter Feather files under `data/raw/male-cns/v1.0`.
`flywireType` yields 87 MaleCNS bodies for `LB3` and two for `CB0701`.
Candidate records preserve `bodyId`, `type`, `flywireType`, `superclass`,
`subclass`, `class`, `supertype`, `receptorType`, `entryNerve`, `somaSide`,
`somaNeuromere`, `dimorphism`, `matchingNotes`, `mancType`, `mancBodyid`,
`exitNerve`, `rootSide`, status, and Task 004 NT/sign resolution. Candidate
body IDs are never treated as old FlyWire roots.

### 6. Per-neuron mapping table

The 20 roots listed in `type_level_sugar_root_ids` below share the 87-body
`LB3` candidate set; the absent root has no candidate set; MN9 shares the
two-body `CB0701` set. This is the complete per-neuron result, with the
candidate sets retained in `data/provenance/task007-mapping-summary.json`.

| reference root | role | later FlyWire evidence | candidate set | status |
| --- | --- | --- | --- | --- |
| 720575940624963786, 720575940630233916, 720575940637568838, 720575940638202345 | sugar | LB3 / sugar-water | LB3 (87) | TYPE_LEVEL |
| 720575940617000768, 720575940630797113, 720575940632889389, 720575940621754367 | sugar | LB3 / sugar-water | LB3 (87) | TYPE_LEVEL |
| 720575940621502051, 720575940640649691, 720575940639332736, 720575940616885538 | sugar | LB3 / sugar-water | LB3 (87) | TYPE_LEVEL |
| 720575940639198653, 720575940617937543, 720575940632425919, 720575940633143833 | sugar | LB3 / sugar-water | LB3 (87) | TYPE_LEVEL |
| 720575940612670570, 720575940628853239, 720575940629176663, 720575940611875570 | sugar | LB3 / sugar-water | LB3 (87) | TYPE_LEVEL |
| 720575940620900446 | sugar | absent in v3.0.0 | none | UNRESOLVED |
| 720575940660219265 | MN9 | CB0701 / ingestion motor | CB0701 (2) | TYPE_LEVEL |

There are no `EXACT` or `AMBIGUOUS` real records. Counts are
`EXACT=0`, `TYPE_LEVEL=21`, `AMBIGUOUS=0`, `UNRESOLVED=1`.

### 7. Sugar-specific biological evidence

The 87 `LB3` candidates reduce to 85 biologically consistent candidates with
`superclass=cb_sensory`, `class=gustatory`, and `entryNerve=MxLbN`. The final
right-side population uses explicit MaleCNS `rootSide=R` because `somaSide`
is null for these candidates: 43 bodies remain. Their types are
`LB3a=8`, `LB3b=6`, `LB3c=10`, `LB3d=15`, `LB4b=3`, and one missing type;
all use `MxLbN`. All 43 `receptorType` values are missing, so no receptor
identity is invented.

Forty-two candidates have Task 004 consensus-first NT resolution to
acetylcholine and derived Shiu-compatible sign `+1`; one has unresolved NT.
This is direct MaleCNS metadata plus the explicit Task 004 policy. `LB3` is
cross-brain type evidence; the population is not an exact per-root identity.

### 8. MN9 evidence

FlyWire `CB0701` and MaleCNS `flywireType=CB0701` / `type=MN9` provide the
cross-brain correspondence. MaleCNS bodies are `10331` (`somaSide=L`) and
`16949` (`somaSide=R`), both `superclass=cb_motor`, `subclass=pm`, and
`exitNerve=PhN`. `mancType`, `mancBodyid`, and `somaNeuromere` are absent.
No NeuronBridge result was substituted. Type plus side does not justify an
exact cross-sex selection, so the readout retains both bodies.

### 9. Final population/readout definitions

The tracked population contains 43 MaleCNS body IDs, uses `rootSide=R`, and
has 42 resolved plus one unresolved Task 004 NT record. The MN9 readout is
`TYPE_LEVEL` with candidate IDs `{10331, 16949}` and no selected body. Task
008 must not silently choose one.

### 10. Structural connectivity sanity check

On the MaleCNS curated graph, defined here as both endpoints having non-null
`superclass`, and without dynamics:

| measure | result |
| --- | ---: |
| direct sugar -> MN9 edges | 0 |
| first-hop curated targets | 459 |
| shortest path to 10331 | 2 |
| shortest path to 16949 | 2 |
| reachable MN9 candidates | 2 |
| total structural path availability | 2 |

First-hop target fingerprint:
`c485c6b9ec4f5e270a83a88812566b2eb976cd3c6e0514a4418f1184b6c3117f`.
These observations did not select any candidate.

### 11. Fingerprints and repeatability

Mapping fingerprint:
`832d8428c458e59cfff7b52fc257a4ba3fd85fdd6f3ebf47f01e02e218f50269`.
Sugar population fingerprint:
`2d8c0738a9f95d1e33d9dadae434fa8ed1be12b19778f91948da0fcf63054c0b`.
The real pipeline was run twice; both serialized results had digest
`da9abdd7c1fd59ba316a19f228f10508652a87e4112772a3c9e8ce7f496864f1` and
reported `identical=True`.

### 12. Limitations and scientific nonclaims

FlyWire v630 is female; MaleCNS v1.0 is male complete-CNS. Homologous type
does not imply identical connectivity or firing. Root continuity is not
cross-sex biological identity. Morphology similarity alone does not prove
identity, and no morphology probability was invented. Type-level mappings
can represent multiple bodies. Sex-specific/dimorphic neurons require
special handling. The v630 table reports the sugar rows as `left`, while the
Shiu experiment labels the stimulated set right-side; this discrepancy is
preserved rather than normalized. The missing sugar root and two-body MN9
set remain unresolved individually. No stimulation, LIF sweep, tuning,
female/male rate comparison, FlyGym, body simulation, or causal claim was
made.

### 13. Validation, files, and next task

`uv run python -m pytest -q` passed with 96 tests; `uv run python -m
compileall src` passed; `git diff --check` passed with only a line-ending
warning. Changed files are:

```text
data/provenance/task007-flywire-evidence.json
data/provenance/task007-mapping-summary.json
docs/plans/2026-09-20-task-007-malecns-sugar-mn9-homolog-mapping.md
src/malecns_sim/analysis/__init__.py
src/malecns_sim/analysis/task007.py
src/malecns_sim/homology.py
tests/test_task007.py
```

Because one sugar root is unresolved and MN9 is type-level with two bodies,
the recommended next task is the narrower `Task 007a - public FlyWire
root-lineage and NeuronBridge/MN9 resolution`. Task 008 should wait until it
explicitly accepts this uncertainty or that task resolves it.

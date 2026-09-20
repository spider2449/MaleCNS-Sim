# Task 007b - MN9 Laterality Resolution

Status: COMPLETE for the narrow laterality scope.  The result is
`SIDE_RESOLVED`, not `EXACT`.  No sugar population change, historical sugar
root resolution, LIF engine run, dynamics result, or connectivity outcome was
used.

## Starting state

Task 007a ended with MN9 `AMBIGUOUS` and candidates:

- MaleCNS body `10331` = `MN9_L`, `somaSide=L`.
- MaleCNS body `16949` = `MN9_R`, `somaSide=R`.

The verified Task 007a commit is
`3683dc963274efa1c910e224aca4d473f847bb97` (`research: resolve public
MaleCNS identity evidence`).  The existing 43-neuron sugar population was
not modified; its fingerprint remains
`2d8c0738a9f95d1e33d9dadae434fa8ed1be12b19778f91948da0fcf63054c0b`.

## VFB CB0701 evidence

The current VFB entry was inspected directly on 2026-09-20:

`https://www.virtualflybrain.org/term/cb0701-vfb_fw000395/`

It identifies `CB0701`, VFB identifier `VFB_fw000395`, and cross-references
FlyWire root `720575940660219265`.  Its direct relationship metadata records
the classification `proboscis muscle 9 motor neuron` and soma location `right
side of organism`.  It also records the motor/efferent classification,
acetylcholine capability, and adult brain/female organism membership.

This is direct VFB page evidence, not a search-result summary.

## Shiu primary-paper laterality evidence

Primary source: Shiu et al., *Nature* 634 (8032): 210-219 (2024), DOI
`10.1038/s41586-024-07763-9`, PMCID `PMC11446845`:

`https://pmc.ncbi.nlm.nih.gov/articles/PMC11446845/`

The exact source location is Methods, “Computational modelling of water and
sugar GRN activity”, especially the paragraphs rendered at lines 516-525.
The methods state that the principal simulations use unilateral left-hemisphere
sugar GRNs, except for Extended Data Fig. 1d, and that ordinary MN9 wording
means the MN9 contralateral to the activated GRNs.  Therefore the ordinary
principal readout is the right MN9.

The paper also explicitly documents that FAFB was left-right inverted and that
the paper uses true biological side.  The pinned reference notebook at
`philshiu/Drosophila_brain_model@91bdd1e7dcf193f3e7ca5a8933497fcef63b7960`
labels the principal sugar list as right hemisphere and the reference root as
left; those are frame labels and are not allowed to override the paper’s true
biological-side statement.

## MaleCNS side identity

The validated MaleCNS v1.0 annotation row source is:

`https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-annotations-male-cns-v1.0-minconf-0.5.feather`

The relevant source fields are:

| body | type | instance | somaSide | rootSide | flywireType | superclass | subclass | exitNerve |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10331 | MN9 | MN9_L | L | null | CB0701 | cb_motor | pm | PhN |
| 16949 | MN9 | MN9_R | R | null | CB0701 | cb_motor | pm | PhN |

The rows were read from the validated local Feather data; no free-text
inference was used.  Official explorer metadata is also consistent: the
corresponding VFB entries are `VFB_jrmc20e1` (left) and `VFB_jrmc20e2`
(right), each classified as a proboscis muscle 9 motor neuron with the
matching MaleCNS type metadata.

## Coordinate and contradiction checks

- No primary VFB evidence was found that makes root `720575940660219265`
  left-sided; its direct entry says right.
- CB0701 is bilateral.  A distinct VFB CB0701 entry is left-sided, but it has
  a different FlyWire root, so that is expected bilateral evidence rather than
  an inconsistency for the queried root.
- No evidence was found that the MaleCNS `MN9_L`/`MN9_R` labels use a
  transformed rather than organism-anatomical side.  The direct `somaSide`
  and VFB side relationships agree.
- The Shiu notebook/paper coordinate difference is real and explicitly
  documented by the paper as the FAFB left-right inversion.  It is resolved by
  using true organism anatomical side, not by treating the notebook comments
  as a second physical-side authority.

## Resolution rule and result

Promotion required all three independent facts:

1. VFB root `720575940660219265` / CB0701 is right-sided.
2. The ordinary Shiu readout is contralateral to left sugar GRNs, hence the
   right MN9.
3. MaleCNS has exactly one direct MN9/CB0701 candidate with explicit right
   side: body `16949`.

All three pass.  The final mapping category is `SIDE_RESOLVED`; the explicit
later readout is MaleCNS body ID `16949` (`MN9_R`).  `EXACT` was not used,
because these sources establish side correspondence but not segmentation
identity or an individual cross-brain proof.

Permitted identity claim:

> side-resolved cross-brain homolog corresponding to the right MN9 / CB0701 reference

This does not claim segmentation identity across FlyWire and MaleCNS, the same
physical animal neuron, identical connectivity, or identical physiology.

## Evidence provenance and fingerprint

Compact evidence is stored in
`data/provenance/task007b-mn9-laterality-evidence.json`.  Its deterministic
normalized evidence fingerprint is:

`b6e0ec543f7f19f5e452baca8f55ea065c762871b18445ad024db362bb8cfbbd`

The resolved readout provenance chain is:

`FlyWire 720575940660219265 -> CB0701 / MN9 -> right-side correspondence -> MaleCNS MN9_R 16949`.

## Implementation and tests

The implementation adds explicit anatomical-side normalization and a narrow
laterality resolver.  It rejects contradiction, does not accept simulation
results as an input, preserves coordinate-system notes, and carries source
provenance into the resolved readout.  `SIDE_RESOLVED` is distinct from
`EXACT` and `TYPE_LEVEL`.

Focused tests cover evidence representation, side normalization, contradictory
evidence, unique and duplicate same-side candidates, type-only rejection,
simulation exclusion, coordinate-note preservation, deterministic
fingerprinting, resolved-readout provenance, and the production Task 007
readout path.

## Limitations and handoff

The result is a laterality/type correspondence only.  It does not establish
individual segmentation lineage, cross-brain morphology identity, connectivity
identity, or physiological identity.  The Shiu paper’s exceptional right-GRN
simulation is not the ordinary principal sugar readout and was not used for
this promotion.  The historical missing sugar root remains unresolved and the
43-neuron sugar population remains unchanged.

Task 008 may proceed with the explicitly documented `SIDE_RESOLVED` readout
body `16949`, provided it preserves the claim boundary above and does not
silently relabel the result as `EXACT`.

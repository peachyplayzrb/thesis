# Provenance Rules

## Purpose
Define minimum evidence and compliance checks before an external dataset can be treated as thesis-active data.

## Required Evidence For Any External Dataset
1. Source identity: provider name, publication reference, and canonical source URL.
2. Acquisition evidence: access request/approval date and acquisition channel.
3. Version identity: exact release/version plus any archive hash/checksum if available.
4. License/terms: explicit usage permission scope, redistribution constraints, and citation obligations.
5. Local integrity: local file inventory with timestamps and verification notes.

## License And Usage Confirmation Checklist
Before first analysis run on newly received external data, log all items below:
- Permitted use includes non-commercial academic thesis work.
- Permission scope covers local processing and model/feature derivation required by pipeline stages.
- Redistribution policy is explicit (raw data, transformed data, and metadata exports handled separately).
- Citation/acknowledgement wording is explicit or default citation standard is documented.
- Any retention/deletion obligations after thesis completion are documented.

If any item is unknown, the dataset remains `fallback` or `pending` in `dataset_registry.md` and cannot become active corpus-of-record.

## Music4All Specific Control (2026-03-22)
- Current state: positive provider reply received; provider requires completed signed disclosure/confidentiality agreement before sharing download URL/password.
- Required close-out steps:
	1. Archive provider reply summary in admin logs with date and sender role.
	2. Complete, sign, and return the requested disclosure/confidentiality agreement.
	3. Record delivered release/version (for example Onion v2) in `dataset_registry.md`.
	4. Record explicit allowed-use and redistribution terms verbatim.
	5. Record required citations and map to thesis references.

## Fallback Governance Rule
When an external dataset is delayed or term-restricted, retain the currently verified corpus as active and track the external dataset as fallback/reference only. Any corpus switch must pass:
1. License compatibility check.
2. Version and provenance completeness check.
3. Minimal schema/compatibility smoke test for affected implementation stages.


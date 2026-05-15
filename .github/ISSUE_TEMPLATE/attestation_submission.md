---
name: Attestation Submission
about: Submit historical name attestations from primary sources
title: "data: attestations from [SOURCE] for [REGION]"
labels: data, attestation
---

## Source Information

- **Source name:** 
- **Source type:** (primary / critical edition / secondary / gazetteer / map)
- **Source ID in sources.jsonl:** 
- **Date range of attestations:** 
- **License:** 

## Attestation Summary

- **Number of attestations:** 
- **Region/Country:** 
- **Language(s):** 
- **Time period:** 

## Quality Checks Completed

- [ ] Source registered in `databank/sources.jsonl`
- [ ] All required fields present (`form`, `language_code`, `year_from`, `source`)
- [ ] Schema validation passes (`uv run toponymia databank validate --schema attestation`)
- [ ] Deduplication check run (`uv run toponymia databank dedup --check`)
- [ ] Language codes are correct ISO 639-3 for the historical period
- [ ] Dates use original document dating (not copy/publication date)
- [ ] Unicode NFC normalization applied
- [ ] No personal data of living individuals
- [ ] Source license allows inclusion

## Notes

<!-- Any anomalies, uncertain readings, or editorial decisions made -->

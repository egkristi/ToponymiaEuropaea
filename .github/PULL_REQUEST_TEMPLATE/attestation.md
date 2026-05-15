## Attestation Data PR

### Source
- **Source:** <!-- e.g., Diplomatarium Norvegicum, bind I -->
- **Source ID:** <!-- e.g., DN_I -->
- **Citation format:** <!-- e.g., "DN I <doc_number>, <year>" -->

### Scope
- **Attestations added:** <!-- number -->
- **Region:** <!-- e.g., Vestland, Norway -->
- **Date range:** <!-- e.g., 1050–1350 -->
- **Language(s):** <!-- e.g., Old Norse (non), Latin (lat) -->

### Quality Checklist

- [ ] Source registered in `databank/sources.jsonl`
- [ ] Schema validation passes: `uv run toponymia databank validate --schema attestation`
- [ ] Deduplication check: `uv run toponymia databank dedup --check <file>`
- [ ] Integrity checksums updated: `uv run toponymia databank integrity --update`
- [ ] All forms are Unicode NFC-normalized
- [ ] Language codes use historical forms (e.g., `non` not `nob` for Old Norse)
- [ ] Dates verified against source (not publication date of edition)
- [ ] Confidence values assigned for uncertain readings
- [ ] No copyright-infringing transcriptions
- [ ] No personal data of living individuals

### Transcription Decisions

<!-- Document any editorial decisions:
- How abbreviations were expanded
- How damaged text was handled
- Dialect normalization choices
- Date estimation methodology
-->

### Sample Records

<!-- Paste 2-3 example attestation records showing the format -->

```json

```

### Testing

- [ ] `uv run pytest tests/ --ignore=tests/test_pipelines/test_dedup.py` passes
- [ ] CI pipeline green

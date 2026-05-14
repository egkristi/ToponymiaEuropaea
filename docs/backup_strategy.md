# Database Backup Strategy

## Overview

The Toponymia Europaea databank is version-controlled in Git, providing built-in
history and recoverability. This document describes the additional backup layers.

## Backup Layers

### Layer 1: Git History (Primary)

- All JSONL data files are tracked in the `databank/` directory
- Every change is committed with a descriptive message
- Full history available via `git log databank/`
- Recovery: `git checkout <commit> -- databank/`

### Layer 2: GitHub (Remote Redundancy)

- All commits are pushed to GitHub (`egkristi/ToponymiaEuropaea`)
- GitHub provides geographic redundancy and availability guarantees
- Recovery: `git clone` or `git pull`

### Layer 3: Tagged Releases (Archival Snapshots)

- Semver-tagged releases (e.g., `v0.3.0`) create immutable snapshots
- GitHub Releases include built distributions
- Each tag preserves the exact state of the databank at that version
- Recovery: `git checkout v0.3.0 -- databank/`

### Layer 4: SHA-256 Integrity Verification

- `databank/MANIFEST.sha256` contains checksums for all records
- `uv run toponymia databank verify` validates integrity
- Detects corruption, unauthorized modifications, or incomplete restores

## Backup Schedule

| Action | Frequency | Automated |
|--------|-----------|-----------|
| Git commit + push | Per change | Yes (CI) |
| Integrity verification | Per CI run | Yes |
| Tagged release | Per milestone | Manual |

## Recovery Procedures

### Corrupted local copy
```bash
git fetch origin
git reset --hard origin/main
uv run toponymia databank verify
```

### Restore specific version
```bash
git checkout v0.3.0 -- databank/
uv run toponymia databank verify
```

### Verify after restore
```bash
uv run toponymia databank verify
# Expected output: All records valid, checksums match
```

## Future Enhancements

- Automated nightly export to cloud storage (when data exceeds git-friendly size)
- PostgreSQL `pg_dump` backups (when operational store is deployed)
- Parquet snapshot archival to object storage

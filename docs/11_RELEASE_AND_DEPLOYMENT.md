# 11_RELEASE_AND_DEPLOYMENT — AMNION-ORACLE
## Release & Deployment

**Project:** AMNION-ORACLE  
**Type:** Release, packaging and deployment specification  
**Status:** Documentation-first (non-clinical)

---

## Non-medical / non-clinical disclaimer

AMNION-ORACLE is a concept-level engineering reference.  
It is NOT a medical device and NOT intended for clinical use.

---

## Purpose

Define what constitutes a valid release of AMNION-ORACLE, how artifacts are packaged, and how integrity and reproducibility are guaranteed.

---

## Release types

### R1 — Documentation-only release
- Docs updated  
- No executable reference code  

### R2 — Reference implementation release
- Docs + minimal simulator code  
- Tests included  

### R3 — Experimental integration release
- Docs + simulator  
- Optional hardware adapters  

---

## Canonical release artifact set

Each release MUST include:

- /docs/  
- /controller/  
- /configs/  
- /tests/  
- README.md  
- LICENSE  
- RELEASE_NOTES.md  
- sha256_manifest.txt  

---

## Manifest and hashing

For every file in the release bundle:

```text
sha256(file) -> sha256_manifest.txt
```

Manifest line format:

```text
<sha256> <relative_path>
```

Example:

```text
e3b0c44298fc1c149afbf4c8996fb924... docs/02_ARCHITECTURE.md
```

---

## Release ID

```text
release_id = YYYYMMDD-HHMM-<short_hash>
```

Example:

```text
20260201-2315-a9f3c2b
```

---

## Integrity verification procedure

User verifies:

- Download release bundle  
- Compute sha256 of all files  
- Compare with sha256_manifest.txt  
- If any mismatch -> release is invalid  

---

## Deterministic rebuild expectation

Given:

- same release version  
- same configs  
- same inputs  

Simulator output and logs MUST be identical.

---

## Deployment modes

### D1 — Local simulator
- clone repo  
- install dependencies  
- run simulator entrypoint  

### D2 — Host controller
- run control loop on host  
- connect to IO adapters  

### D3 — Embedded target (future)
- flash firmware  
- connect monitoring host  

---

## Versioning scheme

```text
Major.Minor.Patch
```

- Major — architecture change  
- Minor — module/interface change  
- Patch — docs/tests/typos  

Example:

```text
v1.2.0
```

---

## Release notes

Each release MUST include RELEASE_NOTES.md:

- summary of changes  
- breaking changes  
- known limitations  
- test status  

---

## Distribution channels

Primary:
- GitHub Releases  

Optional mirrors:
- Zenodo  
- IPFS (future)  

---

## End-of-life policy

Old releases remain available.  
No silent replacement.  
Only new tagged releases.

---

## Summary

Release process guarantees:

- traceability  
- reproducibility  
- integrity  
- long-term availability

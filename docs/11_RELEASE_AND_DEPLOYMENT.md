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

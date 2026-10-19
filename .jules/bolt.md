## 2025-02-23 - Pre-computed Dict Lookups for UID Parsing
**Learning:** Parsing raw UID strings (like "UID1") during polling loops introduced overhead from string operations (`removeprefix`) and repeated lookups (`UID_LOOKUP` + `DECODERS`). Pre-computing a direct map `{"UID1": (key, decoder)}` eliminated slice/parse steps and reduced dictionary lookups to O(1), yielding a ~27% speedup in local device payload parsing.
**Action:** Look for string-keyed dictionary lookups in repetitive loops and pre-compute key-to-handler mappings at module initialization.

## 2025-05-18 - Pre-computing device blocking error status
**Learning:** `BrinkHomeDeviceEntity.has_blocking_error` and `BrinkCoordinator.has_blocking_error` were filtering `device.alerts` repeatedly on every `available` check and state update across every entity. With dozens of entities per device, this created O(N_entities * M_alerts) redundant list iterations per coordinator update cycle. Pre-computing `has_blocking_error` during `BrinkDeviceData` initialization in `api.py` converted this to an O(1) attribute lookup.
**Action:** Whenever an entity property or coordinator property inspects nested list data that is immutable for a given update cycle, pre-calculate it once on the dataclass/model during data fetching instead of computing it dynamically in property getters.

## 2025-02-23 - Pre-computed Dict Lookups for UID Parsing
**Learning:** Parsing raw UID strings (like "UID1" or "1") introduced overhead from string operations (`removeprefix`) and repeated lookups (`UID_LOOKUP` + `DECODERS`). Pre-computing a direct map `{"UID1": (key, decoder), "1": (key, decoder)}` eliminated slice/parse steps and reduced dictionary lookups to O(1), yielding a ~27% speedup in local device payload parsing for local interface callers.
**Action:** Look for string-keyed dictionary lookups in repetitive loops and pre-compute key-to-handler mappings at module initialization.

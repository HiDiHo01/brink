## 2025-05-18 - Pre-computing device blocking error status

**Learning:** `BrinkHomeDeviceEntity.has_blocking_error` and `BrinkCoordinator.has_blocking_error` were filtering `device.alerts` repeatedly on every `available` check and state update across every entity. With dozens of entities per device, this created O(N_entities * M_alerts) redundant list iterations per coordinator update cycle. Pre-computing `has_blocking_error` during `BrinkDeviceData` initialization in `api.py` converted this to an O(1) attribute lookup.

**Action:** Whenever an entity property or coordinator property inspects nested list data that is immutable for a given update cycle, pre-calculate it once on the dataclass/model during data fetching instead of computing it dynamically in property getters.

## 2025-05-19 - Dataclass Caching without Polluting Dataclass Fields

**Learning:** When caching computed properties on a frozen dataclass instance (such as Home Assistant's `SelectEntityDescription`), adding a default field to the dataclass definition adds it to `__init__`, `__eq__`, `__repr__`, and `__hash__`. Mutating this field later via `object.__setattr__` breaks equality comparisons (`__eq__`) between dataclass instances. Using dynamic attribute caching via `object.__getattribute__` and `object.__setattr__` with a un-declared attribute name avoids polluting dataclass comparison semantics.

**Action:** Avoid declaring private dataclass fields solely for caching in frozen dataclasses. Use `object.__getattribute__` / `object.__setattr__` for lazy instance caching when `cached_property` cannot be applied.

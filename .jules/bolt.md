## 2025-05-18 - Pre-computing device blocking error status

**Learning:** `BrinkHomeDeviceEntity.has_blocking_error` and `BrinkCoordinator.has_blocking_error` were filtering `device.alerts` repeatedly on every `available` check and state update across every entity. With dozens of entities per device, this created O(N_entities * M_alerts) redundant list iterations per coordinator update cycle. Pre-computing `has_blocking_error` during `BrinkDeviceData` initialization in `api.py` converted this to an O(1) attribute lookup.

**Action:** Whenever an entity property or coordinator property inspects nested list data that is immutable for a given update cycle, pre-calculate it once on the dataclass/model during data fetching instead of computing it dynamically in property getters.

## 2025-05-19 - Single-pass evaluation for entity extra state attributes

**Learning:** `attr_fn` on the `blocking_error` binary sensor was accessing `entity.coordinator.active_alerts` 4 times per state attribute dictionary construction, triggering redundant list comprehensions across all devices and alerts. It also ran two separate `max()` generator expressions over the same list to extract `.name` and `int(...)`. Refactoring `attr_fn` into a single-pass helper function fetched `active_alerts` once, evaluated `max(alert.level)` once, and eliminated redundant list allocations and iterations.

**Action:** Avoid calling property getters that compute/allocate lists multiple times inside dictionary constructors or lambdas; store the property return value in a local variable and compute aggregate metrics in a single pass.

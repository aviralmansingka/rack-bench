# Certification profile schema (MVP design)

Status: design. Not yet implemented. This document defines the `--config`
profile: the single input that turns rack-bench from observation-only inventory
into graded certification.

## Principles

1. **One TOML file per cluster type**, checkable into git. TOML over YAML for
   comments and fewer footguns.
2. **Every key is consumed** by an existing check, or explicitly stamped
   (bench/smoke sections land their values now, consumed when those stages
   arrive). Unknown keys are rejected at load — fail fast on typos.
3. **No profile = observation-only** (today's behavior). Loading a profile is
   what makes `expected` non-null and turns mismatches into `FAIL`.
4. **Deployment-model conditionals**: the same observation can be healthy on one
   model and a finding on another. The profile declares the model.
5. **Versioned**: `schema_version = 1`; the profile's hash is stamped into every
   result envelope so any number in any report traces to the exact thresholds
   that produced it.

## Sections

### `[profile]` — identity

- `name` (string, required): e.g. `dev-homelab`, `modal-b200`, `nv72`.
- `schema_version` (int, required, must equal 1).
- `description` (string, optional).

### `[unit]` — the certification unit

- `model` (string, required): one of `dev` | `single-tenant-perf` |
  `multi-tenant`. Drives isolation expectations.
- `hosts` (table of group name → list/pattern, optional in MVP since `--hosts`
  fan-out is not implemented): e.g. `all-nodes = ["tray01", "tray02"]`. Stamped
  only for now.

### `[hardware]` — expected values diffed by audit checks

| Key                                                | Consumed by                               |
| -------------------------------------------------- | ----------------------------------------- |
| `cpu_model`                                        | `system.cpu` (FAIL on model mismatch)     |
| `memory_gib` (±2%)                                 | `system.memory`                           |
| `dram_gib` (±2%)                                   | `system.dram` (graded only when readable) |
| `gpu_model` / `gpu_count` / `gpu_memory_mib` (±2%) | `gpu.inventory`                           |
| `gpu_ecc` / `gpu_mig` (expected mode strings)      | `gpu.ecc`, `gpu.mig`                      |
| `nvlink_links_per_gpu`                             | `nvlink.links_per_gpu`                    |
| `numa_nodes`                                       | `topology.numa`                           |

Absent keys = that check stays observation-only. Partial profiles are valid;
grade only what you declare.

### `[security]` — floors and isolation expectations

- `[security.minimums]` — string version floors, consumed by the `*_cve_floor`
  checks (replacing the embedded placeholder table): `nvidia_driver`, `cuda`,
  `runc`, `docker`, `nvidia_container_toolkit`, `connectx_firmware`, `dcgm`,
  `dcgm_exporter`, `kernel`.
- `known_bad_kernels` (list of strings) — consumed by
  `security.known_bad_kernels`.
- `iommu_passthrough_allowed` (bool) — consumed by `security.iommu`. Derived
  default from `[unit].model`: false for `multi-tenant`, true for `dev` and
  `single-tenant-perf` (overridable).

### `[software.pins]` — golden-stack expectations

Map of component → expected version, diffed against the software manifest per
host; mismatch is WARN in `dev`, FAIL otherwise.

### `[bench]` and `[smoke]` — stamped now, consumed by later stages

Values are validated for type/range at load (so typos fail immediately) but no
check reads them until the stages land. Shape:

```toml
[bench.gpu]
gemm_fp8_pct_of_spec = 95        # int 1-100
mem_bw_pct_of_spec = 90

[bench.network]
allreduce_busbw_gbs_min = 380    # positive number

[bench.storage]
randwrite_iops_min = 100000
fsync_p99_ms_max = 10

[smoke]
duration = "4h"                  # duration string
bandwidth_degradation_max_pct = 5
```

### Deliberately NOT in the MVP

- **Credentials** (BMC/Redfish, switch, DPU, UFM, ssh): nothing reachable needs
  them; designing secret storage hastily is worse than deferring.
- Rack-level fields (expected tray count), topology maps, addressing
  expectations. They arrive with `--hosts` and the credential work.

## Validation rules (load time)

- Types and ranges per table above; unknown keys rejected with the offending
  path; `schema_version` mismatch rejected.
- Cross-checks: `nvlink_links_per_gpu` in 1-18; percentages 1-100; memory
  tolerances compiled to absolute bounds at load.

## Grading semantics

A check with a matching profile entry gets `expected` populated and its status
becomes FAIL (or WARN where the schema says so) on mismatch; checks without
entries stay PASS-on-observed. The envelope gains a top-level `profile` block:
`{name, schema_version, sha256}`.

## MVP scope, given no NVL72 access

Reachable targets today: the homelab (Ryzen/RTX 3060), Modal b200 and b200:8
(gVisor-limited). The MVP therefore grades exactly what those can observe, and
the NVL72 keys exist but simply stay unset until hardware arrives:

1. `dev-homelab.toml` — full example below; immediately gradeable: cpu, memory,
   gpu inventory, ecc/mig modes, security floors for the installed stack
   (driver/docker/runc/toolkit), `iommu_passthrough_allowed = true` (dev model —
   the current iommu FAIL becomes a legitimate PASS).
2. `modal-b200.toml` — gpu model/count/memory only; gVisor hides the rest.
3. `nv72.toml` — target profile, keys present, values filled when racks are
   racked.

```toml
# dev-homelab.toml — the full MVP example
[profile]
name = "dev-homelab"
schema_version = 1

[unit]
model = "dev"

[hardware]
cpu_model = "AMD Ryzen 9 7950X 16-Core Processor"
memory_gib = 62
gpu_model = "NVIDIA GeForce RTX 3060"
gpu_count = 1
gpu_memory_mib = 12288
gpu_ecc = "absent"
gpu_mig = "absent"

[security]
iommu_passthrough_allowed = true

[security.minimums]
nvidia_driver = "595.0"
docker = "27.0"
runc = "1.1.12"
nvidia_container_toolkit = "1.17.0"

[software.pins]
cuda = "13.1"
glibc = "2.39"
```

## Implementation plan (next PR)

1. `rack_bench/common/config.py`: loader + validation → frozen `Profile`.
2. `cli.py`: `--config <file>` wiring (flag already accepted, currently unused).
3. Runner threads the profile into `collect()`; consuming checks read their
   expected values; envelope gains the `profile` block.
4. Security floors fall back to the embedded placeholders only when no profile
   supplies minimums.
5. Tests: load/validate/reject paths, grading on/off per key, envelope stamping,
   the homelab example round-trip.

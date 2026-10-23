# Ruff 0.17.2 z/OS cross-build patch set

This directory records the complete source changes used for the published
`s390x-ibm-zos` Ruff 0.17.2 executable.

## Contents

- `ruff-0.17.2-zos.patch` — Ruff workspace changes.
- `Cargo.lock.zos` — exact resolved lockfile.
- `dependencies/*.patch` — patches for every modified registry dependency.
- `rustc-procmacro-wrapper.sh` — injects Cargo's exact PowerPC host proc macros.
- `zos_ruff_stubs.c` — compatibility implementations for advisory clock APIs.

The dependency patches are version-specific. Apply them to clean sources for
the exact versions named in each filename and place the resulting directories
under `zos-deps/` using the path names in the workspace `[patch.crates-io]`
table. Copy `Cargo.lock.zos` over `Cargo.lock`; do not regenerate it.

## Toolchain compatibility

Ruff 0.17.2 declares Rust 1.97, while the IBM cross toolchain is Rust 1.86.
The patch uses targeted nightly feature gates under `RUSTC_BOOTSTRAP=1` and
small equivalent rewrites for APIs absent from 1.86. Dependency versions remain
those in Ruff's release lockfile.

The z/OS changes also:

- reuse the established z/OS libc, rustix, nix, filetime, getrandom, and zstd
  compatibility work;
- exclude Linux assembly from `psm` and use its supported no-stack-switching
  fallback;
- exclude unsupported pseudo-terminal and termios extensions;
- provide `clock_getres` and an `ENOSYS` `clock_settime` shim;
- retain one codegen unit and disable LTO for GOFF-safe linking.

## Build

Build the compatibility archive first:

```sh
s390x-ibm-zos-cc -O2 -c zos_ruff_stubs.c -o zos_ruff_stubs.o
llvm-ar rcs libzos_ruff_stubs.a zos_ruff_stubs.o
```

Then build Ruff:

```sh
export RUSTC_BOOTSTRAP=1
export CARGO_TARGET_S390X_IBM_ZOS_LINKER=/path/to/s390x-ibm-zos-cc
export CARGO_TARGET_S390X_IBM_ZOS_AR=/path/to/s390x-ibm-zos-ar
export RUSTC_WRAPPER=/path/to/rustc-procmacro-wrapper.sh
export RUFF_HOST_DEPS_DIR="$PWD/target/zos/deps"
export RUSTFLAGS='-C target-feature=-vector \
  -C link-arg=/path/to/libzos_mlock_stubs.a \
  -C link-arg=/path/to/libzos_ruff_stubs.a'

cargo build --profile zos --target s390x-ibm-zos \
  --bin ruff --ignore-rust-version --jobs 1
```

The host proc-macro directory must contain the exact artifacts Cargo builds for
this invocation. In particular, Ruff resolves both thiserror 1 and 2, so the
wrapper selects the matching derive artifact while compiling each runtime
crate.

## Artifact

- Size: 149,835,776 bytes
- SHA-256:
  `e104064398bbca3105375dbd2f7c850d788c5879f1ce6c7bfffbf0769bf34628`

Validated directly on z/OS:

- `ruff --version`
- `ruff --help`
- lint detection with `ruff check`
- safe correction with `ruff check --fix`
- format detection with `ruff format --check`
- source rewriting with `ruff format`
- recursive directory discovery

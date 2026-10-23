# ruffport

[Ruff](https://github.com/astral-sh/ruff) for z/OS.

Ruff is an extremely fast Python linter and code formatter written in Rust. This
port publishes a standalone `s390x-ibm-zos` executable cross-compiled with the
IBM Rust 1.86 toolchain.

## Install

```sh
zopen install ruff
```

## Use

```sh
ruff --version
ruff check .
ruff check --fix .
ruff format --check .
ruff format .
```

## Current release

- Ruff: 0.17.2
- Target: `s390x-ibm-zos`
- Binary SHA-256:
  `e104064398bbca3105375dbd2f7c850d788c5879f1ce6c7bfffbf0769bf34628`

Validated directly on z/OS with version/help output, lint detection, safe fixes,
format checks, formatting, and recursive source discovery.

## Reproducible patch set

The complete source and dependency patch collection is in
[`patches/ruff-0.17.2`](patches/ruff-0.17.2/README.md). It includes the exact
Cargo lockfile, proc-macro wrapper, compatibility stubs, build profile, MSRV
compatibility changes, and all dependency patches used for the released binary.

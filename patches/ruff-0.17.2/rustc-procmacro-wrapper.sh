#!/bin/bash
set -e
RUSTC="$1"
shift

is_zos=0
for arg in "$@"; do
    if [[ "$arg" == "s390x-ibm-zos" ]]; then
        is_zos=1
        break
    fi
done
[[ "$is_zos" == 1 ]] || exec "$RUSTC" "$@"

# Cargo's z/OS cross invocation can omit host proc-macro externs. Inject the
# exact artifacts Cargo built for this profile; these run on the PowerPC host.
deps=${RUFF_HOST_DEPS_DIR:-"$PWD/target/zos/deps"}
extra=()
declare -A seen=()
shopt -s nullglob
for artifact in "$deps"/lib*.so; do
    base=${artifact##*/lib}
    name=${base%-*.so}
    [[ "$name" == thiserror_impl ]] && continue
    [[ -n "${seen[$name]:-}" ]] && continue
    seen[$name]=1
    extra+=(--extern "$name=$artifact")
done

# Ruff resolves both thiserror 1 and 2. Inject the matching derive while
# compiling the thiserror runtime crate so its macro re-export has the correct
# metadata. Selecting by whichever artifact happens to sort first is invalid.
thiserror_major=""
for arg in "$@"; do
    case "$arg" in
        */thiserror-1.*/*) thiserror_major=1; break ;;
        */thiserror-2.*/*) thiserror_major=2; break ;;
    esac
done
if [[ -n "$thiserror_major" ]]; then
    for artifact in "$deps"/libthiserror_impl-*.so; do
        if strings "$artifact" 2>/dev/null | grep -q "/thiserror-impl-${thiserror_major}\.0\."; then
            extra+=(--extern "thiserror_impl=$artifact")
            break
        fi
    done
fi

exec "$RUSTC" "$@" "${extra[@]}"

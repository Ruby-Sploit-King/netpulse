#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$(readlink -f -- "${BASH_SOURCE[0]}")")/.." && pwd)"
BIN="$HOME/.local/bin"
VENV="$ROOT/.venv"
NAME="netpulse"

die() {
    printf '\033[1;31m[ERROR]\033[0m %s\n' "$*" >&2
    exit 1
}

require() {
    command -v "$1" >/dev/null 2>&1 || die "Missing dependency: $1"
}

prepare_python() {
    if [[ ! -x "$VENV/bin/python" ]]; then
        require python3
        python3 -m venv "$VENV" || die "Could not create Python virtual environment. Install python3-venv."
    fi

    if ! "$VENV/bin/python" -c 'import rich' >/dev/null 2>&1; then
        "$VENV/bin/python" -m pip install -r "$ROOT/requirements.txt" ||
            die "Python dependency installation failed."
    fi
}

build_project() {
    require cmake
    require c++
    require go

    cmake -S "$ROOT/cpp" -B "$ROOT/build/cpp" -DCMAKE_BUILD_TYPE=Release
    cmake --build "$ROOT/build/cpp" --parallel

    (
        cd "$ROOT/go"
        go test ./...
        go vet ./...
        go build -o "$ROOT/build/netpulse-net" ./cmd/netpulse-net
    )

    [[ -x "$ROOT/build/cpp/netpulse-core" ]] ||
        die "C++ core was not created."
    [[ -x "$ROOT/build/netpulse-net" ]] ||
        die "Go networking binary was not created."
}

install_project() {
    require python3
    prepare_python
    build_project

    mkdir -p "$BIN"
    ln -sfn "$ROOT/scripts/netpulse" "$BIN/$NAME"
    ln -sfn "$ROOT/scripts/netpulse" "$BIN/NetPulse"
    chmod +x "$ROOT/scripts/netpulse"

    printf '\nInstalled command: %s (alias: NetPulse)\n' "$BIN/$NAME"

    case ":${PATH}:" in
        *":$BIN:"*) ;;
        *) printf 'Add this to ~/.bashrc or ~/.zshrc:\nexport PATH="$HOME/.local/bin:$PATH"\n' ;;
    esac

    printf 'Run: %s\n' "$NAME"
}

uninstall_project() {
    local removed=0

    for name in "$NAME" "NetPulse"; do
        if [[ -L "$BIN/$name" ]]; then
            target="$(readlink -f -- "$BIN/$name" || true)"
            if [[ "$target" == "$ROOT/scripts/netpulse" ]]; then
                rm -- "$BIN/$name"
                printf 'Removed global command: %s\n' "$name"
                removed=1
            fi
        fi
    done

    [[ "$removed" == 1 ]] ||
        die "No matching NetPulse launcher found in $BIN."
}

case "${1:-}" in
    --install)
        install_project
        exit 0
        ;;
    --uninstall)
        uninstall_project
        exit 0
        ;;
    --build)
        prepare_python
        build_project
        exit 0
        ;;
esac

[[ -d "$ROOT" ]] || die "Project directory not found."
prepare_python

if [[ ! -x "$ROOT/build/cpp/netpulse-core" ||
      ! -x "$ROOT/build/netpulse-net" ]]; then
    build_project
fi

export NETPULSE_CORE="$ROOT/build/cpp/netpulse-core"
export NETPULSE_NET="$ROOT/build/netpulse-net"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

exec "$VENV/bin/python" "$ROOT/main.py" "$@"


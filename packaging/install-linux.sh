#!/usr/bin/env sh
set -eu

prefix="${PREFIX:-/usr/local}"
bindir="${BINDIR:-$prefix/bin}"
source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
source_bin="$source_dir/bin/codex-token-usage"
target_bin="$bindir/codex-token-usage"

if [ ! -x "$source_bin" ]; then
  echo "missing executable: $source_bin" >&2
  exit 1
fi

mkdir -p "$bindir"
cp "$source_bin" "$target_bin"
chmod 755 "$target_bin"

echo "installed $target_bin"

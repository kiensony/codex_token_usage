#!/usr/bin/env bash
set -euo pipefail

python_bin="${PYTHON_BIN:-python3}"
pip_install_args=()

if [ -n "${PIP_INSTALL_ARGS:-}" ]; then
  # Split simple pip option lists such as "--user".
  read -r -a pip_install_args <<< "${PIP_INSTALL_ARGS}"
elif [ -z "${VIRTUAL_ENV:-}" ]; then
  pip_install_args=(--user)
fi

project_root="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

"$python_bin" -m pip install "${pip_install_args[@]}" --upgrade pip
"$python_bin" -m pip install "${pip_install_args[@]}" pyinstaller
"$python_bin" -m pip install "${pip_install_args[@]}" .

PYTHONPATH=src "$python_bin" -m unittest discover -s tests

"$python_bin" -m PyInstaller \
  --clean \
  --noconfirm \
  --onefile \
  --name codex-token-usage \
  --collect-data codex_token_usage \
  packaging/pyinstaller_entry.py

./dist/codex-token-usage --help
./dist/codex-token-usage --format json --codex-home "${RUNNER_TEMP:-/tmp}/missing-codex-home"

version="$("$python_bin" -c 'import codex_token_usage; print(codex_token_usage.__version__)')"
package="codex-token-usage-${version}-linux-x86_64"
package_dir="dist/${package}"

mkdir -p "$package_dir/bin"
cp dist/codex-token-usage "$package_dir/bin/codex-token-usage"
cp packaging/install-linux.sh "$package_dir/install.sh"
chmod 755 "$package_dir/bin/codex-token-usage" "$package_dir/install.sh"
tar -C dist -czf "dist/${package}.tar.gz" "$package"
sha256sum "dist/${package}.tar.gz" "dist/codex-token-usage" > "dist/${package}.sha256"
printf 'PACKAGE_NAME=%s\n' "$package" > dist/linux-binary.env

#!/bin/bash
set -v
set -e

pushd ../../ ; jlpm run build:jupyterlab ; popd
rm -f core_version.py; cp ../../../core/optumi_core/_version.py core_version.py

# Override the version of optumi_core in the pyproject.toml file
core_version=$(python3 -c "exec(open('core_version.py').read()); print(__version__)")
suffix=$(echo $core_version | awk -F '-' '{print $2}' | tr '[:upper:]' '[:lower:]' || "")
split=($(echo $core_version | awk -F '-' '{print $1}' | tr '.' ' '))

if [[ $suffix != "" ]] && [[ $suffix == "a"* ]]; then
    core_dependency_string=""
else
    core_dependency_string="~=${split[0]}.${split[1]}.${split[2]}"
fi

sed -i "s/^ *\"optumi_core.*$/    \"optumi_core$core_dependency_string\",/" pyproject.toml

rm -rf build/; rm -rf dist/; rm -rf *.egg-info/; python3 -m build -ws

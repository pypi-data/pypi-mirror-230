#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $DIR

COMMAND="${1}"
echo COMMAND=$COMMAND

VERSION_NAME=$(sed -n '/__version__/{s/__version__//;s/\"//g;s/ //g;s/=//;p;q;}' src/excel2x/__init__.py)
echo "VERSION_NAME="$VERSION_NAME

sed -i '' "s/version = .*/version = \"$VERSION_NAME\"/g" pyproject.toml

if [[ "$COMMAND" == "clean" ]]; then
    rm -rf dist/*
    rm -rf build/*
    exit 0
fi
if [[ "$COMMAND" =~ "build" ]]; then
    rm -rf dist/*
    rm -rf build/*
    python3 -m build
fi

if [[ "$COMMAND" =~ "upload_release" ]]; then
    python3 -m twine upload --repository pypi dist/*
fi

if [[ $COMMAND =~ "upload_test" ]]; then
    python3 -m twine upload --repository pypi dist/*
fi

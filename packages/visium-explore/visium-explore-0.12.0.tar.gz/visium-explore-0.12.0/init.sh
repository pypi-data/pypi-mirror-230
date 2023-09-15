#!/usr/bin/env bash

cd example
pipenv run dvc repro
pipenv run explore
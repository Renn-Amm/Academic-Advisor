#!/usr/bin/env bash
# Install essential build tools before pip installs project dependencies
pip install --upgrade pip setuptools wheel build
pip install -r requirements.txt

#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Cria pasta de cache para a IA não dar erro de permissão
mkdir -p .u2net
export U2NET_HOME=$(pwd)/.u2net

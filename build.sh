#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

flask init-db
flask seed-db --books 100 --borrowers 20 --loans 30
flask rebuild-recs

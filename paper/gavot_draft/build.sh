#!/usr/bin/env bash
# Compile every build in this folder and collect the PDFs in pdf/.
# Run from paper/gavot_draft. Needs pdflatex (MiKTeX) on PATH.
set -e
cd "$(dirname "$0")"
for j in main main_rewrite main_full appendix_standalone problem_formulation_standalone proposed_solution_standalone experiments_full_standalone; do
  pdflatex -interaction=nonstopmode -halt-on-error "$j.tex" >/dev/null
  pdflatex -interaction=nonstopmode -halt-on-error "$j.tex" >/dev/null
  grep -E "Output written" "$j.log"
  mv -f "$j.pdf" pdf/
done
rm -f *.aux *.log *.out

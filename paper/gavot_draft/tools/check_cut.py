# Read-only checks for the fit version (see review/CUT_LEDGER.md):
#  1. every numeric token in a *_short section also occurs in its full counterpart;
#  2. every \label and every bold paragraph head in a full section occurs in the short
#     section, in appendix.tex, or is named in review/CUT_LEDGER.md.
# Usage (from paper/gavot_draft):  ../../.venv/Scripts/python.exe tools/check_cut.py
import io, os, re, sys
D = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
def rd(*p): return io.open(os.path.join(D, *p), encoding="utf-8").read()
def strip_comments(s): return re.sub(r"(?m)^%.*$", "", s)
def nums(s): return set(re.findall(r"(?<![\w.])[+-]?\d*\.\d+|(?<![\w.])\d+(?:\.\d+)?", strip_comments(s)))
pairs = [("experiments_full.tex", "experiments_short.tex"),
         ("proposed_solution.tex", "proposed_solution_short.tex"),
         ("problem_formulation.tex", "problem_formulation_short.tex")]
app = rd("appendix.tex"); ledger = rd("review", "CUT_LEDGER.md")
ok = True
for full, short in pairs:
    F, S = strip_comments(rd("sections", full)), strip_comments(rd("sections", short))
    extra = sorted(nums(S) - nums(F), key=lambda x: (len(x), x))
    labels = re.findall(r"\\label\{([^}]*)\}", F)
    heads = re.findall(r"\\textbf\{([^}]*)\}", F)
    miss_l = [l for l in labels if ("\\label{" + l + "}") not in S and ("\\label{" + l + "}") not in app]
    miss_h = [h for h in heads if h not in S and h not in app and h.split(":")[-1].strip().rstrip(".") not in ledger]
    print(f"{short:32s} new numbers: {extra or 'none'}")
    print(f"{'':32s} labels lost: {miss_l or 'none'}")
    print(f"{'':32s} heads not in short/appendix/ledger: {miss_h or 'none'}")
    ok &= not extra and not miss_l and not miss_h
print("OK" if ok else "CHECK FAILED"); sys.exit(0 if ok else 1)

import io, re
diff = io.open("diff_vs_original.txt", encoding="utf-8").read().splitlines()
secs = [(91,"Sec. 1 Introduction (Contributions list)"),(166,"Sec. 2 Group-Blind SGD and its Surrogate"),
        (224,"Sec. 3 Alignment by Masked Optimal Transport"),(433,"Sec. 4 Risk-Averse Layer"),
        (489,"Sec. 5 Experiments"),(623,"Sec. 6 Conclusion / bibliography")]
def sec(n):
    s = "preamble"
    for L,name in secs:
        if n >= L: s = name
    return s
hunks = []; cur = None
for line in diff:
    if line.startswith("@@"):
        n = int(re.match(r"@@ -(\d+)", line).group(1)); cur = {"line": n, "old": [], "new": []}; hunks.append(cur)
    elif cur is None or line.startswith("---") or line.startswith("+++"):
        continue
    elif line.startswith("-"): cur["old"].append(line[1:])
    elif line.startswith("+"): cur["new"].append(line[1:])
    else: cur["old"].append(line[1:]); cur["new"].append(line[1:])
NL = chr(10)
out = ["# Paste-ready edits for main.tex (Herlock's GAVOT draft), 2026-09-15", "",
       "Each item: the block as it stands in the Overleaf now (FIND), and the block to put in its place (REPLACE WITH).",
       "Line numbers refer to the Overleaf main.tex as of 9/15. A few lines of unchanged context are included on both sides so the block is easy to locate with Ctrl+F.",
       "Two more files go with this: figs/severity_imdb.pdf (replaces severity_imdb.png; the includegraphics line below points at it) and, if an appendix page is allowed, appendix.tex pasted after the bibliography.", ""]
for k,h in enumerate(hunks,1):
    out += [f"## Edit {k}: {sec(h['line'])}, around line {h['line']}", "", "FIND:", "```latex", *h["old"], "```", "", "REPLACE WITH:", "```latex", *h["new"], "```", ""]
io.open("PASTE_FOR_HERLOCK.md","w",encoding="utf-8",newline=NL).write(NL.join(out))
print(len(hunks), "edits;", sum(len(h["old"])+len(h["new"]) for h in hunks), "lines")

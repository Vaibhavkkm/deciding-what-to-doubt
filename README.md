# Deciding What to Doubt

Reading report for the course **Advanced Topics in Mathematical Modelling**
(Master in Mathematics, University of Luxembourg, August 2026).

The report traces the statistical lineage of automated quality control for
environmental sensor networks through five core readings, from Grubbs (1969)
to Leigh et al. (2019), following the course's five-role structure:
Historians, Technicians, Experimentalists, Futurists and Critics. The
Experimentalists section reproduces the central behaviours of the methods in
Python on a seeded synthetic benchmark, so every number and figure in the
report is exactly reproducible from this repository.

The compiled report is [`report.pdf`](report.pdf) (39 pages).

## Repository layout

```
main.tex           document shell, cover page, abstract, statements
sections/          one .tex file per section, plus the appendices
references.bib     all 24 references, details verified against the sources
figures/           the seven figures, PNG at 300 dpi (committed, and
                   regenerable from code/)
code/              experiments.py, figures.py and their outputs
report.pdf         the compiled report
requirements.txt   Python dependencies for the experiments
```

## Compiling the report

The figures are separate PNG files that `main.tex` pulls in from `figures/`
via `\graphicspath`, so the folder structure must stay intact.

**Overleaf:** use New Project, then Upload Project, and upload the zip of
this repository in one piece. Set `main.tex` as the main document, compiler
pdfLaTeX. Do not copy `main.tex` alone into a blank project: without the
`figures/` and `sections/` folders next to it, the images and sections
cannot be found.

**Command line:**

```bash
latexmk -pdf main.tex
```

or the classic sequence `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`.

## Reproducing the experiments and figures

```bash
pip install -r requirements.txt
cd code
python3 experiments.py   # builds the benchmark, runs all detectors,
                         # writes results.json and bench.npz (2 to 3 min)
python3 figures.py       # renders the seven PNGs into ../figures/
```

Every random number generator is explicitly seeded, so re-runs reproduce
the published numbers and figures bit for bit. `code/results.json` holds the
exact values behind the detector comparison matrix; `code/bench.npz` is the
saved benchmark state that lets `figures.py` run without re-running the
detectors.

## Statement on the use of AI tools

This report was prepared with the assistance of a large language model
(Claude, Anthropic), used with the prior written permission of the course
responsible. The full statement is on page 2 of the report; the author has
reviewed and takes responsibility for all content, code and citations.

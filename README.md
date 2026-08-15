# Deciding What to Doubt

*How automated quality control for environmental sensor networks learned what
to distrust.*

Reading report for the course **Advanced Topics in Mathematical Modelling**
(Master of Science in Mathematics, University of Luxembourg, August 2026),
written alongside an internship at the Luxembourg Institute of Science and
Technology, ENVISION unit.

The report follows five core readings, from Grubbs (1969) to Leigh et al.
(2019), using the course's five roles: Historian, Technician,
Experimentalist, Futurist and Critic. The Experimentalist section reproduces
the central behaviours of the methods in Python on a seeded synthetic
benchmark, so every number and figure in the report is exactly reproducible
from this repository.

## Repository layout

```
main.tex           preamble, title page, summary, AI statement,
                   acknowledgments and table of contents
sections/          one .tex file per section, plus the bibliography
references.bib     fuller reference list, kept from the long draft
figures/           figures as PNG at 300 dpi (committed, and regenerable
                   from code/), plus the university logo
code/              experiments.py, figures.py and their outputs
requirements.txt   Python dependencies for the experiments
```

`sections/` holds, in order: introduction, the five role sections, the
practical design rules, the conclusion, the reproducibility note and
`bibliography.tex`.

The submitted version carries its bibliography inline in
`sections/bibliography.tex`, so **no BibTeX pass is needed**.
`references.bib` is retained because it holds the fuller reference list
compiled for the longer draft; the submitted report does not read it.

Of the seven figures produced by `code/figures.py`, the submitted report uses
five. `fig_modz.png` and `fig_citations.png` are still generated and
committed, but are not included by any section.

## Compiling the report

The figures are separate PNG files that `main.tex` pulls in from `figures/`
via `\graphicspath`, so the folder structure must stay intact.

**Command line:**

```bash
latexmk -pdf main.tex
```

or run `pdflatex main.tex` twice, so the table of contents and the
cross-references resolve. There is no BibTeX step.

**Overleaf:** use New Project, then Upload Project, and upload the zip of
this repository in one piece. Set `main.tex` as the main document, compiler
pdfLaTeX. Do not copy `main.tex` alone into a blank project: without the
`figures/` and `sections/` folders next to it, the images and sections
cannot be found.

## Reproducing the experiments and figures

```bash
pip install -r requirements.txt
cd code
python3 experiments.py   # builds the benchmark, runs all detectors,
                         # writes results.json and bench.npz
python3 figures.py       # renders the PNGs into ../figures/
```

Every random number generator is explicitly seeded, so re-runs reproduce the
published numbers and figures. `code/results.json` holds the exact values
behind the detector comparison table and matrix figure; `code/bench.npz` is
the saved benchmark state that lets `figures.py` run without re-running the
detectors.

## Statement on the use of AI tools

In accordance with the University of Luxembourg's AI guidelines, generative
AI (Claude, Anthropic) was used for text improvement, proofreading,
restructuring and iterative feedback. It was used as an editorial aid, not to
generate the substantive analysis, experimental results, or conclusions from
the bottom up. The author has reviewed the report in full and can explain and
justify the work. The full statement is in the report's front matter.

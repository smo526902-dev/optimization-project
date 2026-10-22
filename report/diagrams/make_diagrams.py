"""Draw the report's analysis and design diagrams as SVG, then render them to PNG.

    .venv\\Scripts\\python report\\diagrams\\make_diagrams.py

Writes <name>.svg and <name>.png (rendered at 2x by headless Chrome, when
installed) into report/diagrams/. Notation follows UML 2: use-case, package,
class and activity diagrams, plus one data-flow diagram of the experiment.
"""
from __future__ import annotations

import asyncio
import base64
import json
import subprocess
import time
import urllib.request
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent
FONT = "Arial, Helvetica, sans-serif"
INK = "#1A1A1A"
DIM = "#555555"
GREEN = "#1E4D3F"
TINT = "#EEF2EC"
HEAD = "#DCE6DF"
NOTE = "#FFF8DC"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


class SVG:
    def __init__(self, width, height):
        self.w, self.h, self.parts = width, height, []

    def add(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill="#FFFFFF", stroke=INK, sw=1.4, rx=0, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def text(self, x, y, s, size=13, weight=400, anchor="middle", color=INK, italic=False):
        style = ' font-style="italic"' if italic else ""
        self.add(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
                 f'text-anchor="{anchor}" fill="{color}" dominant-baseline="middle"{style}>{escape(s)}</text>')

    def lines(self, x, y, rows, size=13, gap=17, anchor="middle", **kw):
        top = y - gap * (len(rows) - 1) / 2
        for i, r in enumerate(rows):
            self.text(x, top + i * gap, r, size=size, anchor=anchor, **kw)

    def path(self, points, stroke=INK, sw=1.4, dash=None, end=None, start=None):
        d = "M" + " L".join(f"{x} {y}" for x, y in points)
        attrs = f' stroke-dasharray="{dash}"' if dash else ""
        if end:
            attrs += f' marker-end="url(#{end})"'
        if start:
            attrs += f' marker-start="url(#{start})"'
        self.add(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"{attrs}/>')

    def ellipse(self, cx, cy, rx, ry, fill="#FFFFFF", stroke=INK, sw=1.4):
        self.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def circle(self, cx, cy, r, fill=INK, stroke=INK, sw=1.4):
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def polygon(self, pts, fill="#FFFFFF", stroke=INK, sw=1.4):
        p = " ".join(f"{x},{y}" for x, y in pts)
        self.add(f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def svg(self):
        defs = f"""<defs>
<marker id="arrow" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{INK}"/></marker>
<marker id="open" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="11" markerHeight="11" orient="auto-start-reverse"><path d="M1 1 L11 6 L1 11" fill="none" stroke="{INK}" stroke-width="1.4"/></marker>
<marker id="tri" viewBox="0 0 14 14" refX="13" refY="7" markerWidth="14" markerHeight="14" orient="auto-start-reverse"><path d="M1 1 L13 7 L1 13 z" fill="#FFFFFF" stroke="{INK}" stroke-width="1.3"/></marker>
<marker id="diamond" viewBox="0 0 18 10" refX="17" refY="5" markerWidth="18" markerHeight="10" orient="auto-start-reverse"><path d="M1 5 L9 1 L17 5 L9 9 z" fill="{INK}" stroke="{INK}" stroke-width="1"/></marker>
<marker id="odiamond" viewBox="0 0 18 10" refX="17" refY="5" markerWidth="18" markerHeight="10" orient="auto-start-reverse"><path d="M1 5 L9 1 L17 5 L9 9 z" fill="#FFFFFF" stroke="{INK}" stroke-width="1.2"/></marker>
</defs>"""
        body = "\n".join(self.parts)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
                f'{defs}<rect width="100%" height="100%" fill="#FFFFFF"/>{body}</svg>')


# ------------------------------------------------------------------ shapes
def actor(s, x, y, name):
    s.circle(x, y - 38, 11, fill="#FFFFFF")
    s.path([(x, y - 27), (x, y + 8)])
    s.path([(x - 22, y - 14), (x + 22, y - 14)])
    s.path([(x - 18, y + 36), (x, y + 8), (x + 18, y + 36)])
    s.text(x, y + 54, name, size=14, weight=700)


def usecase(s, cx, cy, label, rx=185, ry=30):
    s.ellipse(cx, cy, rx, ry)
    s.lines(cx, cy, label if isinstance(label, list) else [label], size=13)


def boundary(s, x, y, w, h, title):
    s.rect(x, y, w, h, fill=TINT, stroke=GREEN, sw=1.6)
    s.text(x + 14, y + 20, title, size=14, weight=700, anchor="start", color=GREEN)


def class_box(s, x, y, w, name, attrs, ops, stereo=None, italic=False):
    """UML class: name compartment, attributes, operations. Returns (x, y, w, h)."""
    head = 40 if stereo else 28
    a_h = 10 + 17 * len(attrs) if attrs else 10
    o_h = 10 + 17 * len(ops) if ops else 10
    h = head + a_h + o_h
    s.rect(x, y, w, h)
    s.rect(x, y, w, head, fill=HEAD)
    if stereo:
        s.text(x + w / 2, y + 13, stereo, size=11, color=DIM)
        s.text(x + w / 2, y + 29, name, size=14, weight=700, italic=italic)
    else:
        s.text(x + w / 2, y + 15, name, size=14, weight=700, italic=italic)
    s.path([(x, y + head + a_h), (x + w, y + head + a_h)], sw=1.2)
    for i, a in enumerate(attrs):
        s.text(x + 9, y + head + 13 + 17 * i, a, size=12, anchor="start")
    for i, o in enumerate(ops):
        s.text(x + 9, y + head + a_h + 13 + 17 * i, o, size=12, anchor="start")
    return x, y, w, h


def package(s, x, y, w, h, name, rows):
    s.rect(x, y, 110, 22, fill=HEAD)
    s.rect(x, y + 22, w, h - 22, fill="#FFFFFF")
    s.text(x + 10, y + 11, name, size=13, weight=700, anchor="start")
    for i, r in enumerate(rows):
        s.text(x + 14, y + 46 + 18 * i, r, size=12, anchor="start")


def store(s, x, y, w, h, rows):
    """Datastore drawn as a cylinder."""
    s.add(f'<path d="M{x} {y + 10} L{x} {y + h - 10} A{w / 2} 10 0 0 0 {x + w} {y + h - 10} L{x + w} {y + 10}" '
          f'fill="{TINT}" stroke="{INK}" stroke-width="1.4"/>')
    s.ellipse(x + w / 2, y + 10, w / 2, 10, fill=HEAD)
    s.lines(x + w / 2, y + h / 2 + 6, rows, size=12)


def action(s, cx, cy, rows, w=380, h=50, fill="#FFFFFF", bold=False):
    s.rect(cx - w / 2, cy - h / 2, w, h, rx=16, fill=fill)
    s.lines(cx, cy, rows, size=13, weight=700 if bold else 400)


def decision(s, cx, cy, rows, w=200, h=74):
    s.polygon([(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)])
    s.lines(cx, cy, rows, size=12)


def start_node(s, cx, cy):
    s.circle(cx, cy, 11)


def end_node(s, cx, cy):
    s.circle(cx, cy, 14, fill="#FFFFFF")
    s.circle(cx, cy, 8)


def note(s, x, y, w, h, rows):
    s.polygon([(x, y), (x + w - 14, y), (x + w, y + 14), (x + w, y + h), (x, y + h)], fill=NOTE)
    s.path([(x + w - 14, y), (x + w - 14, y + 14), (x + w, y + 14)], sw=1.1)
    for i, r in enumerate(rows):
        s.text(x + 10, y + 18 + 17 * i, r, size=12, anchor="start")


def label(s, x, y, text, anchor="middle", size=12, color=DIM, italic=False):
    s.text(x, y, text, size=size, anchor=anchor, color=color, italic=italic)


# ------------------------------------------------------------------ diagrams
def use_cases():
    s = SVG(1120, 990)
    boundary(s, 330, 30, 600, 630, "Project 27 demo app (Streamlit)")
    cx = 630
    usecase(s, cx, 100, "Watch a GA or MA run")
    usecase(s, cx, 180, "Play the generations")
    usecase(s, cx, 260, ["Change function, dimension,", "budget and operators"], ry=34)
    usecase(s, cx, 350, "Explore the 12 landscapes")
    usecase(s, cx, 440, "Race the GA against the MA")
    usecase(s, cx, 520, "Read the significance verdict")
    usecase(s, cx, 605, "Browse the saved 30-run results")
    # extend / include
    s.path([(cx, 150), (cx, 130)], dash="6 4", end="open")
    label(s, cx + 12, 140, "«extend»", anchor="start")
    s.path([(cx + 185, 260), (cx + 225, 260), (cx + 225, 100), (cx + 185, 100)], dash="6 4", end="open")
    label(s, cx + 232, 180, "«extend»", anchor="start")
    s.path([(cx, 470), (cx, 490)], dash="6 4", end="open")
    label(s, cx + 12, 480, "«include»", anchor="start")

    boundary(s, 330, 700, 600, 270, "Command-line tools (python -m …)")
    usecase(s, cx, 765, "Run the full experiment (7,950 runs)")
    usecase(s, cx, 845, "Analyse results into tables and figures")
    usecase(s, cx, 925, "Run the 307 automated tests")

    actor(s, 120, 330, "Examiner")
    actor(s, 120, 820, "Team member")
    for y in (100, 350, 440, 605):
        s.path([(150, 312), (cx - 185, y)])
    for y in (765, 845, 925):
        s.path([(150, 800), (cx - 185, y)])
    s.path([(120, 760), (120, 412)], end="tri")
    label(s, 128, 590, "can do everything an", anchor="start")
    label(s, 128, 607, "examiner can, plus the CLI", anchor="start")
    return s


def packages():
    s = SVG(1180, 500)
    store(s, 30, 30, 300, 110, ["experiments/results/ · report/figures/", "raw runs, tables, PNG figures"])
    package(s, 440, 30, 330, 120, "app", ["app.py · navigation and theme", "app_pages/ run, explore, compare, results",
                                             "app_pages/ui.py · shared look and run engine"])
    package(s, 30, 250, 330, 160, "experiments", ["config.py · what to run", "run.py · parallel runner", "analyze.py · tables, statistics, figures",
                                                  "run_one.py · head_to_head.py", "pilot_ma.py · gallery.py"])
    package(s, 440, 250, 330, 205, "evoopt", ["benchmarks.py · 12 functions, f*, x*", "problem.py · the evaluation budget",
                                             "operators.py · selection, crossover, mutation", "ga.py · GeneticAlgorithm",
                                             "local_search.py · Hooke-Jeeves, hill climbing", "ma.py · MemeticAlgorithm",
                                             "baselines.py · random search, SciPy DE", "results.py · RunResult"])
    package(s, 850, 250, 300, 130, "tests", ["9 pytest files, 307 tests:", "library, analysis and", "app smoke tests"])
    # dependencies (dashed, open arrowhead)
    s.path([(605, 150), (605, 250)], dash="7 4", end="open")
    label(s, 613, 200, "imports", anchor="start")
    s.path([(480, 150), (480, 200), (290, 200), (290, 250)], dash="7 4", end="open")
    label(s, 385, 188, "uses the error floor and Wilcoxon test")
    s.path([(360, 345), (440, 345)], dash="7 4", end="open")
    label(s, 400, 333, "imports")
    s.path([(120, 250), (120, 140)], dash="7 4", end="open")
    label(s, 128, 195, "writes", anchor="start")
    s.path([(440, 85), (330, 85)], dash="7 4", end="open")
    label(s, 385, 73, "reads")
    s.path([(850, 330), (770, 330)], dash="7 4", end="open")
    label(s, 810, 318, "tests")
    return s


def classes():
    s = SVG(1420, 1010)
    # row 0: the optimiser interface and the baselines that realise it
    class_box(s, 470, 30, 330, "Optimizer", [], ["run(problem, seed, callback): RunResult"], stereo="«interface»", italic=True)
    class_box(s, 40, 30, 300, "RandomSearch", ["batch_size: int"], ["run(problem, seed): RunResult"])
    class_box(s, 900, 30, 300, "ScipyDE", ["popsize: int"], ["run(problem, seed): RunResult"])
    # row 1
    ga = class_box(s, 470, 230, 330, "GeneticAlgorithm", ["config: GAConfig", "name = \"GA\""],
                   ["run(problem, seed, callback): RunResult", "step(problem, pop, fit, rng)", "make_offspring(problem, pop, fit, rng)",
                    "learn(problem, pop, fit, rng)", "select(fit, n, rng)", "crossover(P1, P2, problem, rng)", "mutate(X, problem, rng)"])
    gac = class_box(s, 40, 230, 300, "GAConfig", ["pop_size: int | None", "selection: str = \"tournament\"", "crossover: str = \"sbx\"",
                                                 "crossover_rate: float = 0.9", "mutation: str = \"polynomial\"", "mutation_rate: float | None",
                                                 "elitism: int = 2"], ["resolved(dim): GAConfig", "validate()"])
    ops = class_box(s, 900, 230, 300, "operators", [], ["tournament_selection(f, n, rng, k)", "roulette_selection(f, n, rng)",
                                                        "rank_selection(f, n, rng, pressure)", "sbx_crossover(P1, P2, rng, lo, hi, eta)",
                                                        "blx_alpha_crossover(...)", "arithmetic_crossover(...)", "polynomial_mutation(X, rng, lo, hi, rate)",
                                                        "gaussian_mutation(...)", "uniform_mutation(...)"], stereo="«module»")
    # row 2
    ma = class_box(s, 470, 620, 330, "MemeticAlgorithm", ["name = \"MA\"", "_steps: dict  (search state per individual)"],
                   ["run(problem, seed, callback): RunResult", "learn(problem, pop, fit, rng)  {override}", "reset_learning()"])
    mac = class_box(s, 40, 620, 300, "MAConfig", ["local_search: str = \"hooke_jeeves\"", "learning: str = \"lamarckian\"", "ls_best: bool = True",
                                                 "ls_best_evals: int = 20·d", "ls_rate: float = 0.05", "ls_child_evals: int = 5·d"], [])
    ls = class_box(s, 900, 620, 300, "local_search", [], ["hooke_jeeves(problem, x, fx, step, max_evals)", "hill_climbing(problem, x, fx, step, max_evals, rng)",
                                                          "converged(step, problem): bool"], stereo="«module»")
    # right column
    prob = class_box(s, 1240, 230, 170, "Problem", ["function", "dim, lower, upper", "max_evals, n_evals", "best_x, best_f, trace"],
                     ["evaluate(X): f", "evaluate_one(x): float", "best_at(evals)", "random_points(n, rng)"])
    bench = class_box(s, 1240, 620, 170, "BenchmarkFunction", ["key, name, category", "domain, dims", "f_opt, x_opt"],
                      ["__call__(X): f", "bounds(d)", "f_star(d), x_star(d)"])
    res = class_box(s, 900, 860, 300, "RunResult", ["best_x, best_f, f_star", "n_evals, max_evals, runtime", "trace, history, stats"],
                    ["error: float", "error_at(evals)", "summary(): dict"])

    # realisation (dashed, hollow triangle)
    s.path([(340, 70), (470, 70)], dash="7 4", end="tri")
    s.path([(900, 70), (800, 70)], dash="7 4", end="tri")
    s.path([(635, 230), (635, 112)], dash="7 4", end="tri")
    # generalisation
    s.path([(635, 620), (635, ga[1] + ga[3])], end="tri")
    s.path([(190, 620), (190, gac[1] + gac[3])], end="tri")
    # composition: GA has a GAConfig
    s.path([(470, 300), (340, 300)], start="diamond")
    label(s, 360, 290, "1", anchor="start")
    # usage dependencies
    s.path([(800, 330), (900, 330)], dash="7 4", end="open")
    label(s, 850, 318, "uses")
    s.path([(800, 700), (900, 700)], dash="7 4", end="open")
    label(s, 850, 688, "uses")
    s.path([(760, 230), (760, 200), (1325, 200), (1325, 230)], dash="7 4", end="open")
    label(s, 1040, 190, "evaluate(X): every FE is counted")
    s.path([(1200, 650), (1222, 650), (1222, 330), (1240, 330)], dash="7 4", end="open")
    label(s, 1216, 560, "evaluate", anchor="end")
    # aggregation: a Problem wraps one BenchmarkFunction
    s.path([(1325, prob[1] + prob[3]), (1325, 620)], start="odiamond")
    label(s, 1333, 600, "1", anchor="start")
    # results
    s.path([(635, ma[1] + ma[3]), (635, 920), (900, 920)], dash="7 4", end="open")
    label(s, 650, 908, "run() returns", anchor="start")
    s.path([(1325, bench[1] + bench[3]), (1325, 900), (1200, 900)], dash="7 4", end="open")
    label(s, 1262, 888, "f* (via Problem)", anchor="middle")
    return s


def ga_activity():
    s = SVG(980, 830)
    cx = 360
    start_node(s, cx, 30)
    action(s, cx, 95, ["Initialise N individuals uniformly in the domain"])
    action(s, cx, 175, ["Evaluate them (FEs += N)"])
    decision(s, cx, 270, ["Budget left?"])
    action(s, cx, 370, ["Select parents: tournament of k = 3"])
    action(s, cx, 450, ["Crossover pairs: SBX, p_c = 0.9"])
    action(s, cx, 530, ["Mutate genes: polynomial, p_m = 1/d"])
    action(s, cx, 610, ["Evaluate the N − 2 children (FEs += N − 2)"])
    action(s, cx, 690, ["Keep the 2 best parents (elitism) + the children"])
    action(s, cx, 770, ["Learn: nothing in the GA", "(the MA refines individuals here)"], h=58, fill=TINT, bold=True)
    s.path([(cx, 41), (cx, 70)], end="arrow")
    for a, b in ((120, 150), (200, 233), (307, 345), (395, 425), (475, 505), (555, 585), (635, 665), (715, 741)):
        s.path([(cx, a), (cx, b)], end="arrow")
    label(s, cx + 10, 326, "yes", anchor="start")
    s.path([(cx - 190, 770), (60, 770), (60, 270), (cx - 100, 270)], end="arrow")
    s.add('<text x="40" y="520" font-family="Arial" font-size="12" fill="#555" transform="rotate(-90 40 520)" text-anchor="middle">next generation</text>')
    s.path([(cx + 100, 270), (690, 270), (690, 340)], end="arrow")
    label(s, cx + 130, 258, "no", anchor="start")
    action(s, 690, 370, ["Return the best solution", "found (RunResult)"], w=240, h=58)
    s.path([(690, 399), (690, 445)], end="arrow")
    end_node(s, 690, 460)
    note(s, 600, 560, 360, 92, ["Every evaluation goes through", "Problem.evaluate: it is counted, and a call past", "the budget of 10,000 · d returns +∞, so the", "point can never be selected."])
    s.path([(600, 606), (cx + 190, 610)], dash="4 3")
    return s


def ma_activity():
    s = SVG(1060, 880)
    cx = 380
    start_node(s, cx, 30)
    label(s, cx + 20, 30, "population after elitist replacement", anchor="start")
    action(s, cx, 90, ["Choose the best individual (always)"])
    action(s, cx, 160, ["Choose each child with probability 0.05"])
    decision(s, cx, 250, ["Another chosen", "individual?"])
    decision(s, cx, 360, ["Already fully", "refined?"])
    action(s, cx, 460, ["Resume its stored step, or start", "from the population's spread"], h=56)
    action(s, cx, 550, ["Run Hooke–Jeeves: 20·d FEs for the best,", "5·d FEs for a child (same budget)"], h=56, fill=TINT, bold=True)
    decision(s, cx, 650, ["Lamarckian?"])
    action(s, 210, 760, ["Write the improved genes and", "fitness back; keep the final step"], w=330, h=56)
    action(s, 560, 760, ["Baldwinian: update the fitness", "only; mark the individual learned"], w=330, h=56)
    action(s, 860, 250, ["Forget the search state of", "individuals that left"], w=300, h=56)
    s.path([(cx, 41), (cx, 65)], end="arrow")
    s.path([(cx, 115), (cx, 135)], end="arrow")
    s.path([(cx, 185), (cx, 213)], end="arrow")
    s.path([(cx, 287), (cx, 323)], end="arrow")
    label(s, cx + 10, 305, "yes", anchor="start")
    s.path([(cx, 397), (cx, 432)], end="arrow")
    label(s, cx + 10, 414, "no", anchor="start")
    s.path([(cx, 488), (cx, 522)], end="arrow")
    s.path([(cx, 578), (cx, 613)], end="arrow")
    s.path([(cx - 100, 650), (210, 650), (210, 732)], end="arrow")
    label(s, 240, 638, "yes")
    s.path([(cx + 100, 650), (560, 650), (560, 732)], end="arrow")
    label(s, 540, 638, "no")
    # loop back to the "another?" decision
    s.path([(210, 788), (210, 840), (40, 840), (40, 250), (cx - 100, 250)], end="arrow")
    s.path([(560, 788), (560, 840), (210, 840)])
    s.path([(cx - 100, 360), (40, 360)])
    label(s, 200, 348, "yes: skip")
    s.path([(cx + 100, 250), (710, 250)], end="arrow")
    label(s, cx + 130, 238, "no", anchor="start")
    s.path([(860, 278), (860, 330)], end="arrow")
    end_node(s, 860, 345)
    label(s, 860, 375, "return population")
    note(s, 620, 470, 410, 110, ["Local-search chain: the final step of every", "refined individual is remembered, so its search",
                                 "resumes where it stopped (Molina et al., 2010)", "instead of starting over with a large step.",
                                 "All local-search FEs use the GA's own budget."])
    s.path([(620, 525), (cx + 190, 460)], dash="4 3")
    return s


def hooke_jeeves_activity():
    s = SVG(900, 720)
    cx = 330
    start_node(s, cx, 30)
    label(s, cx + 20, 30, "start point x, step h (one per variable), budget", anchor="start")
    action(s, cx, 100, ["Exploratory move: for each variable try", "x_i + h_i, then x_i − h_i; keep the first improvement"], w=440, h=56)
    decision(s, cx, 210, ["Improved?"])
    action(s, cx, 320, ["Pattern move: jump to x_new + (x_new − x_base)", "and explore around it"], w=440, h=56)
    decision(s, cx, 430, ["Still", "improving?"])
    action(s, 700, 210, ["Halve every step h_i"], w=220)
    decision(s, 700, 330, ["Budget left and", "h > 1e-10 · width?"], w=230, h=84)
    action(s, 700, 470, ["Return x, f(x) and h"], w=220)
    s.path([(cx, 41), (cx, 72)], end="arrow")
    s.path([(cx, 128), (cx, 173)], end="arrow")
    s.path([(cx, 247), (cx, 292)], end="arrow")
    label(s, cx + 10, 268, "yes", anchor="start")
    s.path([(cx, 348), (cx, 393)], end="arrow")
    s.path([(cx - 100, 430), (60, 430), (60, 320), (cx - 220, 320)], end="arrow")
    label(s, 68, 418, "yes", anchor="start")
    s.path([(cx, 467), (cx, 540), (40, 540), (40, 100), (cx - 220, 100)], end="arrow")
    label(s, cx + 10, 500, "no: explore from", anchor="start")
    label(s, cx + 10, 517, "the new base", anchor="start")
    s.path([(cx + 100, 210), (590, 210)], end="arrow")
    label(s, cx + 125, 198, "no", anchor="start")
    s.path([(700, 235), (700, 288)], end="arrow")
    s.path([(815, 330), (860, 330), (860, 60), (cx, 60), (cx, 72)], end="arrow")
    label(s, 868, 200, "yes", anchor="start")
    s.path([(700, 372), (700, 445)], end="arrow")
    label(s, 710, 408, "no", anchor="start")
    s.path([(700, 495), (700, 545)], end="arrow")
    end_node(s, 700, 560)
    note(s, 80, 600, 560, 92, ["Derivative-free: it only compares f values. Pattern moves", "accelerate along valleys, which is why the MA solves",
                               "Rosenbrock where the GA stalls. Each trial point costs one", "evaluation through Problem.evaluate."])
    return s


def pipeline():
    s = SVG(1300, 250)
    y = 95

    def box(x, w, title, rows):
        s.rect(x, y - 60, w, 120, rx=8)
        s.rect(x, y - 60, w, 30, rx=8, fill=HEAD)
        s.rect(x, y - 38, w, 8, fill=HEAD, stroke=HEAD, sw=0)
        s.path([(x, y - 30), (x + w, y - 30)], sw=1.2)
        s.text(x + w / 2, y - 45, title, size=13, weight=700)
        s.lines(x + w / 2, y + 15, rows, size=12)

    box(20, 210, "experiments/config.py", ["30 problems × 4 algorithms", "× 30 seeds, budget 10,000·d", "+ 8 ablation studies"])
    box(290, 220, "experiments/run.py", ["builds every run, merges", "identical settings,", "16 worker processes"])
    store(s, 570, 40, 190, 110, ["runs.csv", "curves.npy"])
    box(820, 220, "experiments/analyze.py", ["errors < 1e-8 count as 0,", "Wilcoxon rank-sum,", "Holm correction"])
    box(1100, 180, "Outputs", ["tables (Markdown, CSV)", "figures (PNG)", "app: Saved results page"])
    for a, b in ((230, 290), (510, 570), (760, 820), (1040, 1100)):
        s.path([(a, y), (b, y)], end="arrow")
    label(s, 260, y - 12, "jobs")
    label(s, 540, y - 12, "writes")
    label(s, 790, y - 12, "reads")
    label(s, 1070, y - 12, "writes")
    label(s, 650, 222, "7,950 runs (6,900 distinct) · seeds 0–29 · every FE counted by Problem.evaluate", size=13, color=INK)
    return s


DIAGRAMS = {
    "use_cases": use_cases,
    "packages": packages,
    "classes": classes,
    "ga_activity": ga_activity,
    "ma_learn_activity": ma_activity,
    "hooke_jeeves_activity": hooke_jeeves_activity,
    "experiment_pipeline": pipeline,
}


# ---------------------------------------------------------------- rendering
async def _render(paths, port):
    import websockets

    for svg_path in paths:
        size = json.loads(svg_path.with_suffix(".json").read_text())
        req = urllib.request.Request(f"http://127.0.0.1:{port}/json/new?about:blank", method="PUT")
        target = json.loads(urllib.request.urlopen(req).read())
        async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100 * 1024 * 1024) as ws:
            n = 0

            async def cdp(method, params=None):
                nonlocal n
                n += 1
                await ws.send(json.dumps({"id": n, "method": method, "params": params or {}}))
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get("id") == n:
                        return msg.get("result", {})

            await cdp("Emulation.setDeviceMetricsOverride", {"width": size["w"], "height": size["h"], "deviceScaleFactor": 2, "mobile": False})
            await cdp("Page.enable")
            await cdp("Page.navigate", {"url": svg_path.resolve().as_uri()})
            await asyncio.sleep(1.2)
            shot = await cdp("Page.captureScreenshot", {"format": "png"})
            svg_path.with_suffix(".png").write_bytes(base64.b64decode(shot["data"]))
        urllib.request.urlopen(f"http://127.0.0.1:{port}/json/close/{target['id']}")
        svg_path.with_suffix(".json").unlink()


def render_png(paths, port=9344):
    profile = Path.home() / "AppData" / "Local" / "Temp" / "project27-diagram-chrome"
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                             f"--remote-debugging-port={port}", f"--user-data-dir={profile}", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1)
                break
            except Exception:
                time.sleep(0.2)
        asyncio.run(_render(paths, port))
    finally:
        proc.terminate()


def main():
    written = []
    for name, draw in DIAGRAMS.items():
        s = draw()
        path = OUT / f"{name}.svg"
        path.write_text(s.svg(), encoding="utf-8")
        path.with_suffix(".json").write_text(json.dumps({"w": s.w, "h": s.h}))
        written.append(path)
        print(f"wrote {path.name} ({s.w}x{s.h})")
    if Path(CHROME).exists():
        render_png(written)
        print("rendered PNGs at 2x")
    else:
        print("Chrome not found: SVGs only")


if __name__ == "__main__":
    main()

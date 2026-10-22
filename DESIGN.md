---
name: Project 27
description: A specimen cabinet for watching Genetic and Memetic Algorithms search 12 benchmark landscapes.
colors:
  cabinet-green: "#1E4D3F"
  cabinet-green-deep: "#173E33"
  cabinet-rule: "#3F6E5F"
  rail-text: "#E7EFE9"
  rail-caption: "#BFD2C6"
  label-paper: "#F4F7F3"
  tray-ground: "#EEF2EC"
  tray-shade: "#E2E9E3"
  paper: "#FFFFFF"
  ink: "#15201B"
  ink-dim: "#4A5A52"
  hairline: "#C8D2CB"
  grid-rule: "#E4EAE5"
  elite-yellow: "#E3B323"
  ga-cobalt: "#2E5BD8"
  ma-vermilion: "#D9412B"
  de-ochre: "#B7861A"
  rs-slate: "#7A8580"
  verdict-ok-ink: "#22603A"
  verdict-ok-wash: "#E3F1E8"
  verdict-ok-edge: "#B9DCC6"
  verdict-no-ink: "#8E2A1A"
  verdict-no-wash: "#F8E5E1"
  verdict-no-edge: "#EBC0B7"
typography:
  headline:
    fontFamily: "Archivo, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 650
    letterSpacing: "-0.015em"
  title:
    fontFamily: "Archivo, sans-serif"
    fontSize: "1.35rem"
    fontWeight: 620
  verdict:
    fontFamily: "Archivo, sans-serif"
    fontSize: "1.2rem"
    fontWeight: 600
    lineHeight: 1.35
  label-heading:
    fontFamily: "Archivo, sans-serif"
    fontSize: "1.05rem"
    fontWeight: 600
  body:
    fontFamily: "Archivo, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
  data:
    fontFamily: "Archivo, sans-serif"
    fontSize: "0.86rem"
    fontWeight: 400
  label:
    fontFamily: "Archivo, sans-serif"
    fontSize: "0.78rem"
    fontWeight: 600
  numeral:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: "0.94em"
    fontWeight: 400
    fontFeature: "tnum"
  chart-tick:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: "11px"
    fontWeight: 400
rounded:
  tray: "3px"
  base: "4px"
  bar: "3px"
  chip: "999px"
  pin: "50%"
spacing:
  tray-gap: "6px"
  cell-y: "7px"
  cell-x: "12px"
  label-x: "16px"
  page-y: "3rem"
components:
  button-run:
    backgroundColor: "{colors.label-paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.base}"
  button-run-hover:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
  button-play:
    backgroundColor: "{colors.cabinet-green}"
    textColor: "{colors.paper}"
    typography: "{typography.body}"
  accession-label:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.base}"
    padding: "14px 16px 10px"
  unit-tray:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.tray}"
    padding: "6px 6px 8px"
  table-wrap:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.base}"
  table-cell:
    typography: "{typography.data}"
    padding: "7px 12px"
  table-head:
    textColor: "{colors.ink-dim}"
    typography: "{typography.label}"
    padding: "9px 12px"
  chip-ok:
    backgroundColor: "{colors.verdict-ok-wash}"
    textColor: "{colors.verdict-ok-ink}"
    rounded: "{rounded.chip}"
    padding: "0 8px"
  chip-no:
    backgroundColor: "{colors.verdict-no-wash}"
    textColor: "{colors.verdict-no-ink}"
    rounded: "{rounded.chip}"
    padding: "0 8px"
  chip-tie:
    backgroundColor: "{colors.tray-ground}"
    textColor: "{colors.ink-dim}"
    rounded: "{rounded.chip}"
    padding: "0 8px"
  pin:
    rounded: "{rounded.pin}"
    size: "12px"
  rate-bar:
    backgroundColor: "{colors.grid-rule}"
    rounded: "{rounded.bar}"
    width: "56px"
    height: "6px"
  chart-panel:
    backgroundColor: "{colors.paper}"
    rounded: "{rounded.base}"
  nav-rail:
    backgroundColor: "{colors.cabinet-green}"
    textColor: "{colors.rail-text}"
  empty-state:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-dim}"
    rounded: "{rounded.base}"
    padding: "22px 24px"
---

# Design System: Project 27

## Overview

**Creative North Star: "The Specimen Cabinet"**

Every candidate solution is a specimen: pinned on the landscape where it was found, labelled with its value, filed by generation. The app is a natural-history cabinet. A cabinet-green rail holds navigation and the run controls; the main field is a cool tray ground on which white unit trays sit, each edged by a single hairline. Algorithms are told apart by the colour of their pin heads, and the one best specimen carries a yellow pin and a typed accession label.

The density is that of a well-kept collection drawer: compact, ruled, legible at arm's length on a laptop. Depth comes from paper on ground and from rules, never from shadows. Words are set in one grotesque (Archivo); every number is set in a tabular monospace (JetBrains Mono), so a reader always knows which marks are measurements. The world rejects the category default it was built against: a white Streamlit page of sliders over stock Plotly charts.

**Key Characteristics:**
- Cabinet-green rail, cool tray ground, white trays with 1px hairlines, no shadows.
- Pin heads as the series key: GA cobalt, MA vermilion, DE ochre, RS slate.
- Yellow belongs to the best specimen and nothing else.
- Archivo for words, JetBrains Mono (tabular) for every number.
- Ink rules (1.5px) under headings of labels and tables; pale grid rules between rows.

## Colors

A green-and-paper cabinet with a four-pin series key and a single reserved yellow.

### Primary
- **Cabinet Green** (cabinet-green): the navigation rail's ground, the Streamlit primary and link colour, the Play/Pause buttons, the active colour of the generation slider, and the low end of the landscape tint.
- **Cabinet Green Deep** (cabinet-green-deep): secondary surfaces inside the rail (input fields, code blocks).
- **Cabinet Rule** (cabinet-rule): borders inside the rail.
- **Rail Text** (rail-text) and **Rail Caption** (rail-caption): words on the rail; captions and the brand's subline take the quieter caption tone.
- **Label Paper** (label-paper): the rail's primary accent. The Run button is a slip of label paper on green; it turns pure paper on hover. Also the high end of the landscape tint.

### Secondary
- **Elite Yellow** (elite-yellow): the best specimen's pin on the landscape, the pin in the accession label's heading, the border of the "best" tag on the chart. Text selection uses it at 40% alpha.

### Tertiary (series pin heads)
- **GA Cobalt** (ga-cobalt), **MA Vermilion** (ma-vermilion), **DE Ochre** (de-ochre), **RS Slate** (rs-slate): one colour per algorithm, used for pins, chart lines, rate bars and the wash of solved trays. Never used for anything but the algorithm it names.

### Neutral
- **Tray Ground** (tray-ground): the page background and the header strip; also the slider rail and the tie chip's fill.
- **Tray Shade** (tray-shade): Streamlit's secondary background on the main field.
- **Paper** (paper): every unit tray, label, table and chart panel, including Plotly's paper and plot background.
- **Ink** (ink): text, heading rules, chart hover-label ground, the best marker's outline, the optimum star's outline.
- **Ink Dim** (ink-dim): secondary text, ledes, table headers, tick labels, the success threshold line.
- **Hairline** (hairline): the 1px edge of every tray, label, table and chart panel; axis lines and ticks.
- **Grid Rule** (grid-rule): row rules inside labels and tables, chart gridlines, the empty track of a rate bar.
- **Verdict washes**: ok (verdict-ok-ink / -wash / -edge) and no (verdict-no-ink / -wash / -edge) colour the solved/better and not-solved/worse chips.

### Named Rules
**The One Yellow Rule.** Elite Yellow marks the best specimen only. Sliders, primary buttons, series and warnings never take it; the only ambient use is the 40% text-selection tint.

**The Pin-Head Key Rule.** A series colour always means the same algorithm on every page, chart, bar, tray and pin. A new algorithm gets a new pin colour; it never borrows one.

**The Paper-on-Ground Rule.** Content lives on white paper over the tray ground; the ground itself carries only titles, ledes and captions.

## Typography

**Display Font:** none; the system has no display tier.
**Body Font:** Archivo (variable 100–900, self-hosted, with sans-serif fallback)
**Label/Mono Font:** JetBrains Mono (variable 100–800, self-hosted, with monospace fallback)

**Character:** A sober grotesque for every word paired with a typewriter-like tabular mono for every figure, like a typed accession number on a handwritten-neat label.

### Hierarchy
- **Headline** (650, 1.75rem, -0.015em): the page title, which names the problem being shown ("Rastrigin, 2-D").
- **Title** (620, 1.35rem): section headings such as "Every seed".
- **Verdict** (600, 1.2rem, 1.35, max 60ch): the one-sentence statistical verdict on the comparison page.
- **Label heading** (600, 1.05rem): the accession label's heading ("Best specimen").
- **Body** (400, 1rem): ledes (Ink Dim, max 72ch) and prose.
- **Data** (400, 0.86rem): label rows, table cells, the fairness line.
- **Label** (600, 0.78rem): table column heads in Ink Dim; tray seed names and chips run 0.72–0.74rem.
- **Numeral** (JetBrains Mono, tabular, 0.94em of its context): every number in prose, labels, tables and trays.
- **Chart tick** (JetBrains Mono, 11px, Ink Dim): axis ticks, hover labels (12px on Ink), the generation readout, the success annotation (10px).

### Named Rules
**The Typed Number Rule.** Every number is set in JetBrains Mono with tabular figures, wrapped so it can be told from the words around it. Words, including units like "evaluations" and "s", stay in Archivo; the only mono words are chart readouts and identifiers.

## Layout

A fixed cabinet-green sidebar rail on the left holds page navigation, then the page's controls (function, dimension, algorithm, seed, a collapsed "Budget and operators" group), then the full-width Run button, then the brand. The main field is Streamlit's wide layout with 3rem top and bottom padding and a 2.6rem tray-coloured header.

Each page opens with the headline and a lede, then one plot owns the field. On the run page the field splits 3:2: the landscape on the left, the accession label on the right, with a full-width convergence strip below. Explore splits 1:1 and 2:3; comparison stacks chart, drawer, table. Columns use Streamlit's medium gap.

The drawer of unit trays is a grid: a 76px algorithm column, then trays auto-filling at a 74px minimum with 6px gaps, so seeds wrap on narrow screens. Tables scroll horizontally inside their paper wrap rather than squeezing. On mobile Streamlit collapses the rail into its drawer and columns stack.

## Elevation & Depth

The system is flat. No element carries a drop shadow. Depth is conveyed by tone (white paper on the cool tray ground, deep green inside green) and by rules: 1px hairlines around every panel, a 1.5px ink rule under every label and table heading, pale grid rules between rows. The only box-shadows in the build are the pin's inset paper ring and outer 1px colour ring, which draw the pin head itself, not elevation.

### Named Rules
**The Hairline Rule.** Every container is separated by a 1px Hairline edge and a 4px corner, never by a shadow. Plotly panels get the same frame as HTML trays.

## Shapes

Corners are square-ish: 4px on labels, tables, chart panels, inputs and buttons; 3px on the small unit trays and rate bars. Pins are perfect circles (12px, 10px inside a tray), solid when the run solved, hollow (paper with a 1.5px colour ring) when it did not. Chips are full pills. The optimum is a paper star outlined in ink; the best specimen is a larger yellow dot outlined in ink. The empty state is the one dashed edge in the system.

## Components

### Buttons
- **Shape:** gently squared (4px).
- **Run (rail primary):** a Label Paper slip with Ink text at weight 650 on cabinet green, full rail width, Material icon at left; hover turns it pure Paper.
- **Play / Pause:** Cabinet Green Plotly buttons with white Archivo 13px labels, on their own row beneath a full-width generation slider.
- **Segmented controls** (algorithm, ablation study) use Streamlit's segmented control under the theme.

### Chips
- **Style:** pill (999px), 1px border, 0 8px padding, Archivo 0.74rem.
- **State:** ok (solved, better) in green wash; no (not solved, worse) in red wash; tie in tray ground with hairline. Chips state outcomes plainly; ties and losses are shown with the same weight as wins.

### Cards / Containers
- **Corner Style:** 4px (trays 3px).
- **Background:** Paper on Tray Ground.
- **Shadow Strategy:** none (see Elevation & Depth).
- **Border:** 1px Hairline.
- **Internal Padding:** labels 14px 16px 10px; trays 6px 6px 8px.

### Inputs / Fields
- **Style:** Streamlit widgets under the theme: visible widget borders, 4px radius; inside the rail they sit on Cabinet Green Deep with Rail Text.
- **Focus:** Streamlit's default focus treatment in the primary colour (Label Paper in the rail, Cabinet Green on the field).

### Navigation
- Streamlit page navigation at the top of the rail, Material icons beside each title; the active page sits on a lighter green band in bold. The brand ("Project 27" and its subline in Rail Caption) closes the rail.

### Accession Label (signature)
The best specimen's typed label. A Paper panel with a heading row: a yellow pin and "Best specimen" on the left, a mono accession number (algorithm·seed·generation, e.g. MA·s1·g275) in Ink Dim on the right, an ink rule beneath. A one-line meta note, then a two-column definition list (term in Ink Dim, value in Ink) ruled with Grid Rule lines. All readouts live as rows of this label; outcome chips sit inline beside the error value.

### Drawer of Unit Trays (signature)
One row per algorithm, one small tray per seed: seed name, final error in mono, and a pin at top right. A solved tray is washed with its series colour (8% fill, 42% border) and carries a solid pin; an unsolved one stays paper with a hollow pin. A legend line beneath explains the encoding.

### In-World Table (signature)
An HTML table inside a Paper wrap with a Hairline edge. Column heads in Label type over a 1.5px ink rule; rows ruled in Grid Rule; numeric columns right-aligned in mono. Algorithm cells carry their pin; rates show a 56px series-coloured bar before the mono percentage.

### Chart Panel (signature)
Plotly figures on Paper, framed by the Hairline edge and 4px corner. Grid in Grid Rule, axis lines and outside ticks in Hairline, tick labels in mono, horizontal legend top-left, ink hover labels with white mono text. Landscapes are tinted by the rank of f from deep cabinet green (low) to label paper (high). Convergence plots are log-scaled with a dashed Ink Dim success line at 1e-4; the best line is 2.4px, the population mean 1px at 45% opacity.

## Do's and Don'ts

### Do:
- **Do** put every number in JetBrains Mono with tabular figures, including inline numbers inside sentences.
- **Do** frame every chart and content block in Paper with a 1px Hairline and 4px corner.
- **Do** colour each algorithm by its pin head (GA cobalt, MA vermilion, DE ochre, RS slate) everywhere it appears.
- **Do** keep run controls in the cabinet-green rail with a single Label Paper primary button.
- **Do** fold summary figures into rows of the accession label or an in-world table.
- **Do** show ties, losses and unsolved runs with the same visual weight as wins (tie chip, no chip, hollow pin).

### Don't:
- **Don't** use Elite Yellow for anything other than the best specimen.
- **Don't** add drop shadows; depth is paper on ground and hairlines.
- **Don't** set numbers in Archivo, or running prose in JetBrains Mono; mono words are limited to chart readouts and identifiers (the generation readout, the accession number, the success annotation).
- **Don't** fall back to stock Plotly or Streamlit chart theming; every chart goes through the shared layout.
- **Don't** pull out summary figures as a row of big hero-metric tiles.

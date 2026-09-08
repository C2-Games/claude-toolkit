---
name: latex-style
description: Enforces a consistent LaTeX report style — both the custom report.cls template (A4/0.8in-margin/twoside/12pt geometry, newtxtext/newtxmath fonts, singlespacing, an FRBC-named RGB color palette applied to section numerals/captions/divider pages/title bar, full-page Roman-numeral section dividers, fancyhdr alternating title/subtitle headers, APA biblatex, raggedright bold-label table/figure captions) and how to write the body content itself — comment-banner conventions, the \input{}-a-generated-fragment table pattern, the figure/landscape/Notes-minipage pattern, and the \appendixpage/A.1-numbering appendix pattern. Use whenever writing, editing, or reviewing any .tex/.cls file for a report-style document, including new sections, tables, figures, appendices, or title-page/header edits — apply by default without waiting for the user to mention style.
---

# LaTeX report style guide

Every rule below applies to any report-style `.tex`/`.cls` file you write or
edit. Match these exactly — do not substitute generic LaTeX template
conventions. When editing an existing document that already has a
`report.cls`, keep new content consistent with what's already there rather
than reintroducing default LaTeX styling.

The canonical, ready-to-copy class file is `examples/report-cls.md` — when
scaffolding a brand-new document, copy that file wholesale as `report.cls`
rather than re-deriving it piece by piece.

## 1. Document class and page geometry

Documents are built on a **custom `report.cls`** (not the standard LaTeX
`report` class) that loads `article` underneath:

```latex
\LoadClass[12pt, twoside]{article}
\usepackage{geometry, enumitem, indentfirst, graphicx, comment}
\geometry{a4paper, margin=0.8in}
\raggedbottom
```

- **A4 paper**, not letter. **0.8in margins** on all sides. **Twoside,
  12pt.**
- `\raggedbottom` avoids stretching content vertically to fill the page —
  pages end wherever the content ends.
- `indentfirst` so the first paragraph after a heading indents like every
  other paragraph (LaTeX's default un-indents it).

## 2. Fonts and spacing

```latex
\usepackage{newtxtext, newtxmath, setspace}
\singlespace
```

`newtxtext`/`newtxmath` gives a Times-like serif text font with a matching
math font, and compiles under plain pdfLaTeX — don't reach for `fontspec`
or a `mainfont` declaration, which require XeLaTeX/LuaLaTeX and would break
this pipeline. Body text is single-spaced.

## 3. Color palette

Define the full palette up front with `xcolor`'s `RGB` option, before any
package that might reference a color name:

```latex
\usepackage[RGB]{xcolor}
\definecolor{FRBCBlue1}{RGB}{11, 77, 118}
\definecolor{FRBCBlue2}{RGB}{16, 60, 98}
\definecolor{FRBCBrown}{RGB}{147, 121, 92}
\definecolor{FRBCGreen}{RGB}{75, 118, 97}
\definecolor{FRBCOrange}{RGB}{196, 122, 55}
\definecolor{FRBCYellow}{RGB}{211, 201, 119}
\definecolor{FRBCGrey1}{RGB}{128, 128, 128}
\definecolor{FRBCGrey2}{RGB}{65, 75, 86}
```

Keep these exact names and RGB triples — they're shared across projects, so
renaming or re-deriving them per-document breaks that consistency. `FRBCBlue1`
is the primary accent, used for section numerals and caption labels (see
§6, §8). `FRBCBrown` is the title-page accent (§7). The rest of the palette
(`FRBCBlue2`, `FRBCGreen`, `FRBCOrange`, `FRBCYellow`, `FRBCGrey1`,
`FRBCGrey2`) is available for ad hoc use — e.g. a chart color, a highlight
box — but nothing in the base template currently draws on them.

Hyperlinks and citations use blue-black tints, kept separate from the FRBC
palette since they're a link-affordance convention, not a brand color:

```latex
\usepackage[linktocpage=false, linktoc=all]{hyperref}
\hypersetup{
    colorlinks,
    linkcolor={blue!20!black},
    citecolor={blue!50!black},
    filecolor=magenta,
    urlcolor=black
}
\usepackage[capitalise, noabbrev]{cleveref}
```

## 4. Bibliography

APA-style `biblatex`, American language mapping, citations capped at 2
authors shown:

```latex
\usepackage[style=apa, language=american, maxnames=2, minnames=1, sortcites=true]{biblatex}
\DeclareLanguageMapping{american}{american-apa}
\addbibresource{ref.bib}
```

Cite in body text with `\parencite{key}`. At the end of the document:

```latex
\nocite{*}
\printbibliography
```

`\nocite{*}` forces every entry in `ref.bib` to print even if it was never
cited in the body — keep this unless the document specifically wants an
uncited-entries-excluded bibliography.

## 5. Header and footer

```latex
\usepackage{fancyhdr}
\setlength{\headheight}{18.5pt}
\pagestyle{fancy}
\fancypagestyle{main}{
    \fancyhf{}
    \fancyhead[R]{Updated: \today}
    \fancyhead[LE]{\mytitle}
    \fancyhead[LO]{\mysubtitle}
    \fancyfoot[R]{\thepage}
}
\renewcommand{\headrulewidth}{0pt}
```

This defines a named pagestyle `main` — invoke it with `\pagestyle{main}`
in the body of the document, not the bare `fancy` style. The header
alternates by page side (twoside document): even pages show the title
(`LE`), odd pages show the subtitle (`LO`) — a classic book-style
alternation. No rule line under the header (`\headrulewidth{0pt}`). Footer
just shows the page number, right-aligned.

The title page itself uses `\pagestyle{empty}` (no header/footer at all),
and body numbering conventionally starts at page 3 (title = 1, TOC = 2,
both gobbled):

```latex
\pagenumbering{gobble}
\mytitlepage
\tableofcontents
\newpage

\pagestyle{main}
\pagenumbering{arabic}
\setcounter{page}{3}
```

## 6. Section headings

```latex
\usepackage[indentafter]{titlesec}
\setcounter{secnumdepth}{3}
\titleformat{\section}
    {\normalfont\Large\bfseries}
    {\textcolor{FRBCBlue1}{\Roman{section}.}}{0.5em}{}
\titleformat{\subsection}
    {\normalfont\Large\bfseries}
    {\textcolor{FRBCBlue1}{\arabic{subsection}.}}{0.5em}{}
\titleformat{\subsubsection}
    {\normalfont\normalsize}
    {\Alph{subsubsection}.}{0.5em}{}
```

- `\section` numbers in **Roman numerals** (I., II., III...), `\subsection`
  in **Arabic** (1., 2., 3...), `\subsubsection` in **capital letters**
  (A., B., C...). Section and subsection are deliberately the same size and
  weight (`\Large\bfseries`) — the numbering style, not text size, is what
  distinguishes them. Don't "fix" this into a conventional size hierarchy;
  it's intentional given the full-page divider convention below.
- Only the **numeral** is colored `FRBCBlue1` — put the `\textcolor{}` call
  inside the label argument only, never wrapping the title text itself.
  Title text stays the default text color so long headings stay readable
  and don't compete visually with body-text links (which are also
  blue-tinted, see §3).

## 7. Full-page section dividers

Each top-level section opens on its own dedicated page rather than an
inline heading — use `\fullpagesection{...}` in place of `\section{...}`:

```latex
\usepackage{calc}
\newcommand{\fullpagesection}[1]{%
    \clearpage
    \refstepcounter{section}
    \addcontentsline{toc}{section}{\protect\numberline{\Roman{section}}#1}
    \thispagestyle{empty}

    \vspace*{\fill}

    \begin{center}
        \begin{minipage}{\textwidth}
            {\fontsize{35}{60}\selectfont\bfseries \textcolor{FRBCBlue1}{Section \Roman{section}:}}

            \vspace*{1em}

            {\fontsize{28}{30}\selectfont #1}
        \end{minipage}
    \end{center}

    \vspace*{\fill}
    \clearpage
}
```

The "Section N:" label (35pt/60pt leading) is colored `FRBCBlue1`; the
section title itself (28pt/30pt leading) stays black — same numeral-only
coloring principle as §6. Content is vertically centered on an otherwise
blank page (`\vspace*{\fill}` above and below), with no header/footer on
the divider page itself (`\thispagestyle{empty}`), and the section is
manually added to the TOC with a Roman-numeral `\numberline`.

Use `\subsection{...}` as normal within a section — subsections don't get
their own divider page, only top-level sections do.

## 8. Table of contents

```latex
\usepackage{tocloft}
\renewcommand{\numberline}[1]{#1.\hspace*{0.5em}}
```

This globally redefines `\numberline` to append a period and a small space
after any section number — keeping TOC entries, list-of-figures, etc.
consistent with the "I." / "1." period-suffixed style used in the headings
themselves. Call `\tableofcontents` plainly; `hyperref`'s
`linktocpage=false, linktoc=all` (§3) makes entries clickable without
turning the page number itself into a link.

## 9. Title page

```latex
\usepackage{tikz}
\newcommand{\mytitlepage}{
    \pagestyle{empty}
    \begin{titlepage}
        \begin{tikzpicture}[remember picture, overlay]
            \fill[color=FRBCBrown] ([yshift=-0.7cm]current page.north west) rectangle ([yshift=-1.2cm]current page.north east);
        \end{tikzpicture}

        \vspace*{0.1cm}

        \huge{\bfseries \mytitle}

        \Large{\mysubtitle}

        \vspace{0.5cm}

        \large{\textcolor{black!40}{Author Name}}

        \vfill

        \normalsize{
            \textbf{Created:} \created

            \textbf{Updated:} \today \hfill \textbf{Prepared by:} \names
        }
    \end{titlepage}
}

\newcommand{\mytitle}{}
\newcommand{\mysubtitle}{}
\newcommand{\created}{}
\newcommand{\names}{}
```

- Branding is a plain **tikz-drawn horizontal bar** near the top of the
  page, filled `FRBCBrown` — no logo image file. It spans the full page
  width as a thin band roughly 0.5cm tall.
- Title is `\huge\bfseries`; subtitle `\Large`, not bold; author names
  `\large`, de-emphasized to `black!40` (light gray) — this grey is a
  neutral text-dimming convention, not part of the FRBC accent palette.
- Metadata footer line uses `\hfill` to right-align "Prepared by:" against
  the left-aligned "Updated:".
- `\mytitle`, `\mysubtitle`, `\created`, `\names` are declared empty in the
  class and `\renewcommand`'d in the calling `.tex` file — follow this
  placeholder-command pattern for any other per-document metadata you need,
  rather than hardcoding values into the class file. The author-name lines
  themselves, however, are written directly into `\mytitlepage` in the
  class file (see `examples/report-cls.md`) — edit `report.cls` itself to
  change authors, don't try to parameterize them from the `.tex` file.

## 10. Tables and figures

```latex
\usepackage{pdflscape, tabularx, booktabs, caption, array, multirow, colortbl, longtable}
\newcolumntype{L}{>{\raggedright\arraybackslash}X}
\newcolumntype{R}{>{\raggedleft\arraybackslash}X}
\newcolumntype{C}{>{\centering\arraybackslash}X}
\renewcommand{\arraystretch}{1.1}
\def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}
\captionsetup[table]{
    singlelinecheck=false,
    justification=raggedright,
    labelfont={bf, normalsize, color=FRBCBlue1},
    font={normalsize}
}
\captionsetup[figure]{
    singlelinecheck=false,
    justification=raggedright,
    labelfont={bf, normalsize, color=FRBCBlue1},
    font={normalsize}
}
```

- Use `booktabs` rules (`\toprule`/`\midrule`/`\bottomrule`), never `\hline`,
  in any table body.
- Wrap wide tables in `pdflscape`'s `landscape` environment rather than
  shrinking them to fit portrait.
- `L`/`R`/`C` are custom `tabularx` column types for ragged-right,
  ragged-left, and centered variable-width columns.
- `\arraystretch{1.1}` gives slightly more row padding than the LaTeX
  default (1.0) — don't override this per-table.
- `\sym{}` reproduces Stata `esttab`/`estout`'s significance-star macro
  (works in and out of math mode) — needed if a table is `\input{}`'d
  directly from Stata-generated `.tex` output.
- **Captions go above the content** — `\caption{}` precedes
  `\input{...}`/`\includegraphics{...}`, not after. This is a deliberate
  deviation from the more common caption-below-table convention.
- The bold caption **label** (`Table 1`, `Figure 1`) is colored
  `FRBCBlue1`; the caption **body text** stays the default color. Captions
  are always ragged-right and never centered, even when they'd fit on one
  line (`singlelinecheck=false`).
- For notes below a table, use a manual `\begin{flushleft}\footnotesize
  \textit{Notes:} ...\end{flushleft}` block rather than a formal
  `threeparttable`/`tnote` mechanism.

## 11. Lists

```latex
\setlist[itemize]{nosep, leftmargin=*, before=\vspace{-0.8em}, after=\vspace{-1em}}
```

This tightens `itemize` blocks specifically (not `enumerate`) — no extra
inter-item spacing, flexible left margin, and negative vertical space
before/after the list to cancel out whitespace LaTeX would otherwise add
around it. Leave `enumerate` at its defaults unless a specific document
calls for the same treatment.

## 12. Writing body content

The rules above govern the document *class*. These govern how you write
the section `.tex` files that get `\input{}`'d into the body — comment
structure, and the standard table/figure/appendix patterns.

### 12.1 Comment banners

Mark major thematic blocks with a full-width `%===` banner and a short
label, and lighter-weight divisions within a section with `%---`:

```latex
%===============================================================================
% QLS6: WAGE CHANGE SCENARIOS
%===============================================================================

\begin{landscape}
    \subsection{Wage Change Questions (QLS6)}

    % --- Expected & Desired Weekly Hours ---
    \subsubsection{Expected \& Desired Weekly Hours}
    ...
\end{landscape}

%-------------------------------------------------------------------------------

% --- Expected Employment Status ---
\subsubsection{Expected Employment Status}
```

Use the heavy `%===` banner to separate distinct topics that would each
warrant their own subsection or set of subsections — it's a visual anchor
when scanning a long section file, not a LaTeX-visible element. Use the
lighter `%---` rule and inline `% --- Label ---` comments to mark smaller
subdivisions (a subsubsection, a repeated sub-pattern) without the same
visual weight. This is a pure authoring convention — it has no effect on
the compiled output — but keep it consistent so long section files stay
navigable.

### 12.2 Tables

The default table pattern `\input{}`s a tabular fragment generated by an
external pipeline (e.g. Stata's `esttab`/`estout`) rather than typing the
`tabular`/`tabularx` body by hand:

```latex
\begin{table}[H]
    \centering
    \caption{Demographic Characteristics I}

    \input{../../output/tables/demos-1.tex}

    \vspace*{-1em}

    \begin{flushleft}
        \footnotesize \textit{Notes:} This table presents demographic
        characteristics of survey respondents. ...
    \end{flushleft}
\end{table}
```

`\caption{}` comes first (per §10, captions sit above content), then the
`\input{}` of the generated fragment, then `\vspace*{-1em}` to pull the
Notes block up and cancel the whitespace LaTeX adds after the table body,
then the Notes block directly inside `\begin{flushleft}` — no minipage
wrapper (contrast with figures, §12.3). Point `\input{}` at wherever the
data pipeline writes its output (commonly a sibling `output/tables/`
directory).

This is the default, not a hard requirement: when there's no external
pipeline generating the fragment, write the `tabularx`/`booktabs` body
directly in the `.tex` file as described in §10 — e.g. a one-off summary
table like a sample-cleaning log. Whichever way the table body is
produced, the `\caption{}` → content → `\vspace*{-1em}` → Notes-in-`flushleft`
shape stays the same.

### 12.3 Figures

Figures follow a parallel but distinct shape — the Notes block is wrapped
in a `0.9\linewidth` minipage, which tables don't do:

```latex
\begin{figure}[p]
    \centering
    \caption{Respondent Age \& Gender Distribution}

    \includegraphics[scale=0.68]{../../output/figures/demos_population.pdf}

    \vspace{0.5em}

    \begin{minipage}{0.9\linewidth}
        \begin{flushleft}
            \footnotesize \textit{Notes:} This figure presents a population
            pyramid displaying the age and gender distribution of survey
            respondents. ...
        \end{flushleft}
    \end{minipage}
\end{figure}
```

Use the `[p]` placement specifier (a dedicated float page) rather than
`[H]`/`[htbp]` for figures — they're typically full-width plots that don't
share a page with body text. The `0.9\linewidth` minipage keeps the Notes
text from spanning the figure's full width, which reads better for a wide
plot; tables don't need this because the table content itself already
constrains the width.

Wrap any table or figure too wide for the portrait text block in
`\begin{landscape}...\end{landscape}` (from `pdflscape`, already loaded
per §10) rather than shrinking it to fit:

```latex
\begin{landscape}
    \begin{figure}[p]
        ...
    \end{figure}
\end{landscape}
```

### 12.4 Appendix

Open an appendix with `\appendixpage` — a divider page in the same style
as `\fullpagesection` (§7), but unnumbered (just "Appendix", no Roman
numeral or TOC number), and immediately renumber subsections as `A.1`,
`A.2`, ... :

```latex
\appendixpage

\renewcommand{\thesubsection}{A.\arabic{subsection}}

\subsection{Sample Cleaning}
```

Add `\appendixpage` to `report.cls` alongside `\fullpagesection` — it's
not part of the base template in `examples/report-cls.md` yet, so define
it when a document needs an appendix:

```latex
\newcommand{\appendixpage}{%
    \clearpage
    \refstepcounter{section}
    \addcontentsline{toc}{section}{\protect Appendix}
    \thispagestyle{empty}

    \vspace*{\fill}

    \begin{center}
        \begin{minipage}{\textwidth}
            {\fontsize{35}{60}\selectfont\bfseries \textcolor{FRBCBlue1}{Appendix}}
        \end{minipage}
    \end{center}

    \vspace*{\fill}
    \clearpage
}
```

It still calls `\refstepcounter{section}` so cross-references and
numbering stay in sync, but adds a plain `Appendix` TOC entry instead of a
`\numberline`'d one, and prints just the word "Appendix" on the divider
page rather than "Section N: Title".

## Reference

See `examples/report-cls.md` for the complete, internally consistent
`report.cls` file with every rule above integrated — copy it directly
when starting a new report-style document.

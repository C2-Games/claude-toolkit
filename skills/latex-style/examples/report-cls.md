# Canonical `report.cls`

Copy this file wholesale as `report.cls` when scaffolding a new report-style
LaTeX document. It's a complete, self-consistent custom document class —
every color is defined before its first use, and every macro referenced in
the main `.tex` file (`\mytitlepage`, `\fullpagesection`, `\appendixpage`,
`\mytitle`, `\mysubtitle`, `\created`, `\names`, `\sym`) is defined here.

A minimal calling document looks like:

```latex
\documentclass{report}

\renewcommand{\mytitle}{My Report Title}
\renewcommand{\mysubtitle}{A Subtitle}
\renewcommand{\names}{Author Name}
\renewcommand{\created}{January 1, 2026}

\begin{document}
\pagenumbering{gobble}
\mytitlepage
\tableofcontents
\newpage

\pagestyle{main}
\pagenumbering{arabic}
\setcounter{page}{3}

\fullpagesection{First Section}
\label{sec:first}

Body text here.

\subsection{A Subsection}

More body text.

\appendixpage
\renewcommand{\thesubsection}{A.\arabic{subsection}}
\subsection{An Appendix Subsection}

Appendix body text.

\newpage
\nocite{*}
\printbibliography
\end{document}
```

## Full `report.cls`

```latex
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{report}[2026/01/01 General Report Class]


% Document class options
\LoadClass[12pt, twoside]{article}
\usepackage{geometry, enumitem, indentfirst, graphicx, comment}
\geometry{a4paper, margin=0.8in}
\raggedbottom


% Math packages
\usepackage{amssymb, amsmath, amsthm}


% Custom colors — define every palette color up front, before anything
% below references it.
\usepackage[RGB]{xcolor}
\definecolor{FRBCBlue1}{RGB}{11, 77, 118}
\definecolor{FRBCBlue2}{RGB}{16, 60, 98}
\definecolor{FRBCBrown}{RGB}{147, 121, 92}
\definecolor{FRBCGreen}{RGB}{75, 118, 97}
\definecolor{FRBCOrange}{RGB}{196, 122, 55}
\definecolor{FRBCYellow}{RGB}{211, 201, 119}
\definecolor{FRBCGrey1}{RGB}{128, 128, 128}
\definecolor{FRBCGrey2}{RGB}{65, 75, 86}


% References, links, and bibliography
\usepackage{varioref}
\usepackage[linktocpage=false, linktoc=all]{hyperref}
\hypersetup{
    colorlinks,
    linkcolor={blue!20!black},
    citecolor={blue!50!black},
    filecolor=magenta,
    urlcolor=black
}

\usepackage[capitalise, noabbrev]{cleveref}
\usepackage[style=apa, language=american, maxnames=2, minnames=1, sortcites=true]{biblatex}
\DeclareLanguageMapping{american}{american-apa}
\addbibresource{ref.bib}


% Header & footer formatting
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


% Font formatting
\usepackage{newtxtext, newtxmath, setspace}
\singlespace


% Section formatting — numerals are colored FRBCBlue1, title text stays
% the default text color.
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


% TOC formatting
\usepackage{tocloft}
\renewcommand{\numberline}[1]{#1.\hspace*{0.5em}}


% Title page
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

        \large{\textcolor{black!40}{Damjan Pfajar}}

        \large{\textcolor{black!40}{Edith Liu}}

        \large{\textcolor{black!40}{Calvin McElvain}}

        \vfill

        \normalsize{
            \textbf{Created:} \created

            \textbf{Updated:} \today \hfill \textbf{Prepared by:} \names
        }
    \end{titlepage}
}


% Preamble placeholder commands — override per-document via \renewcommand
\newcommand{\mytitle}{}
\newcommand{\mysubtitle}{}
\newcommand{\created}{}
\newcommand{\names}{}


% Table & figure formatting
\usepackage{pdflscape, tabularx, booktabs, caption, array, multirow, colortbl, longtable}
\newcolumntype{L}{>{\raggedright\arraybackslash}X}
\newcolumntype{R}{>{\raggedleft\arraybackslash}X}
\newcolumntype{C}{>{\centering\arraybackslash}X}
\setlist[itemize]{nosep, leftmargin=*, before=\vspace{-0.8em}, after=\vspace{-1em}}
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

## Notes on the author list

The three names in `\mytitlepage` (`Damjan Pfajar`, `Edith Liu`, `Calvin
McElvain`) are hardcoded in the class file itself, not parameterized like
`\mytitle`/`\mysubtitle`/`\created`/`\names`. Edit `report.cls` directly to
change the author list for a new project — don't try to override it from
the calling `.tex` file.

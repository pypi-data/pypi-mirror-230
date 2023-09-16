# html_mappings.py

HTML_CONVERSION_MAPPINGS = {
    'h1': {'markdown': '#', 'latex': '\\section'},
    'h2': {'markdown': '##', 'latex': '\\subsection'},
    'h3': {'markdown': '###', 'latex': '\\subsubsection'},
    'p': {'markdown': '', 'latex': '\\par '},
    'br': {'markdown': '  \n', 'latex': '\\newline '},
    'strong': {'markdown': '**', 'latex': '\\textbf{'},
    'em': {'markdown': '*', 'latex': '\\emph{'},
    'pre': {'markdown': '```', 'latex': '\\texttt{'},
    'code': {'markdown': '`', 'latex': '\\texttt{'},
    'a': {'markdown': '[', 'latex': '\\href{'},
    'img': {'markdown': '![image](', 'latex': '\\includegraphics{'},
    'ul': {'markdown': '- ', 'latex': '\\begin{itemize}\n\\item '},
    'ol': {'markdown': '1. ', 'latex': '\\begin{enumerate}\n\\item '},
    'li': {'markdown': '', 'latex': '\\item '},
    'quote': {'markdown': '> ', 'latex': '\\begin{quote}\n'},
    'blockquote': {'markdown': '> ', 'latex': '\\begin{quote}\n'},
    'hr': {'markdown': '---', 'latex': '\\rule{\\linewidth}{0.4pt}'},
    'table': {'markdown': '', 'latex': '\\begin{tabular}'},
    'tr': {'markdown': '', 'latex': ''},
    'th': {'markdown': '| ', 'latex': ' & '},
    'td': {'markdown': '| ', 'latex': ' & '},
}

LATEX_ENVIRONMENTS = {
    'ul': {'latex': '\\end{itemize}'},
    'ol': {'latex': '\\end{enumerate}'},
    'quote': {'latex': '\\end{quote}'},
    'blockquote': {'latex': '\\end{quote}'},
    'table': {'latex': '\\end{tabular}'},
}

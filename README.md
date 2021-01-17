# pytexnumber.py

Renumbers LaTeX equations. The program reads from the standard input and writes to the standard output.

### usage:

    pytexnumber.py [-h] [--ignore-comments] [--no-ignore-comments]
                   [--log LOG] [pattern] [replacement]

### positional arguments:

    pattern               input pattern, e.g., "eqn"
    replacement           replacement pattern, e.g., "Eqn"

### optional arguments:

    -h, --help            show this help message and exit
    --ignore-comments     ignore comments, true by default
    --no-ignore-comments  do not ignore comments, false by default
    --log LOG             log file

### Description

Replaces all labels from the input stream (in this case redirected from `in.tex`) that match a given input pattern, such
as `\label{pattern*}`
and all corresponding references (`\ref`, `\eqref`, `\pageref`) with renumbered ones `replacement+idx`, where `idx`
counts the matching `\label{pattern*}` order of appearance, i.e., equals 1 for the first `\label` that matches the input
pattern, 2 for the second etc. The output is written to the standard output (in this case redirected to `out.tex`).
Optionally, writes the replacement pattern sequence to `log_file`. Warnings and errors are output to the standard error
stream.

### Example

Consider a LaTeX file `in.tex` having three labels, named, in order of appearance, `\label{eqn5}`
, `\label{eqn_important}`and lastly `\label{entropy}`. Then the command

    python3 pytexnumber.py <in.tex >out.tex eqn Eqn 

will replace `\label{eqn5}` by `\label{Eqn1}` (and also all references to `eqn5`
will automatically become references to `Eqn1`) and replace
`\label{eqn_important}` by `\label{Eqn2}` (again together with the corresponding references). The `\label{entropy}`
remains unchanged since it does not match the input pattern `\label{eqn*}`. The changes are saved to the file `out.tex`,
and the replacement pattern sequence is written to the file `log.txt`.

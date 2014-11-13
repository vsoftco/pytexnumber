 - Usage: 

        python3 py3texnumber.py in.tex out.tex pattern replacement 
    for the Python 3 version.

        python py2texnumber.py in.tex out.tex pattern replacement 
    for the Python 2 version.

- Description: replaces all labels in in.tex that match 
a given input pattern, such as \label{pattern...} 
and all corresponding references (\ref, \eqref, \pageref) 
with renumbered ones replacement+idx, where idx counts 
the matching \label{pattern...} order of appearance, 
i.e. equals 1 for the first \label that matches the input pattern, 
2 for the second etc. The in.tex is left unchanged and the 
modifications are written to out.tex.

- Example: consider a latex file source.tex having three labels, named, 
in order of appearance, \label{eqn5}, \label{eqn_important} 
and lastly \label{entropy}. Then the command 

        python3 py3texnumber.py in.tex out.tex eqn Eqn 

will replace \label{eqn5} by \label{Eqn1} (and also all references 
to eqn5 will automatically become references to Eqn1) and replace 
\label{eqn_important} by \label{Eqn2} (again together with 
the corresponding references). The \label{entropy} remains unchanged 
since it does not match the input pattern \label{eqn...}. 
The changes are saved to the file out.tex.

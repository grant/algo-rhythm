This file contains code and datafiles for getting a training set from Music XML.

The file "readxml.py" is the main code file.  If the function "createStateMatrices()" is called, then a hash map will be returned, the keys will be
the xml filenames of the pieces, the values will be python ordered pairs, where the first element is and integer, and the second is a state matrix.
The integer indicates the start location of the measure for the state matrix.  For example, if start location = 0, then the first measure starts
at the first time point, if start location = 3, then the first 3 time points are before the first measure, which starts on the fourth time point.

The file catalog.txt controls which xml files are read, and supports directives for specifying the measure start, adjusting the tempo, and transposing
parts.

If run as main, "readxml.py" will create midi files for all state matrices, and put them in the directory "midi."  This can be used to check that the
music was properly read and has a reasonable tempo.


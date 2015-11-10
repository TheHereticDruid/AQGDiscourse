# AQGDiscourse

A python implementation of Automatically creating questions from a given passage. <br/><br/>
Question generated is of the following types: <br/>
1. Contradictory <br/>
2. Concluding <br/>
3. Illustrative <br/>
4. Reasoning <br/>
5. Time related <br/>
6. True/False <br/>
7. Gap-fill <br/>
8. Programming <br/>
9. Equations <br/>
10. Paragraph level <br/><br/> 
Discourse Markers are used to cluster the sentences to form questions.
	
# Installation

1. nltk

 * Download NLTK v3 from:

	    	https://github.com/nltk/nltk 

 * Install NLTK:

	    	sudo python setup.py install

2. Stanford parser

 * Get the latest version from:

	    	http://nlp.stanford.edu/software/lex-parser.shtml#Download

 * Extract the standford-parser-full-20xx-xx-xx.zip. <br/>

 * Create a new folder. Place the extracted files into this jar folder: stanford-parser-3.x.x-models.jar and stanford-parser.jar.
(For example(in my case): Create a folder 'jars' in /home/anirudh and paste tanford-parser-3.x.x-models.jar and stanford-parser.jar. in    /home/anirudh/jars)
<br/>

 * Open the stanford-parser-3.x.x-models.jar using an Archive manager (7zip).

 * Browse inside the jar file; edu/stanford/nlp/models/lexparser. Again, extract the file called 'englishPCFG.ser.gz'. Remember the location where you extract this ser.gz file.
(For me, it is: /home/anirudh/englishPCFG.ser.gz)

3. To run the code:

 * Add the passage in input.txt file.

 * Setup the initial settings in the config.txt file.

 * Start the stanford-corenlp server by running corenlp.py.

 * Run the AQG code using:

	        python v10.py


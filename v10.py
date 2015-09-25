''' 
Automatic Question Generation 

'''

'''

Instructions:

- Packages needed:
	1. en : get linguistics package from https://www.nodebox.net/code/index.php/Linguistics#verb_conjugation
		and paste it in python path.
	2. stanford parser: Steps for its installation and links will be provided in a separate text file.
	3. stanford corenlp: Follow the steps from https://github.com/dasmith/stanford-corenlp-python
		Start the server using python corenlp.py before running this code.
	4. Some nltk packages from nltk.download()
- Usage: python v2.py
'''
############################################ Imports #############################################################################

import nltk
import nltk.data
from nltk.tree import Tree
import os
import stanford
from nltk.stem.snowball import SnowballStemmer
import re
import json
from jsonrpc import ServerProxy, JsonRpc20, TransportTcpIp
import ast
import en
from nltk.corpus import brown
import math
import random
import copy
from decision import *
from features import *
from nltk.corpus import wordnet as wn
import inflect

#################################################################################################################################


#Setting stanford environment variables

os.environ['STANFORD_PARSER'] = '/home/druidicheretic/jars'
os.environ['STANFORD_MODELS'] = '/home/druidicheretic/jars'


############################################# Class initializations ############################################################

stemmer = SnowballStemmer("english")
parser = stanford.StanfordParser(model_path="/home/druidicheretic/notJars/englishPCFG.ser.gz")

class StanfordNLP:
    def __init__(self):
        self.server = ServerProxy(JsonRpc20(),
                                  TransportTcpIp(addr=("127.0.0.1", 8080)))
    
    def parse(self, text):
        return json.loads(self.server.parse(text))

obj=Features()
# brown_tagged_sents = brown.tagged_sents(categories='news')
# brown_sents = brown.sents(categories='news')
# unigram_tagger = nltk.UnigramTagger(brown_tagged_sents)
################################################################################################################################



############################################ Global Initializations #############################################################


#List of auxiliary verbs
aux_list= ['am', 'are', 'is', 'was', 'were', 'can', 'could', 'does', 'do', 'did', 'has', 'had', 'may', 'might', 'must', 'need',
 'ought', 'shall', 'should', 'will', 'would', "aren't", "isn't", "wasn't", "weren't", "can't", "couldn't", "doesn't", "don't",
 "didn't", "hasn't", "hadn't", "mightn't", "wouldn't", "won't", "shan't", "shouldn't", "mustn't", "needn't", "am not", "may not"] #Add some stuff to aux list


aux_negate= {"am": "am not", "are": "aren't", "is": "isn't", "was": "wasn't", "were": "weren't", "can": "can't", 'could': "couldn't",
 'does': "doesn't", 'do': "don't", "did": "didn't", 'has': "hasn't", 'had': "hadn't", 'may': "may not", 'might': "mightn't",
 'must': "mustn't", 'need': "needn't", 'shall': "shan't", 'should': "shouldn't", 'will': "won't", 'would': "wouldn't", "am not": "am",
 "aren't": "are", "isn't": "is", "wasn't": "was", "weren't": "were", "can't": "can", "couldn't": 'could', "doesn't": 'does', "don't": 'do',
 "didn't": "did", "hasn't": 'has', "hadn't": 'had', "may not": 'may', "mightn't": 'might', "mustn't": 'must', "needn't": 'need', "shan't": 'shall',
 "shouldn't": 'should', "won't": 'will', "wouldn't": 'would'}

#List to hold all input sentences
sentences= []

#Clusters
contradictory_sentences= []
additive_sentences= []
concluding_sentences= []
emphasis_sentences= []
illustrate_sentences= []
why_sentences= []
when_sentences= []
discuss_sentences= []
gapfill_Sentences= []
tfSentences= []
equation_sentences= []
program_sentences= []
others= []

prev= []
prev2= []

qterms= []

#Basically, a list of list
sentences_map= {0: contradictory_sentences, 1: additive_sentences, 2: concluding_sentences, 3: emphasis_sentences,
 4: illustrate_sentences, 5: why_sentences, 6: when_sentences, 7: discuss_sentences, 8: tfSentences, 9: gapfill_Sentences, 
 11: equation_sentences, 12: program_sentences}

#Maps sentence numbers to each selected split sentence.
sentnumb_map= {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7:[], 8: [], 9: [], 11: [], 12: []}

#Stores the resultant questions
all_questions= []

conjunction= ['and', 'or']

thres=0.5
nounphrase= 0

comm= ["/*", "//"]

sentence_gapfill= {}

allnouns= []
rem= []

prevInChain= 0.0
braceCount= 0.0

infEng=inflect.engine()

##################################################################################################################################


################################################# coreference ####################################################################
# Function used to parse the text to get a dictionary of values
##################################################################################################################################

def coreference():

	global sentences
	global result

	text= ' '.join(sentences)

	nlp = StanfordNLP()
	result = nlp.parse(text)


# Function To Draw The Decision Tree For Programming Languages, Tag All Lines As Natural Or Not, And Make A List Of Non-Naturals
def decisionTree():

	fp= open("decision.pickle", "r")	#Set To Language Specific File
	tree= ast.literal_eval(fp.read().strip())
	fp.close()
	fp=open("args.pickle","r")
	start=fp.read().strip().split("\n")
	dt= Decision(tree= tree, start=[float(i) for i in start])	#Also Set Start Here
	b= []
	for i in rem:
		#All Features
		t1= obj.ratioK(sentences[i])
		t2= obj.operators(sentences[i])
		t3= obj.comments(sentences[i])
		t4= obj.braces(sentences[i])
		t5= obj.indent(sentences[i])
		t6= obj.semicolon(sentences[i])
		t7= obj.programChain()
		t8= obj.capital(sentences[i])
		t9= obj.ratioC(sentences[i])

		b.append(t4)
		tmp= [t1, t2, t3, t4, t5, t6, t7, t8, t9]
		tmp= dt.refineR([tmp], [0, 8])
		if(dt.score(tmp)):	#Tag The tmp Sentence, 1 For Non-Naturals
			program_sentences.append(i)

	chain(b)
			
#Function To Group Non Naturals Into Programs
def chain(braces):

	tmp= []
	j= 0
	# Chain Them Together, Contiguous Set Of Sentences
	for i in range(len(program_sentences)-1):
		if(program_sentences[i+1]- program_sentences[i]> 1):
			tmp.append([j, i])
			j= i+1

	l= len(program_sentences)
	if(j!= l and l-j > 1):
		tmp.append([j, i+1])

	#If A Later Block Starts With An Indented Line, Attach To The Previous Block
	i= 1
	while(i < len(tmp)):
		print resSentences[tmp[i][0]]
		if(obj.indent(resSentences[tmp[i][0]])):
			iV=tmp[i-1][1]
			jV=tmp[i][0]
			delLst=[]
			for itr in range(len(all_questions)):
				if all_questions[itr][3]>iV and all_questions[itr][3]<jV:
					delLst.append(itr)
			tmp[i-1][1]=tmp[i][1]
			del tmp[i]
			delLst.sort()
			delLst.reverse()
			for itr in delLst:
				del all_questions[itr]
		else:
			i+=1

	#If An Earlier Block Ends Without Closing All Braces, Attach To Next Block
	i= 0
	while(i < len(tmp)-1):
		if(braces[tmp[i][1]]==1.0):
			iV=tmp[i][1]
			jV=tmp[i+1][0]
			delLst=[]
			for itr in range(len(all_questions)):
				if all_questions[itr][3]>iV and all_questions[itr][3]<jV:
					delLst.append(itr)
			tmp[i][1]=tmp[i+1][1]
			del tmp[i+1]
			delLst.sort()
			delLst.reverse()
			for itr in delLst:
				del all_questions[itr]
		else:
			i+=1


	tmp= [[program_sentences[i] for i in j] for j in tmp]

	c, tmp= extractQuestionSentences(tmp)
	genProgramQuestions(c, tmp)

def remComments(lst):
	commentBlock=""
	commentSingle=["//"]	#set
	commentMultiple=[["/*","*/"],["/**","*/"]]	#set
	commentDict={"//":0,"/*":1,"/**":1}
	newLst=[]
	for s in lst:
		if commentBlock!="":
			for ele in commentMultiple:
				if ele[0]==commentBlock:
					sIndex=-1
					sVal=0
					if ele[1] in s:
						commentBlock=""
						sIndex=s.index(ele[1])
						sVal=len(ele[1])
						s=s[sIndex+sVal:]
					else:
						s=""
		else:
			cIndex=9999
			cValue=-1
			for k,v in commentDict.items():
				if k in s and cIndex>s.index(k):
					cIndex=s.index(k)
					cValue=v
			if cValue==0:
				if cIndex!=0:
					s=s[:cIndex-1]
				else:
					s=""
			elif cValue==1:
				for ele in commentMultiple:
					if ele[0] in s:
						eIndex=-1
						eLen=0
						if ele[1] not in s:
							commentBlock=ele[0]
						else:
							eIndex=s.index(ele[1])
							eLen=len(ele[1])
					if eIndex>0:
						if cIndex!=0:
							s=s[:cIndex-1]+s[eIndex+eLen:]
						else:
							s=s[eIndex+eLen:]
					else:
						if cIndex!=0:
							s=s[:cIndex-1]
						else:
							s=""
		newLst.append(s)
	return newLst
#Function To Generate Program Questions
def genProgramQuestions(c, lst):

	flag= 0
	keywords= ["WAP", "Write a program", "program to", "program that"]
	q= []
	for i in c:
		tmp= []
		tmp2= []
		for j in i:
			tmp.append(sentences[j])	#Retrieve Sentences, Including Code
			tmp2.append(j)
		tmp.append("What does the above program do? If any, what is the output?")	#First Possible Type Of Question
			
		tmp=remComments(tmp)
		tmp= [j for j in tmp if j!= ""]
		if(len(tmp) > 1):
			sentnumb_map[12].append(tmp2)
			tmpLst=quoteBreak(tmp)
			tmpStr=""
			for it in range(len(tmp)):
				tmpStr+=tmp[it]
				if it in tmpLst:
					tmpStr+=" "
				else:
					tmpStr+="\n"
			all_questions.append([tmpStr, 12, 4, tmp2[0], -1])

	for i in c:
		flag= 0
		for k in keywords:
			res= re.search(k, sentences[i[0]-1], re.I)
			res2= re.search(k, sentences[i[0]-2], re.I)
			if(res):
				flag= 1
				if(res.group()== "WAP" or res.group()== "Write a program"):	#If WAP Exists In The Question Statement
					sentnumb_map[12].append([i[0]-1])
					all_questions.append([sentences[i[0]-1], 12, 5, i[0]-1, -1])
				else:
					index= sentences[i[0]-1].index("program")	#Search For Program Keyword, And Append WAP To The Following Statement Part
					sentnumb_map[12].append([i[0]-1])
					all_questions.append(["Write a "+ sentences[i[0]-1][index:], 12, 4, i[0]-1, -1])
				break
			
			elif(res2 and flag== 0):
				flag= 1
				if(res2.group()== "WAP" or res2.group()== "Write a program"):	#If WAP Exists In The Question Statement
					sentnumb_map[12].append([i[0]-2])
					all_questions.append([sentences[i[0]-1], 12, 5, i[0]-2, -1])
				else:
					index= sentences[i[0]-1].index("program")	#Search For Program Keyword, And Append WAP To The Following Statement Part
					sentnumb_map[12].append([i[0]-2])
					all_questions.append(["Write a "+ sentences[i[0]-2][index:], 12, 4, i[0]-2, -1])
				break

	
#Function To Get The Question Defining Statement(Basis) Of The Question, Per Programming Block
#Gets Either From The First Comment Line, Or The Line Previous, Along With The Whole Program, For Each Block
def extractQuestionSentences(lst):

	c= []
	#First Check For Comments
	for k in range(len(lst)):
		flag= 0
		tmp= []
		i= lst[k][0]
		while i<= lst[k][1]:
			flag2= 0
			if(flag== 0):
				for j in comm:
					res= re.search(j, sentences[i])
					if(res):
						if(res.group()== "/*"):
							tmp.append(i)
							flag= 1
						else:
							tmp.append(i)
						flag2= 1
						break
			else:
				tmp.append(i)
				if(res.search(r"*/", sentences[i])):
					flag= 0
			if(flag2== 0):
				break
			i+= 1

		#If No Comments, Take The Previous Line As Well
		if(len(c)== 0 and k > 0):
			tmp.append(lst[k][0]-1)

		c.append(tmp)

	return c, lst
		

def calcFreq():

	global termOcc
	global termRel
	global termFreq
	global resSentences
	#global unigram_tagger

	termRel= {}
	termOcc= {}
	termFreq= {}
	words= []

	resSentences= sentences
	if "coref" in result:
		for i in result['coref']:
			for j in i:
				if(j[0][3] > j[1][3] and j[0][1]!= j[1][1]):
					resSentences[j[0][1]]= resSentences[j[0][1]].replace(j[0][0], j[1][0])


	for i in resSentences:
		for j in i.split():
			tmp=j.lower()
			#tags= unigram_tagger.tag([tmp])
			tags= nltk.pos_tag(nltk.word_tokenize(tmp))
			if(re.search("NN.*", tags[0][1])):
				if(termFreq.get(tmp, 'empty')== 'empty'):
					termFreq[tmp]= 0
				termFreq[tmp]+=1	#Number Of Times The Word Appears In The Document


	for i in resSentences:
		tmpWords=[]
		tags= nltk.pos_tag(nltk.word_tokenize(i))

		# allwords= [word for word, tag in tags]
		# for k in range(len(allwords)):
		# 	if(allwords.count(allwords[i])> 1):


		for word, tag in tags:

			if(re.search("NN.*", tag)):

				tmp= word.lower()
				tmpWords.append(tmp) 

		tmpWords=list(set(tmpWords))
		for it in tmpWords:
			if(termOcc.get(it, 'empty')== 'empty'):
				termOcc[it]= 0
			termOcc[it]+= 1		#Number Of Sentences The Word Appears In The Document

		words+=tmpWords
		words=list(set(words))

		tmpWords=list(set(tmpWords))
		for w1 in tmpWords:
			for w2 in tmpWords:
				if(w1!= w2):

					if(termRel.get(w1, 'empty')== 'empty'):
						termRel[w1]= {}

					if(termRel[w1].get(w2, 'empty')== 'empty'):
						termRel[w1][w2]= 0

					termRel[w1][w2]+= 1	#Number Of Sentences Two Words Appear Together In

#Length Of Sentence
def length(s):

	return len(s.split())
#Number Of NN Terms In Sentence
def nnouns(s):

	c= 0
	tags= nltk.pos_tag(nltk.word_tokenize(s))

	for word, tag in tags:
		if(re.search("NN.*", tag)):
			c+= 1

	return c

#Function To Make Gap-Fill Type Of Questions
def genGapFill():

	global gapfill_Sentences

	for i in rem:
		f1= 0 
		f2= 0
		tmpSent=remBrackets(resSentences[i])
		nn= nnouns(tmpSent)
		l= length(tmpSent)

		if(l > 10 and l < 35):
			f1= 1

		if(nn>= 3):
			f2= nn

		score= f1* f2	#Score Based On If It Has Atleast 3 NN Terms, And If Of Medium Length

		if(score != 0):

			tags= nltk.pos_tag(nltk.word_tokenize(tmpSent))

			flag= 0
			for w, t in tags:
				if(re.search("PR.*", t) or re.search("this", w, re.I) or re.search("these", w, re.I) or re.search("that", w, re.I) or re.search("them", w, re.I)):
					flag= 1	#Check If It Still Has Pronouns
					break

			if(flag== 0):
				gapfill_Sentences.append(tmpSent)

				sentnumb_map[9].append([i])

	count= len(termFreq)/2
	newFreq= []

	for k, v in termFreq.items():
		if(count== 0):
			newFreq.append(k)	#Get High Frequency Terms
		else:
			count-= 1

	# for s in gapfill_Sentences:

	# 	np= simplify(s)

	# 	flag2= 0
	# 	for w in np.split():
	# 		if(w in newFreq):
	# 			flag2= 1

	# 	if(1):
	# 		s= s.replace(np, "_________________")
	# 		print s

	global prev
	global prev2

	v= 0
	lst= []
	for s in gapfill_Sentences:

		simplify(s)
		tmp= prev
		if(tmp== []):
			continue
		tmp= tmp[1:]
		tmp.reverse()
		tmp= [' '.join(i.leaves()) for i in tmp]	#NN Terms
		prev2= [i[0] for i in prev2]
		prev2= list(set(prev2))
		if(prev2!= []):
			tmp= prev2

		flag3= 0
		replacement= []

		for i in prev2:
			if(i not in newFreq):
				newFreq.append(i)

		for i in tmp:
			for j in i.split():
				if(j in newFreq):
					replacement.append(i)	#NN Term To Be Taken Out
		replacement= list(set(replacement))
		replacement= [i for i in replacement if len(i)>4]
		if replacement:
			replacement= random.choice(replacement)
			
			t= s.replace(replacement, "_____________")	#NN Term Is Replaced By Blank
			sentence_gapfill[replacement]= v
			all_questions.append([t+"\nFill In The Blanks.", 9, 1, sentnumb_map[9][v][0], replacement])
			lst.append(sentnumb_map[9][v])
		
			v+= 1

	sentnumb_map[9]= copy.deepcopy(lst)


#Function To Title And Group Sentences.
def titling():

	prev= ""
	context= {}
	newContext= {}

	if "coref" in result:
		for i in result['coref']:
			for j in i:

				val= j[1][0][0].upper()+ j[1][0][1:]
				if(context.get(val, 'empty')== 'empty'):
					context[val]= [j[1][1]]	#List Each NP With Its Coreferences, From The Common coref Data 
				context[val].append(j[0][1])

	i= -1
	print context
	for k, v in context.items():
		i+= 1
		tags= nltk.pos_tag(nltk.word_tokenize(k))
		flag= 0
		for word, tag in tags:
			if(not re.search("NN.*", tag)):
				flag= 1
				break

		if(flag== 0):
			newContext[k]= v
		
	
	if(not newContext):

		#If there are no pronouns being resolved, this dictionary will be empty.
		#So, we assume that then, the first sentence will contain the context.

		tags= nltk.pos_tag(nltk.word_tokenize(sentences[0]))
		for word, tag in tags:
			if(re.search("NN.*", tag)):
				newContext[word]= range(len(sentences))
				break

	#Print
	print "------------------Titling-----------------------\n"
	for k, v in newContext.items():
		newContext[k]= sorted(list(set(v)))
		print "Title: ", k
		print "Sentences: "
		for val in newContext[k]:
			print sentences[val]
		print "\n"
		
#Get Sentences Which Haven't Been Made Into Questions Yet
def othersNumb():

	global rem
	sentnumbers= [i for i in range(len(resSentences))]

	othersnum= []
	for k, v in sentnumb_map.items():
		for val in v:
			for s in val:
				othersnum.append(s)

	rem= list(set(sentnumbers)- set(othersnum))
	rem= list(set(rem)- set(program_sentences))
	rem.sort()
	genTrueFalse(rem)

#All NN's In The Text
def getAllNouns():

	global allnouns

	for i in resSentences:

		tags= nltk.pos_tag(nltk.word_tokenize(i))
		for word, tag in tags:
			if(re.search("NN.*", tag)):
				allnouns.append(word)

	allnouns= list(set(allnouns))

#Two Other Types Of True/False Questions
def negate(s, n, j, e, rn=-1):
	if(rn>=0):
		rand2=rn
	else:
		rand2= random.randint(0, 2)

	if(rand2== 0):

		aux= ""
		for i in aux_list:
			if(i in s.split()):
				aux= i
				break

		if(aux!= ""):
			temp= s.replace(aux, aux_negate[aux])	#Negate Auxiliary Verb
			temp+= " True/False?"
			all_questions.append([temp+j, 8, 1+e, n+e, "False"])

		else:
			all_questions.append([s+"True/False?"+j, 8, 1+e, n+e, "False"])

	elif(rand2==1):
		tags= nltk.pos_tag(nltk.word_tokenize(s))
		words= []
		accTags=[]
		for word, tag in tags:
			if(re.search("JJ.?|NNS?", tag)):
				words.append(word)	#Find JJs In Sentence
				accTags.append(tag)
		if(words==[]):
			negate(s, n, j, e, rn=0)
		else:
			flg=0
			for it in range(len(words)):
				if accTags[it].index("JJ")==0:
					sets=[jt for jt in wn.sysnets(words[it]) if jt.split(".")[1]=="a"]
				else:
					sets=[jt for jt in wn.sysnets(words[it]) if jt.split(".")[1]=="n"]
				if sets:
					for kt in sets:
						ant=kt.lemmas()[0].antonyms()
						if ant:
							ant=ant[0].name()
							if accTags[it]=="NNS":
								ant=infEng.plural_noun(ant)
							s.replace(it,ant)
							flg=1
							break
				if flg:
					break
		if flg:
			s+= " True/False?"
			all_questions.append([s+j, 8, 1+e, n+e, "False"])
		else:
			negate(s, n, j, e, rn=0)
	else:

		tags= nltk.pos_tag(nltk.word_tokenize(s))

		words= []
		for word, tag in tags:
			if(re.search("NN.*", tag)):
				words.append(word)	#Find NNs In Sentence
		remNouns=list(set(allnouns)-set(words))
		if remNouns!=[]:
			rand= random.randint(0, len(remNouns)-1)
			an= remNouns[rand]
			tmp= s.replace(words[-1], an)	#Replace A NN With One Not In The Sentence, Randomly Chosen
			tmp+= " True/False?"
			all_questions.append([tmp+j, 8, 1+e, n+e, "False"])
		else:
			negate(s, n, j, e, rn=0)


#Function To Generate True False Questions
def genTrueFalse(num):

	global all_questions
	global tfSentences

	getAllNouns()

	j= 0
	f= 0
	for i in num:
		pre= genPreSentence(resSentences[i])	#Get Main Clause Of Sentence
 		if(pre != ""):

			tags= nltk.pos_tag(nltk.word_tokenize(resSentences[i]))
			alltags= [tag for word, tag in tags]

			flag= 0
			flag2= 0
			for k in alltags:
				if(re.search("PR.*", k)):
					flag= 1
					break

			tags= nltk.pos_tag(nltk.word_tokenize(resSentences[i]))[:nounphrase]
			for word, tag in tags:
				if(re.search("NN.*", tag)):
					flag2= 1
					break
			just=""
			eM=0
			if(flag==0 and flag2==1 and len(resSentences[i].split())< 30 and len(resSentences[i].split())> 5):	#If No Sentences, And Atleast One More NN, And Of Reasonable Length
				if i+1 in [it[0] for it in sentnumb_map[5]] and i+1 in [it[3] for it in all_questions if it[1]==5]:
					just=" Justify Your Answer In A Sentence."
					eM=1
				rand= random.randint(0, 1)
				tfSentences.append(remBrackets(resSentences[i]))
				sentnumb_map[8].append([i])
				rand=0
				if(rand== 0):
					negate(tfSentences[-1], i, just, eM, rn=1)
				else:
					all_questions.append([tfSentences[-1]+ " True/False?"+just, 8, 1+eM, i+eM, "True"])	#Direct True False
					j+= 1

	

def qSet():
	finalQList=[]
	totalMarks=50	#Say
	curMarks=0
	carryOver=0
	addedList=[]
	remExtras()
	add_context()
	order={7: 10, 10: 10, 12: 10, 0: 10, 4: 10, 6: 10, 11: 10, 8: 10, 5: 10, 9:10}	 #Set To List Of Numbers Representing Question Types, In Order Of Highest Mark Prob To Lowest, With Type As Key, And Percentage In Decimal As Value
	for o, p in order.items():
		totalPMarks=int(totalMarks*p+carryOver)	#Total Marks For Current Part
		if totalPMarks+curMarks>totalMarks:
			totalPMarks=totalMarks-curMarks
		curPMarks=0
		curQList=[]
		cur_questions=[q for q in all_questions if q[1]==o and q[2]<=totalPMarks]	#All Questions Of The Type In Consideration
		while curPMarks<totalPMarks and cur_questions!=[]:
			rnd=random.randint(0, len(cur_questions)-1)
			if len(cur_questions[rnd])==5:
				if cur_questions[rnd][3] in addedList:	#If Sentence Of Question Is Already Used, Remove From Consideration
					del cur_questions[rnd]
					continue
				else:
					addedList.append(cur_questions[rnd][3])
			curPMarks+=cur_questions[rnd][2]	#Update Marks
			curQList.append(cur_questions[rnd])
			del cur_questions[rnd]
			cur_questions=[q for q in cur_questions if q[2]<=totalPMarks-curPMarks]	#Update List Of Available Questions
		carryOver=totalPMarks-curPMarks
		finalQList+=curQList	#Update List Of Questions In Set
		curMarks+=curPMarks 	#Update Marks


	print "\nOne Question Set Is"
	for i in range(len(finalQList)):
 		print i+1, ") ", finalQList[i][0], "\n"

	print "\nThe Corresponding Answers Are"
	for i in range(len(finalQList)):
		if finalQList[i][-1]!=-1:
 			print i+1, ") ", finalQList[i][-1], "\n"
		else:
 			print i+1, ") ", "**Not Currently Available**", "\n"

def add_context():

	QNN=[]
	SNN=[]
	stemList=[]
	sentnum= []
	
	global docLen
	docLen= [len(i.split()) for i in resSentences]
	docLen= sum(docLen)	#Total Count Of Words In The Document


	for eq in range(len(all_questions)):

		# if(len(all_questions)-1 <= eq and sentnum[eq]== all_questions[neq][-1]):
		QNN=[]
		SNN=[]
		stemList=[]
		contextWord= []

		# print eq, sentences[eq], all_questions[neq]
		tmpL=nltk.word_tokenize(all_questions[eq][0])
		tags= nltk.pos_tag(tmpL)
		stemList=tmpL

		for it in range(len(stemList)):
			stemList[it]=stemmer.stem(stemList[it])	#List Of Stemmed Words From The Question Statement

		for word, tag in tags:
			if(re.search("NN.*", tag)):
				QNN.append(word.lower())
		QNN=list(set(QNN))	#List Of NNs In Question Statement

		maxVal=0
		maxCmp=0
		for it in QNN:
			if(termFreq.get(it, 'empty')!= 'empty'):
				tmp= idf(it)
				if(tmp >maxCmp):
					maxVal=it
					maxCmp= tmp 	#QNN With Highest Frequency In Document, maxVal
		
		tags= nltk.pos_tag(nltk.word_tokenize(resSentences[all_questions[eq][3]]))

		for word, tag in tags:
			if(re.search("NN.*", tag)):
				SNN.append(word.lower())
		SNN=list(set(SNN))	#List Of NNs In Base Sentence

		maxVal2= []
		maxCmp2= []

		for jN in SNN:
			jNS=stemmer.stem(jN)
			if(jNS not in stemList):	#If An NN In The Base Sentence Is Not In The Question
				if(termRel.get(maxVal, 'qwertyuiop')!= 'qwertyuiop'):
					if(termRel[maxVal].get(jN, 'qwertyuiop')!= 'qwertyuiop'):
						if(termOcc.get(maxVal, 'qwertyuiop')!= 'qwertyuiop'):
							if(float(termRel[maxVal][jN])/termOcc[maxVal]>=thres):	#If The Ratio Of (Times the word appears in the same sentence as maxVal/Number Of Sentences It Appears In) Crosses A Threshold
								contextWord.append(jN)	#Keep As Context Word
								maxCmp2.append(float(termRel[maxVal][jN])/termOcc[maxVal] * idf(jN))	#Store The (ratio*Times the word appears in the document)


		delWords= []

		if(contextWord!= [] and contextWord!= ""):
			for cW in contextWord:
				tags= nltk.pos_tag(nltk.word_tokenize(cW))
				if(re.search("NN.*", tags[0][1])):
					pass
				else:
					delWords.append(cW)	#If The Word Is Not NN, Don't Use


		if(delWords!= []):
			for dl in delWords:
				contextWord.remove(dl)

		maxidf1= 0
		maxidf2= ""
		for it in range(len(contextWord)):
			if(maxCmp2[it] > maxidf1):
				maxidf1=maxCmp2[it]
				maxidf2=contextWord[it]

		contextWord=maxidf2	#Context Word With Highest Frequency In Document

		if contextWord!= [] and contextWord!= "":
			all_questions[eq][0]+="\nKeyword: "+contextWord	#Forming The Question

def idf(s):	#Actually Only Document Frequency

	if(termFreq.get(s, 'empty')!= 'empty'):
		return termFreq[s]
	else:
		return 0


################################################# simplify #######################################################################
# Function used to simplify the pronounresun resolved text
##################################################################################################################################


def simplify(s):

	temp= ""
	stmp1= parser.raw_parse_sents((s, ""))

	tree1= Tree("root", stmp1)

	tree1= recurse(tree1[0])

	if(tree1):
		temp= " ".join(tree1.leaves())
		return temp

	else:
		return ""



################################################# recurse #######################################################################
# Function used to recursively traverse the tree and get the last NP node
##################################################################################################################################


def recurse(parent):

	global prev
	global prev2
	for node in parent:
		if(type(node) is nltk.tree.Tree):
			if(node.label()== 'NP'):
				prev.append(node)
			if(node.label()== "JJ"):
				prev2.append(node)
			recurse(node)

	if(prev!= []):
		return prev[-1]
	else:
		return None


################################################# regex ##########################################################################
# Returns compiled form of a pattern
##################################################################################################################################

def regex(s):
	return re.compile(s, re.I)


################################################# genRegex #######################################################################
# Function used to generate a list to store all the compiled regex patterns of discourse markers
##################################################################################################################################

def genRegex():

	global all_discourse
	all_discourse= []
	fp= open("discourse.txt", "r")

	for line in fp:
		line= line.strip("\n").split(".")
		all_discourse.append(line)
	
	all_discourse= [[regex(k) for k in j] for j in all_discourse]	#Turn All Discourse Markers Into Corresponding regexps



################################################ Sentensify ########################################################################
#This function is used to tokenize and split into sentences
####################################################################################################################################

def sentensify():

	global sentences
	global equation_sentences

	tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	fp = open("input.txt")
	data = fp.read()

	sentences= tokenizer.tokenize(data)
	newsen= []
	for i in range(len(sentences)):
		if("\n" in sentences[i]):
			tmp= sentences[i].split("\n")
			newtmp= [j for j in tmp if j != ""]
			newsen+= newtmp
		else:
			newsen+= [sentences[i]]

	sentences= newsen	#Sentences Split Both By "." And "\n"

	print "\nSentences Of The Document\n", "\n".join(sentences)
	spc=r"[ \t]*"
	ele= r"[2-9]*(([A-Z][a-z]|[A-Z])+[2-9]*|[(]([A-Z][a-z]|[A-Z])+[2-9]*[)])+"
	regex= ele+"("+spc+"[+]"+spc+ ele+ ")*("+spc+"->"+spc+")"+ ele+"("+spc+"[+]"+spc+ele+")*"	#For Equations

	flag= 0
	for i in range(len(sentences)):
		if(re.search(regex, sentences[i])):
			flag= 1

			if(":" in sentences[i]):
				tmp= sentences[i]

				equation_sentences.append(tmp)
				sentnumb_map[11].append([i])

			else:
				equation_sentences.append(' '.join(sentences[i-1:i+1]))
				sentnumb_map[11].append([i-1, i])
				#tmp= sentences[i].split(".")[0]



	

	#Function calls

	coreference()
	cluster(sentences)
	calcFreq()
	genEqnQsn()
	print "\nAfter Adding Discourse Marker Questions, The List Of Questions Becomes\n", "\n".join([aQ[0] for aQ in all_questions])
	setRem()
	decisionTree()
	print "\nAfter Adding Programming Questions, The List Of Questions Becomes\n", "\n".join([aQ[0] for aQ in all_questions])
	othersNumb()
	genGapFill()
	titling()
	reduce_sentence()
	pronoun_resolution()
	print "\nFinal Question Bank Is\n", "\n".join([aQ[0] for aQ in all_questions])

def setRem():	#Get Sentences Not Already Turned Into Questions
	global rem
	sentnumbers= [i for i in range(len(resSentences))]

	othersnum= []
	for k, v in sentnumb_map.items():
		for val in v:
			for s in val:
				othersnum.append(s)

	rem= list(set(sentnumbers)- set(othersnum))

def genEqnQsn():
	clearLst=[]
	for eqnSent in range(len(equation_sentences)):
		eqn=equation_sentences[eqnSent].strip().split(".")
		
		if len(eqn)==1 and ':' in eqn[0]:
			eqn=eqn[0].split(":")
			pSen= eqn[0].strip()
			eqn= eqn[1].strip()

		elif(len(eqn)== 2):
			pSen= eqn[0]
			eqn= eqn[1]	#Get Equation And Previous Sentence, Based On Whether The Delimiter Is "\n" Or Just ":"


		spl0=re.split("->",eqn)
		spl1=spl0[0].strip().split("+")
		spl2=spl0[1].strip().split("+")	#Get Each Component Of Equation
		tags=nltk.pos_tag(nltk.word_tokenize(pSen))
		checkTag=""
		checkWord=""
		flag=0
		for word, tag in tags:
			if(re.search("equation|reaction",word,re.I)):	#If Previous Sentence Has Keywords Like "equation" Or "reaction"
				if checkTag=="NNP" or checkTag=="NNPS":
					flag=1
					break
			else:
				checkTag=tag
				checkWord=word
		if flag==1:
			q="In The Following Example Of "+checkWord+" Reaction, What Is Missing?\n"	#One Type Of Question, Gap-Fill
			rnd1=random.randint(0,len(spl1)-1)
			rnd2=random.randint(0,len(spl2)-1)
			for it in range(len(spl1)):
				if(it==rnd1):
					q+="____+"
				else:
					q+=spl1[it].strip()+"+"
			q=q[:-1]+"->"
			for it in range(len(spl2)):
				if(it==rnd2):
					q+="____+"
				else:
					q+=spl2[it].strip()+"+"	#Replace One Component In Both LHS And RHS With Blank
			q=q[:-1]
			all_questions.append([q, 11, 2, sentnumb_map[11][eqnSent][0], -1])
			q="Provide Below The "+checkWord+" Reaction."	#Another Type, Definition
			all_questions.append([q, 11, 2, sentnumb_map[11][eqnSent][0], -1])
		q="Balance the following equation:\n"	#Third, General Type Of Question, Balancing
		it=0
		while it<len(spl1):
			if(spl1[it][0]>="2" and spl1[it][0]<="9" or spl1[it][0]==" "):
				spl1[it]=spl1[it][1:]
				it-= 1
			it+=1	#Removing Ordinal Values From LHS
		it=0
		while it<len(spl2):
			if(spl2[it][0]>="2" and spl2[it][0]<="9" or spl1[it][0]==" "):
				spl2[it]=spl2[it][1:]
				it-= 1
			it+=1	#Removing Ordinal Values From RHS
		for it in range(len(spl1)):
			q+=spl1[it].strip()+"+"
		q=q[:-1]+"->"
		for it in range(len(spl2)):
			q+=spl2[it].strip()+"+"
		q=q[:-1]
		all_questions.append([q, 11, 2, sentnumb_map[11][eqnSent][0], -1])	#Adding Question Into The Final Set



################################################# reduce_sentence ################################################################
# Function used to reduce sentence with multiple discourse markers belonging to 3 or more clusters
##################################################################################################################################

def reduce_sentence():

	tmp= []
	a= contradictory_sentences+ additive_sentences+ concluding_sentences+ emphasis_sentences+ illustrate_sentences+ why_sentences+ when_sentences

	a= [i for i in a if len(i)== 1]

	for i in a:
		if(a.count(i) >= 3):
			tmp.append(i)
			for j in range(a.count(i)):
				a.remove(i)

	for i in contradictory_sentences:
		if i in tmp:
			contradictory_sentences.remove(i)

	for i in additive_sentences:
		if i in tmp:
			additive_sentences.remove(i)

	for i in concluding_sentences:
		if i in tmp:
			concluding_sentences.remove(i)

	for i in emphasis_sentences:
		if i in tmp:
			emphasis_sentences.remove(i)

	for i in illustrate_sentences:
		if i in tmp:
			illustrate_sentences.remove(i)

	for i in why_sentences:
		if i in tmp:
			why_sentences.remove(i)

	for i in when_sentences:
		if i in tmp:
			when_sentences.remove(i)


################################################# getNode #######################################################################
# Function used to get appropriate subject node for a sentence for pronoun resolution
##################################################################################################################################

def getNode(tree):

	global nounphrase
	node= None
	for t in tree:
		n1= t
		break

	for t in n1:
		n2= t
		break

	for t in n2:
		if(t.label()== "S" or t.label()== "FRAG"):
			node= t
			break

	s= ""
	flag1= 0
	flag2= 0
	nounphrase= 0
	if(node):
		for n in node:
			if(n.label()== "NP"):
				s+= ' '.join(n.leaves())+ " "
				s= s[0].upper()+ s[1:]
				nounphrase= len(s.split())
				flag1= 1

			if(n.label()== "VP"):
				s+= ' '.join(n.leaves())+ "."
				flag2= 1

			if(flag1== 1 and flag2 ==1):
				return s

	return ""

################################################# genPreSentence #################################################################
# Function used to get NP-VP Pair of sentence
##################################################################################################################################

def genPreSentence(i):

	if(type(i) is int):

		if(i-10> 0):
			tmp= sentences[i-10:i+1]
		else:
			tmp= sentences[0:i+1]

	else:
		tmp= [i]

	node= ""
	if(tmp):
		tmp.reverse()
		for s in tmp:

			s= parser.raw_parse_sents((s, ""))

			tree= Tree("root", s)

			node= getNode(tree)

			if(node != ""):
				break

	return node


################################################# pronoun_resolution #############################################################
# Function used to resolve common pronouns using stanford corenlp
##################################################################################################################################

def pronoun_resolution():

	i=0
	w= ""
	for k, v in sentnumb_map.items():

		c= 0
		for q in all_questions[i: i+len(v)]:

			tags= nltk.pos_tag(nltk.word_tokenize(q[0]))

			only_tags= [tag for word, tag in tags]

			flag= 0
			flag3= 0
			for ot in range(len(only_tags)):

				#Search for tags PRP
				if(re.search("PR.*", only_tags[ot])):
					w= tags[ot][0]
					w= w.encode("utf-8")
					flag= 1

				#For words like this, these
				res= re.search("DT", only_tags[ot])
				if(res and (tags[ot][0].lower()== "these" or tags[ot][0].lower()== "this" or tags[ot][0].lower()== "those")):
					flag3= 1


			if(flag3== 1):
				pre_sentence= genPreSentence(all_questions[i][3]-1)
				all_questions[i][0]= pre_sentence+ all_questions[i][0]

			if(flag== 1):

				flag2= 0
				pronounres= []
				if result.get('coref',-1)!=-1:
					for res in result['coref']:
						for j in res:
							if(j[0][1] == sentnumb_map[k][c][0] and j[0][0]== w and flag2== 0):
								pronounres= j
								flag2= 1
								break
						if(flag2):
							break

					if(flag2):
						if(len(pronounres[1][0].split())>= 3):
							sim= simplify(pronounres[1][0])

						else:
							sim= pronounres[1][0]

						if(sim not in all_questions[i][0]):
							all_questions[i][0]= all_questions[i][0].replace(pronounres[0][0], sim)

			c+= 1
			i+= 1



################################################# cluster ########################################################################
# Function used to cluster sentences into different discourse marker categories.
##################################################################################################################################

def cluster(sentences):

	for s in range(len(sentences)):
		for i in range(len(all_discourse)):
			for j in range(len(all_discourse[i])):			
				res= all_discourse[i][j].search(sentences[s])
				if(res):
					try:
						if(res.group()[0] >= 'A' and res.group()[0] <= 'Z'):
							if(all_discourse[i][j].search('Finally,') or all_discourse[i][j].search('Lastly,')):	#Discuss Questions
								count= 0
								if(s>6):
									beg1= s-6
									beg2= s-7
								else:
									beg1= 0
									beg2= 0

								for k in sentences[beg1:s+1]:
									if(re.search("Firstly,", k, re.I)):
										temp= [sentences[beg2+count]]
										temp2= [beg2+count]
										break

									count+= 1

							elif(all_discourse[i][j].search('Furthermore,')):	#Additive
								if(re.search("Further", sentences[s-1], re.I)):
									temp= sentences[s-2: s+1]
									temp2= [s-2, s]
								else:
									temp= sentences[s-1: s+1]
									temp2= [s-1, s]

							elif(all_discourse[i][j].search('Although')):	#Contradictory
								temp= [sentences[s]]
								temp2= [s]

							elif(i <= 4):	#Illustrative
								temp= sentences[s-1: s+1]
								temp2= [s-1, s]

							else:
								temp= [sentences[s]]
								temp2= [s]

						else:
							temp= [sentences[s]]
							temp2= [s]	#All Else

						sentences_map[i].append(temp)
						sentnumb_map[i].append(temp2)

					except:
						print "Exception"

					

	curr= contradictory_sentences+ additive_sentences+ concluding_sentences+ emphasis_sentences+ illustrate_sentences+ why_sentences+ when_sentences+ discuss_sentences
	tmp= []
	for i in curr:
		for j in i:
			tmp.append(j)
	others= list(set(sentences)- set(tmp))

	print "\nClustered Questions\n",sentences_map

	# print "contradictory_sentences= ", contradictory_sentences ,"\n\n"
	# print "additive_sentences= ", additive_sentences ,"\n\n"
	# print "concluding_sentences= ", concluding_sentences ,"\n\n"
	# print "emphasis_sentences= ", emphasis_sentences ,"\n\n"
	# print "illustrate_sentences= ", illustrate_sentences ,"\n\n"
	# print "why_sentences= ", why_sentences ,"\n\n"
	# print "when_sentences= ", when_sentences ,"\n\n"
	# print "discuss_sentences= ", discuss_sentences, "\n\n"
	# print "others= ", others ,"\n\n"
	remBrackets()
	genContQuestionTerms()
	genContQuestion()
	genConcludingQuestions()
	genwhyQuestions()
	genIllustrativeQuestions()
	genWhenQuestions()
	genDiscussQuestions()	#Generate Each Question Type In Turn

def genDiscussQuestions():

	for i in range(len(discuss_sentences)):

		pre= genPreSentence(sentnumb_map[7][i][0])

		tags= nltk.pos_tag(nltk.word_tokenize(pre))

		s= ""
		flag= 0
		for word, tag in tags:
			if(re.search("VB.*", tag) and flag==0):
				s+= en.verb.present_participle(word)+ " "	#Convert The Main Verb To Present Participle
				flag=1
			else:
				s+= word+ " "

		if(s!= "" and s[-2]!= "."):
			s= s[:-1]+"."

		all_questions.append(["Discuss about "+s, 7, 5, sentnumb_map[7][i][0], -1])	#Add To All Questions


################################################# genwhenQuestions ###############################################################
# Function used to generate why questions
##################################################################################################################################

def genWhenQuestions():

	for i in range(len(when_sentences)):

		s= when_sentences[i][0].split("when")[0]	#Get First Part Of The Sentence

		s= genPreSentence(s)	#Get Main Clause

		tags= nltk.pos_tag(nltk.word_tokenize(s))

		flag= 0
		flag8= 0
		for word, tag in tags:
			for j in aux_list:
				if(word== j):
					flag= 1
					aux= word 	#If Auxiliary Already Exists, Locate It
					break
			if(flag):
				break

		if(flag==0):

			for word, tag in tags:

				res= re.search("VB.*", tag)
				if(res and flag8== 0):
					flag8= 1
					s= s.replace(word, en.verb.present(word))

			tags= nltk.pos_tag(nltk.word_tokenize(s))		
			flag1= 0
			flag2= 0
			s= ""
			kW=""
			for word, tag in tags:
				tmp= None
				res= re.search("VB.*", tag)
				if(res and not flag1):
					if(res.group()[-1] in ['D', 'N']):	#If Main Verb Is Past Tense
						flag1=1
						kW=" did "	#Auxiliary Is "did"
						tmp= stemmer.stem(word)
						s+=en.verb.present(word)+" "
						continue
				if(not re.search("RB.*", tag)):	#Ignore Adverbs
					s+= word+ " "
			if kW:

				if(s!= ""):
					question= "When"+kW+s+"?"

					all_questions.append([question, 6, 2, sentnumb_map[6][i][0], " ".join(sentences[sentnumb_map[6][i][0]: sentnumb_map[6][i][-1]+1])])
			else:
				s=""
				for word, tag in tags:
					res= re.search("NN.*", tag)

					if(res and not flag2):
						if(res.group()[-1]== 'S'):	#If Main Noun Is Multiple
							flag2= 1
							kW=" do "
							tmp= word
							s= " do "+ s 	#Auxiliary Is "do"
						else:
							flag2= 1
							kW=" does "
							tmp= word
							s= " does "+ s	#Auxiliary Is "does"
					if(not re.search("RB.*", tag)):	#Ignore Adverbs
						s+= word+ " "

				if(s!= ""):
					question= "When"+ s+ "?"	#Add "Why" And "?"
					all_questions.append([question, 6, 2, sentnumb_map[6][i][0], " ".join(sentences[sentnumb_map[6][i][0]: sentnumb_map[6][i][-1]+1])])	#Add To Questions


		elif(flag==1):

			taux= r"\b"+aux+r"\b"
			tmp= re.split(taux, s)
			s= aux + " " + tmp[0][:-1]+ tmp[1] 	#Move Auxiliary To The Front

			stags= nltk.pos_tag(nltk.word_tokenize(s))
			s= ""
			for word, tag in stags:

				# res= re.search("VB.*", tag)
				# if(res and res.group()!= aux):
				# 	s+= en.verb.present(word, person=3)+ " "

				if(re.search("RB.*", tag)):	#Remove Adverbs
					pass

				else:
					s+= word+ " "

			s= s[:-2]

			if s!= "":
				all_questions.append(["When "+s+ "?", 6, 2, sentnumb_map[6][i][0], " ".join(sentences[sentnumb_map[6][i][0]: sentnumb_map[6][i][-1]+1])])	#Add "When" And "?" As Needed To Form The Question


################################################# genIllustrativeQuestions #######################################################
# Function used to generate illustrative questions
##################################################################################################################################

def genIllustrativeQuestions():

	tmpq= ""
	for i in range(len(illustrate_sentences)):

		num= sentnumb_map[4][i][0]
		q= 0
		flag= 0
		for k, v in sentnumb_map.items():
			if(k!= 4):
				for val in range(len(v)):
					
					if(num== sentnumb_map[k][val][0]):	#If The Previous Sentence Is Already Used In A Different Question, Add " Give an illustration." At The End
						tmpq= q
						flag= 1
						break

					q+= 1
			if(flag):
				break

		if(flag):
			all_questions[tmpq][0]=remPunct(all_questions[tmpq][0])
			all_questions[tmpq][0]+= " Give an illustration."
			all_questions[tmpq][2]= 4
			all_questions[tmpq][1]= 10
			all_questions[tmpq][1]= sentnumb_map[4][i][0]


		else:
				
			if(len(illustrate_sentences[i])== 1):	#Marker Is In The Middle Of The Sentence

				for j in all_discourse[4]:
					isen= ' '.join(illustrate_sentences[i])
					res= j.search(isen)

					if(res):
						s= isen.split(res.group())[-1]

						s= genPreSentence(s)	#Get NP-VP Of Sentence

						tags= nltk.pos_tag(nltk.word_tokenize(s))

						s= ""
						tmp= None
						for word, tag in tags:
							
							if(re.search("VB.*", tag)):
								tmp= word

							else:
								if(tmp):
									tmp= en.verb.present_participle(tmp)	#If Previous Word Was Verb, Make It Present Participle Before Adding Both
									s+= tmp+" "+ word+ " "
									tmp= None
								else:
									s+= word+ " "

						if(s[-2]!= "."):
							s= s[:-2]+ "."

						all_questions.append(["Give an illustration for "+ s, 4, 2, sentnumb_map[4][i][0], " ".join(sentences[sentnumb_map[4][i][0]: sentnumb_map[4][i][-1]+1])])	#Make The Question

			else:	#Marker Is At The Start Of The Sentence

				s= genPreSentence(sentnumb_map[4][i][0])
				tags= nltk.pos_tag(nltk.word_tokenize(s))
				s= ""
				tmp= None
				for word, tag in tags:

					
					if(re.search("VB.*", tag)):
						tmp= word

					else:
						if(tmp!="safe" and tmp):
							tmp= en.verb.present_participle(tmp)
							s+= tmp+" "+ word+ " "
							tmp= None
						else:
							s+= word+ " "
				if(s!= "" and s[-2]!= "."):
					s= s[:-2]+ "."
				if(s!= "" and len(s.split())<= 15):		
					all_questions.append(["Give an illustration for "+ s, 4, 2, sentnumb_map[4][i][0], " ".join(sentences[sentnumb_map[4][i][0]: sentnumb_map[4][i][-1]+1])])	#Make The Question Similarly
				elif(s!= ""):		
					all_questions.append([s[0].upper()+ s[1:]+ " Give an illustration.", 4, 2, sentnumb_map[4][i][0], " ".join(sentences[sentnumb_map[4][i][0]: sentnumb_map[4][i][-1]+1])])	#Make The Question Similarly



################################################# removeDM #######################################################################
# Function used to remove discourse markers from a sentene
##################################################################################################################################

def removeDM(s):
	for i in all_discourse:
		for j in i:
			res= j.search(s)
			if(res):
				s= s.replace(res.group(), "")
	return s


################################################# genwhyQuestions ################################################################
# Function used to generate reasoning questions
##################################################################################################################################

def genwhyQuestions():
	global all_questions
	qphrase= " Why"
	i= 0
	for line in why_sentences:

		line= ' '.join(line)
		for disc in all_discourse[5]:
			
			res= disc.search(line)
			s= ""
			if(res):

				if(line.index(res.group()) != 0):	#If Marker In The Middle Of The Sentence

					i1= -1
					i2= line.index(res.group())

				else:

					#If the DM occur at the beginning of the sentence 
					if(res.group()== "Since" or (res.group()== "Because" and line.split()[0][-1] != ",")):	#If Marker Is "Since", Or "Because"(Dependant On Same Sentence)
						i1= line.index(",")+1
						i2= line.index(line[-1])+1


					else:
						pre= genPreSentence(sentences[sentnumb_map[5][i][0]-1])	#"Because," With Data In Previous Sentence
						i1= 0
						i2= 0
				if(i1<i2):	#"Because," Or "Since" Dependent On Same Sentence
					s+= line[i1+1:i2]
				elif(i1== i2 == 0):	#"Because,", On Previous Sentence
					s= pre
				else: 	#Marker In Middle Of Sentence
					s+= line[i2+6: i1]
				
				if(i1== -1):	#Current Line
					var1=-1
				elif(i1<i2):	#Middle Of The Line
					var1=0
				else:	#Previous Line
					var1=-1
				s=re.split(r"\band\b|\bor\b", s, re.I)[var1]	#Get The Relevant Fraction Of Sentence
				s= removeDM(s)	#Remove Excess Markers
				allw= s.split(" ")
				fl=0
				for itr in range(len(allw)): 
					if(allw[itr] in aux_list):
						fl=1
						s= allw[itr] + " " +' '.join(allw[:itr])+ " " +' '.join(allw[itr+1:])	#Push Auxiliary To Front
						question= qphrase+" "+ s+ "?"	#Add "Why" And "?"
						all_questions.append([question, 5, 2, sentnumb_map[5][i][0], " ".join(sentences[sentnumb_map[5][i][0]: sentnumb_map[5][i][-1]+1])])	#Add To Questions
						break
				if(fl==0):
					tags= nltk.pos_tag(nltk.word_tokenize(s))
					flag1= 0
					flag2= 0
					s= ""
					kW=""
					for word, tag in tags:
						tmp= None
						res= re.search("VB.*", tag)
						if(res and not flag1):
							if(res.group()[-1] in ['D', 'N']):	#If Main Verb Is Past Tense
								flag1=1
								kW=" did "	#Auxiliary Is "did"
								tmp= stemmer.stem(word)
								s+=en.verb.present(word)+" "
								continue
						if(not re.search("RB.*", tag)):	#Ignore Adverbs
							s+= word+ " "
					if kW:
						question= qphrase+kW+s+"?"
						all_questions.append([question, 5, 2, sentnumb_map[5][i][0], " ".join(sentences[sentnumb_map[5][i][0]: sentnumb_map[5][i][-1]+1])])
					else:
						s=""
						for word, tag in tags:
							res= re.search("NN.*", tag)

							if(res and not flag2):
								if(res.group()[-1]== 'S'):	#If Main Noun Is Multiple
									flag2= 1
									kW=" do "
									tmp= word 	#Auxiliary Is "do"
								else:
									flag2= 1
									kW=" does "
									tmp= word 	#Auxiliary Is "does"
							if(not re.search("RB.*", tag)):	#Ignore Adverbs
								s+= word+ " "
						question= qphrase+ kW+s+ "?"	#Add "Why" And "?"
						all_questions.append([question, 5, 2, sentnumb_map[5][i][0], " ".join(sentences[sentnumb_map[5][i][0]: sentnumb_map[5][i][-1]+1])])	#Add To Questions
		i+= 1

################################################# genConcludingQuestions #########################################################
# Function used to generating questions based on conclusions
##################################################################################################################################


def genConcludingQuestions():

	qphrase= " How was it concluded that "
	i= 0
	flag=1
	for line in concluding_sentences:
		s= ' '.join(line)
		q= ""
		for disc in all_discourse[2]:
			res= disc.search(s)
			if(res):
				q= s.split(res.group())
				if res.group()[0]>="a" and res.group()[0]<="z":
					j=-1
					while True:
						if q[0][j]==" ":
							j-=1
						elif q[0][j]==",":
							flag=0
							break
						else:
							break
				break
		if(q!= "" and flag):
			all_questions.append([qphrase+ q[1]+ "?", 2, 2, sentnumb_map[2][i][0], " ".join(sentences[sentnumb_map[2][i][0]: sentnumb_map[2][i][-1]+1])])
		else:
			del sentnumb_map[2][i]

		i+= 1


################################################# tokenize #######################################################################
# Function used to generate tags using stanford parser
##################################################################################################################################

def tokenize(s):

	s= parser.raw_parse_sents((s, ""))
	tree= Tree("root", s)

	for node in tree[0]:
		n= node
		break

	return [(word, tag) for word, tag in n.pos()]


################################################# genContQuestion ################################################################
# Function used to generating contradictory questions
##################################################################################################################################

def genContQuestion():

	qphrase= " What opposing view has been provided in the passage?"

	i= 0
	for qt in qterms:
		
		# qt= qt.replace(".", "")
		# temp= ""

		# if("|" in qt):
		# 	temporary= qt.split("|")
		# 	if(len(temporary)== 2):
		# 		np= temporary[0]
		# 		vp= temporary[1]
		# 	else:
		# 		np= temporary[0]
		# 		vp= ""
		# else:
		# 	np=""
		# 	vp= qt

		# tags= tokenize(np+ " "+vp+ ".")

		# flag= 0
		# flag2= 0
		# for word, tag in tags:


		# 	if(flag== 1 and tag not in "," and tag not in "."):
		# 		temp+= word+ " "


		# 	if(re.search("VB.*", tag) and flag==0):
		# 		flag= 1
		# 		temp= word+ " "
			
		all_questions.append([qt+ qphrase, 0, 2, sentnumb_map[0][i][0], " ".join(sentences[sentnumb_map[0][i][0]: sentnumb_map[0][i][-1]+1])])

		i+= 1


################################################# genContQuestionTerms ##########################################################
# Function used to generate phrases which can form a contradictory question.
##################################################################################################################################

def genContQuestionTerms():

	fp= open("targetarg.txt", "r")
	d= fp.read().strip("\n")

	d= ast.literal_eval(d)

	global curr
	for s in contradictory_sentences:		
		for dm in all_discourse[0]:
			res= dm.search(' '.join(s))
			if(res):
				discmark= res.group()
				break
		l= len(s)

		discmark= discmark.replace("\b", "")
		discmark= discmark.replace(",", "")

		details= d[discmark.lower()]
		if(l== 1):
			sen= s[0].split(discmark)[details[0]-1]

		else:
			sen= s[details[0]-1]

		tags= nltk.pos_tag(nltk.word_tokenize(sen))
		sen=""
		for word, tag in tags:
			if not re.search("RB", tag):
				sen+=word+" "
		sen=sen[:-1]
		if(sen[-1] != "."):
			sen= sen+ "."

		qterms.append(sen)
		# sen= parser.raw_parse_sents((sen, ""))

		# tree= Tree("root", sen)
		# curr= ""


		# treegen(tree[0], details[1])


################################################# treegen ########################################################################
# Function used to send appropriate node from tree to get question phrases
##################################################################################################################################

def treegen(parent, dm):
	for node in parent:
		n1= node
		break

	for node in n1:
		n2= node
		break	
	
	recursive(n2, dm)



################################################# recursive ######################################################################
# Function used to get question phrases by appropriately choosing the subject from the tree.
# Each discourse marker has different subject phrses which can result in a question.
# These have been listed in targetarg.txt and it is passed as an argument to this function (dm)
##################################################################################################################################

def recursive(n2, dm):

	global curr

	if(dm== 2):
		flag= 0
		for node in n2:
			s= ""
			if(node.label()== "S"):
				flag= 1
				for n in node:
					if(n.label()== 'NP'):
						s+= ' '.join(n.leaves())+ "|"
					if(n.label()== "VP"):
						flag2= 0
						for no in n:
							if(no.label()== 'CC'):
								flag2= 1
								cc= no.leaves()
								break


						tp= ' '.join(n.leaves())+ " "

						if(flag2):
							tp= tp.split(cc)[-1]+ " "

						s+= tp					
					curr= s

		if(flag== 0):
			if(n2.label()== "S"):
				flag= 1
				for n in n2:
					if(n.label()== 'NP'):
						s+= ' '.join(n.leaves())+ "|"
					if(n.label()== "VP"):
						flag2= 0
						for no in n:
							if(no.label()== 'CC'):
								flag2= 1
								cc= no.leaves()[0]
								cc= cc.encode("utf-8")
								break

						tp= ' '.join(n.leaves())+ " "
						if(flag2):
							tp= tp.split(cc)[-1]+ " "							

						s+= tp
					curr= s

		curr= curr.encode("utf-8")

		qterms.append(curr)

	else:
		flag= 0
		for node in n2:
			s= ""
			if(node.label()== "S"):
				flag= 1
				for n in node:
					if(n.label()== 'NP'):
						s+= ' '.join(n.leaves())+ "|"
					if(n.label()== "VP"):
						flag2= 0
						for no in n:
							if(no.label()== 'CC'):
								flag2= 1
								cc= no.leaves()
								break

						tp= ' '.join(n.leaves())+ " "

						if(flag2):
							tp= tp.split(cc)[0]+ " "

						s+= tp

					curr= s
				break

		if(flag== 0):
			if(n2.label()== "S"):
				flag= 1
				for n in n2:
					if(n.label()== 'NP'):
						s+= ' '.join(n.leaves())+ "|"
					if(n.label()== "VP"):
						flag2= 0
						for no in n:
							if(no.label()== 'CC'):
								flag2= 1
								cc= no.leaves()
								break

						tp= ' '.join(n.leaves())+ " "

						if(flag2):
							tp= tp.split(cc)[0]+ " "

						s+= tp

					curr= s

	
		curr= curr.encode("utf-8")

		qterms.append(curr)

def remQsns():
	remLst=[]
	for it in range(len(all_questions)):
		if all_questions[it][1]<8:
			sent=nltk.sent_tokenize(all_questions[it][0])[0]
			if len(nltk.word_tokenize(sent))<=4 or genPreSentence(sent)=="":
				remLst.append(it)
				break
	if remLst:
		remLst.sort()
		remLst.reverse()
	for it in remLst:
		del all_questions[it]

def remBrackets(argStr=""):
	if argStr:
		if argStr[0]=="(":
			argStr=argStr[1:]
		if argStr[-1]==")":
			argStr=argStr[:-1]
		argStr=re.sub("\(.*?\)","",argStr)
		return argStr
	else:
		for k in sentences_map.keys():
			if k<8:
				for ln in range(len(sentences_map[k])):
					for sn in range(len(sentences_map[k][ln])):
						if sentences_map[k][ln][sn][0]=="(":
							sentences_map[k][ln][sn]=sentences_map[k][ln][sn][1:]
						if sentences_map[k][ln][sn][-1]==")":
							sentences_map[k][ln][sn]=sentences_map[k][ln][sn][:-1]
						sentences_map[k][ln][sn]=re.sub("\(.*?\)","",sentences_map[k][ln][sn])

def remExtras():
	for it in range(len(all_questions)):
		k=all_questions[it][0][-1]
		if k=="?" or k==".":
			while True:
				if (all_questions[it][0][-1]>="a" and all_questions[it][0][-1]<="z") or (all_questions[it][0][-1]>="A" and all_questions[it][0][-1]<="Z") or (all_questions[it][0][-1]>="0" and all_questions[it][0][-1]<="9"):
					all_questions[it][0]+=k
					break
				else:
					all_questions[it][0]=all_questions[it][0][:-1]
		all_questions[it][0]=re.sub("  +", " ", all_questions[it][0])
	for it in range(len(all_questions)):
		if all_questions[it][1]<8:
			all_questions[it][0]=reCase(all_questions[it][0]).strip()

def quoteBreak(lst):
	flag=""
	ret=[]
	for it in range(len(lst)):
		itr=re.findall(r"[^\\](\"|\')",lst[it])
		for jt in itr:
			if flag=="":
				flag=jt
			elif flag==jt:
				flag=""
		if flag:
			ret.append(it)
	return ret

def reCase(s):
	sents=nltk.sent_tokenize(s)
	totalSent=""
	for it in range(len(sents)):
		words=nltk.word_tokenize(sents[it])
		if words[0][0]>="a" and words[0][0]<="z":
			words[0]=shiftCase(words[0],"U")
		tags= nltk.pos_tag(words)
		newSent=words[0]
		for word, tag in tags[1:]:
			if not re.search("\.|\,", tag):
				newSent+=" "
			if not re.search("NNP.?", tag) and word[0]>="A" and word[0]<="Z":
				newSent+=shiftCase(word,"l")
			elif re.search("NNP.?", tag) and word[0]>="a" and word[0]<="z":
				newSent+=shiftCase(word,"U")
			else:
				newSent+=word
		totalSent+=newSent+" "
	return totalSent.strip()

def remPunct(sent):
	k=sent[-1]
	if k=="?" or k==".":
		while True:
			if (sent[-1]>="a" and sent[-1]<="z") or (sent[-1]>="A" and sent[-1]<="Z") or (sent[-1]>="0" and sent[-1]<="9"):
				sent+=k
				break
			else:
				sent=sent[:-1]
	return sent

def shiftCase(w,c):
	retWord=""
	if c=="l":
		for i in w:
			if retWord=="":
				retWord+=i.lower()
			else:
				retWord+=i
	elif c=="U":
		for i in w:
			if retWord=="":
				retWord+=i.upper()
			else:
				retWord+=i
	return retWord

genRegex()
sentensify()
remQsns()
qSet()
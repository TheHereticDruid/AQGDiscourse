from decision import *
from features import *
import nltk
import ast


obj= Features()

cFp=open("config.txt","r")
cFr=cFp.read().split("\n")
cFp.close()

fp= open(cFr[3].split(":")[1], "r")	#Set To Language Specific File
tree= ast.literal_eval(fp.read().strip())
fp.close()

fp=open(cFr[4].split(":")[1],"r")
start=fp.read().strip().split("\n")
fp.close()

dt= Decision(tree= tree, start=[float(i) for i in start])

def divide():

	fp1= open("input.txt", "r").read().strip()
	para= fp1.split("\n\n")
	para= [nltk.sent_tokenize(i) for i in para]

	return recurse(para, 0, 1)


def recurse(para, i, j):

	if i>= len(para)-1:
		return para

	else:

		t1= obj.ratioK(para[i][-1])
		t2= obj.operators(para[i][-1])
		t3= obj.comments(para[i][-1])
		t4= obj.braces(para[i][-1])
		t5= obj.indent(para[i][-1])
		t6= obj.semicolon(para[i][-1])
		t7= obj.programChain()
		t8= obj.capital(para[i][-1])
		t9= obj.ratioC(para[i][-1])

		t11= obj.ratioK(para[j][0])
		t12= obj.operators(para[j][0])
		t13= obj.comments(para[j][0])
		t14= obj.braces(para[j][0])
		t15= obj.indent(para[j][0])
		t16= obj.semicolon(para[j][0])
		t17= obj.programChain()
		t18= obj.capital(para[j][0])
		t19= obj.ratioC(para[j][0])

		tmp= [t1, t2, t3, t4, t5, t6, t7, t8, t9]
		tmp= dt.refineR([tmp], [0, 8])

		tmp2= [t11, t12, t13, t14, t15, t16, t17, t18, t19]
		tmp2= dt.refineR([tmp2], [0, 8])
		if(dt.score(tmp) and dt.score(tmp2)):
			newpara= []
			for k in range(len(para)):
				if(k== i):
					newpara.append(["\n".join(para[i]+ para[j])])
				elif(k!= j):
					newpara.append(para[k])
			return recurse(newpara, i, j)

		else:
			return recurse(para, j, j+1)

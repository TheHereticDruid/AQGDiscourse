import re
import enchant
import json

prevInChain=0
braceCount=0
commentBlock=[]
encModel=enchant.Dict("en_US")

with open('featureConfig.json') as data_file:    
	conf = json.load(data_file)

keywords= conf["keywords"]
operatorList= conf["operatorList"]
commentSingle= conf["commentSingle"]
commentMultiple= conf["commentMultiple"]
dataFile= conf["dataFile"]
#self.commentDict= conf["commentDict"]

commentDict={}
for cS in commentSingle:
	commentDict[cS]=0
for cM in commentMultiple:
	commentDict[cM[0]]=1

def ratioK(s):
	sW=[ele for ele in re.split("[^A-Za-z0-9_$]",s) if ele!=""]	
	l=len(sW)
	c=0.0
	for ele in sW:
		if ele in keywords:
			c+=1
	if float(l)!=0.0:
		return c/l
	return 0.0

def operators(s):
	#operatorList=["+","-","*","/","^","%",">","<","="]	#set
	for ele in operatorList:
		if ele in s:
			return 1.0
	return 0.0

def comments(s):
	global commentBlock
	# commentSingle=["//"]	#set
	# commentMultiple=[["/*","*/"],["/**","*/"]]	#set
	# commentDict={"//":0,"/*":1,"/**":1}
	if commentBlock!="":
		for ele in commentMultiple:
			if ele[0]==commentBlock:
				if ele[1] in s:
					commentBlock=""
		return 1.0
	else:
		cIndex=9999
		cValue=-1
		for k,v in commentDict.items():
			if k in s and cIndex>s.index(k):
				cIndex=s.index(k)
				cValue=v
		if cValue==0:
			return 1.0
		elif cValue==1:
			for ele in commentMultiple:
				if ele[0] in s:
					if ele[1] not in s:
						commentBlock=ele[0]
			return 1.0
		else:
			return 0.0
	return 0.0

def braces(s):
	global braceCount
	tmp=0
	if "{" in s:
		braceCount+=1
	if braceCount>0:
		tmp=1
	if "}" in s:
		braceCount-=1
	return float(tmp)

def indent(s):
	if s[0]==" " or s[0]=="\t":
		return 1.0
	return 0.0

def semicolon(s):
	if s[:-1]==";":
		return 1.0
	return 0.0

def programChain():
	global prevInChain
	if prevInChain==1:
		prevInChain=0
		return 1.0
	return 0.0

def capital(s):
	for i in s:
		if i==" " or i=="\t":
			continue
		else:
			if i>="a" and i<="z":
				return 1.0
			return 0.0

def ratioC(s):
	sW=[ele for ele in re.split("[^A-Za-z0-9_$]",s) if ele!="" and ele not in keywords]	
	l=len(sW)
	c=0.0
	for ele in sW:
		if encModel.check(ele):
			c+=1
	if float(l)!=0.0:
		return 1.0-c/l
	return 1.0

def run():
	global prevInChain
	fp1=open(dataFile,"r")
	fp2=open("javaTr.txt","w")
	for ln in fp1.read().split("\n")[:-1]:
		vec=ln[-1]
		ln=ln[:-1]
		vec=[str(ratioK(ln)),str(operators(ln)),str(comments(ln)),str(braces(ln)),str(indent(ln)),str(semicolon(ln)),str(programChain()),str(capital(ln)),str(ratioC(ln)),str(float(int(vec)))]
		prevInChain=0
		if vec[-1]=="1.0":
			prevInChain=1
		fp2.write("\t".join(vec))
		fp2.write("\n")
	fp1.close()
	fp2.close()

# run()
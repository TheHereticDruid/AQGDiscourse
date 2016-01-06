from decision import *
import ast
#nn= NeuralNetwork()
#pla= Perceptron([0, 1, 2, 3, 4, 5, 6, 7, 8], "javaTrain.txt")


fp= open("javaTr.txt", "r")

lst= fp.read().split("\n")[:-1]
lst=lst[int(0.8*len(lst)):]
total= len(lst)

start1= 0.0
start2= 0.0
accuracy= []


while start1 <= 1.0:
	start2= 0.0
	while start2 <= 1.0:
		ct= 0
		dt= Decision(tree= {}, start= [start1, start2])
		dt.train()
		for i in range(len(lst)):
			tmp= lst[i].split("\t")
			tmp= [float(j) for j in tmp]
			#op2= pla.run(tmp[0:-1])
			tmp= dt.refineR([tmp], [0,8])
			op1= dt.score(tmp)
			
			#op= nn.test([tmp[:-1]])


			if(op1== tmp[0][-1]):
				ct+= 1
		
		
		accuracy.append([float(ct)/float(total), dt.tree, start1, start2])
		start2+= 0.01
	start1+= 0.01

maximum= reduce(lambda a, b: max(a, b), accuracy)
fp=open("decision.pickle", "w")
fp.write(str(maximum[1]))
fp.close()
fp=open("args.pickle", "w")
fp.write(str(maximum[2])+"\n"+str(maximum[3]))
fp.close()
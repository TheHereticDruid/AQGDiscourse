#Important: The attribute values are referred to by column numbers
import math
import copy
class Decision():
    def __init__(self, tree= {}, start= [0.2, 0.2]):
        self.maxAttr= []
        self.miscalc= 0
        self.tree= tree
        self.start= start

    def create_decision_tree(self, data, attributes, target_attr, fitness_func):
        """
        Returns a new decision tree based on the examples given.
        """
        vals    = [record[target_attr] for record in data]
        default = self.majority_value(data, target_attr)

        # If the dataset is empty or the attributes list is empty, return the
        # default value. When checking the attributes list for emptiness, we
        # need to subtract 1 to account for the target attribute.
        if not data or (len(attributes) ) <= 0:
            return default
        # If all the records in the dataset have the same classification,
        # return that classification.
        elif vals.count(vals[0]) == len(vals):
            return vals[0]
        else:
            # Choose the next best attribute to best classify our data
            best, j = self.choose_attribute(data, attributes, target_attr,
                                    fitness_func)

            if(best not in set(self.maxAttr)):
                self.maxAttr.append(best)
            del(attributes[j])
            
            # Create a new decision tree/node with the best attribute and an empty
            # dictionary object--we'll fill that up next.
            tree = {best:{}}

            # Create a new decision tree/sub-node for each of the values in the
            # best attribute field
            for val in self.get_values(data, best):
                # Create a subtree for the current value under the "best" field
                subtree = self.create_decision_tree(
                    self.get_examples(data, best, val),
                    [attr for attr in attributes if attr != best],
                    target_attr,
                    fitness_func)

                # Add the new subtree to the empty dictionary object in our new
                # tree/node we just created.
                tree[best][val] = subtree

        return tree

    def get_values(self, data, best):
        l= []
        for example in data:
            l.append(example[best])
        s= set(l)
        return list(s)

    def get_examples(self, data, best, val):
        l= []
        for example in data:
            if(example[best]== val):
                l.append(example)
        return l

    def entropy(self, data, target_attr):
        """
        Calculates the entropy of the given data set for the target attribute.
        """
        val_freq     = {}
        data_entropy = 0.0

        # Calculate the frequency of each of the values in the target attr
        for record in data:
            if (record[target_attr] in val_freq):
                val_freq[record[target_attr]] += 1.0
            else:
                val_freq[record[target_attr]]  = 1.0

        # Calculate the entropy of the data for the target attribute
        for freq in val_freq.values():
            data_entropy += (-freq/len(data)) * math.log(freq/len(data), 2) 
            
        return data_entropy

    def gain(self, data, attr, target_attr):
        """
        Calculates the information gain (reduction in entropy) that would
        result by splitting the data on the chosen attribute (attr).
        """
        val_freq       = {}
        subset_entropy = 0.0

        # Calculate the frequency of each of the values in the target attribute
        for record in data:
            if (record[attr] in val_freq):
                val_freq[record[attr]] += 1.0
            else:
                val_freq[record[attr]]  = 1.0

        # Calculate the sum of the entropy for each subset of records weighted
        # by their probability of occuring in the training set.
        for val in val_freq.keys():
            val_prob        = val_freq[val] / sum(val_freq.values())
            data_subset     = [record for record in data if record[attr] == val]
            subset_entropy += val_prob * self.entropy(data_subset, target_attr)

        # Subtract the entropy of the chosen attribute from the entropy of the
        # whole data set with respect to the target attribute (and return it)
        return (self.entropy(data, target_attr) - subset_entropy)


    #Function to choose the next best attribute
    def choose_attribute(self, data, attributes, target_attr, fitness_func):
        gA=[]
        for attr in attributes:
            gA.append(fitness_func(data, attr, target_attr))
        m=gA[0]
        j=0
        k=0
        for i in gA:
            if m<i:
                m=i
                j=k
            k+=1
        return attributes[j], j

    #Discritize into 2 classes. 

    def refineR(self, data, lst):
        for l in range(len(lst)):       
            for i in range(len(data)):
                if float(data[i][lst[l]])< self.start[l]:
                    data[i][lst[l]]=0.0
                else:
                    data[i][lst[l]]=1.0
        return data

    def majority_value(self, data, target_attr):
        l={0.0:0.0,1.0:0.0}
        for record in data:
            l[record[target_attr]]+=1
        if l[0.0]>l[1.0]:
            return 0.0
        else:
            return 1.0


    def train(self):

        #Get data from file
        data=[]
        f = open('javaTr.txt', 'r')
        for line in f:
            p=[float(it) for it in line.strip('\n').split("\t")]
            data.append(p)
        
        f.close()
        alldata= data
        #List of columns which need to be discritized
        lst= [0, 8]   

        #lst2= [1, 2, 5, 6, 8, 10, 11, 12]
        #Function to replace data with boolean values
        data= self.refineR(data, lst)
        #data= refine_classification(data, lst2)
        attributes= [0, 1, 2, 3, 4, 5, 6, 7, 8]
        target_attr= 9

        self.tree= self.create_decision_tree(data, attributes, target_attr, self.gain)


    def score(self, example):
        tmpTree=copy.deepcopy(self.tree)
        while True:
            for k in tmpTree.keys():
                try:
                    tmpTree=tmpTree[k][example[0][k]]
                    break
                except:
                    tmpTree= 1.0
            if tmpTree==0.0 or tmpTree==1.0:
                break
        return tmpTree
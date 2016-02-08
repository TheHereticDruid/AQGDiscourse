The sample quiz distribution is filled in by the user as required in the percentage.json file. There are some conditions to follow while changing this file.
The value 'total_score' takes is the total number of points the quiz is worth.
The keys of the json object 'order' are strings of integers representing question types, as listed below:
0 -> Contradictory
1 -> Additive(NOT IMPLEMENTED)
2 -> Concluding
3 -> Emphasis(NOT IMPLEMENTED)
4 -> Illustrative
5 -> Reasoning
6 -> Time-Related
7 -> Discuss
8 -> True/False
9 -> Gap-Fill
11 -> Equation
12 -> Programming
13 -> Paragraph Level
The values of the object are percentages of the total score each question type is expected to cost. If the limit for a question type can't be reached, the remaining points are carried over to the next question type in consideration.
Th order in which the question types appear in the json object is the order in which they will be added into the sample quiz.

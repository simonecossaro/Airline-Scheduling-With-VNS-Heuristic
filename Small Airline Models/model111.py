import pandas as pd

results = pd.read_csv('results.csv').iloc[:,1:]

sum = 0
for i in range(len(results)):
    sum += (1 - results.iloc[i,5]/results.iloc[i,4])

print(sum / len(results))

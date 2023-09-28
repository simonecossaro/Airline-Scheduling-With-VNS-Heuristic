import matplotlib.pyplot as plt
import pandas as pd

df_results = pd.read_csv('Results/results.csv').iloc[:,1:]
df_time = pd.read_csv('Results/times.csv').iloc[:,1:]

plt.figure(figsize=(6.4,5.5))
x = list()
for i in range(len(df_results)):
    x.append(str(df_results.iloc[i,0])+"\n"+"("+str(df_results.iloc[i,1])+")")
# y1 time for model 1
y1 = df_time.iloc[:,2]
# y2 time for vns
y2 = df_time.iloc[:,-1]
plt.bar(x, y1, color = 'blue')
plt.bar(x, y2, color = 'cyan')
plt.plot(x,y1,marker="o",linestyle="",color='black')
plt.plot(x,y2,marker="o",linestyle="",color='black')
plt.xlabel("airline")
plt.ylabel("time(s)")
plt.savefig('Results/time_plot.png')
plt.clf()
# y3 revenue for model 1
y3 = df_results.iloc[:,2]
# y4 revenue for vns
y4 = df_results.iloc[:,5]
plt.bar(x, y3, color = 'blue')
plt.bar(x, y4, color = 'cyan')
plt.xlabel("airline")
plt.ylabel("revenue(€)")
plt.savefig('Results/results_plot.png')
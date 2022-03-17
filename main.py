#Daniel Cunningham
#C964
#Student ID# 001197223

import pandas
from sklearn.cluster import *
from datetime import *
import tkinter
import matplotlib.pyplot as mpl
import seaborn as sea


def isWithinHour(start, end, current):
    return start <= current <= end


# Descriptive method, includes machine learning DBscan clustering algorithm
def clusterData(data):
    sixFeet = 0.0018288
    dbscan = DBSCAN(eps=sixFeet, min_samples=2, metric='haversine').fit(data[['Latitude', 'Longitude']])
    labels = dbscan.labels_
    data['Cluster'] = labels
    return data


#Non-Descriptive method, classifies employees as exposed or not exposed based on Descriptive method
def contactTracing(data, employee):

    employees = set()
    for i in range(len(data)):
        employees.add(data.iloc[i]["Employee"])

    if employee not in employees:
        return -1

    exposedClusters = set()
    potentialExposures = set()
    exposedEmployees = set()
    exposedTimes = {}
    employeeTimes = {}

    data = clusterData(data)

    for i in range(len(data)):
        if data['Employee'][i] == employee and data['Cluster'][i] != -1:
            exposedClusters.add(data['Cluster'][i])
            exposedTimes.update({data['TimeStamp'][i]: data['Cluster'][i]})

    for i in range(len(data)):
        if data["Cluster"][i] in exposedClusters and data['Employee'][i] != employee:
            potentialExposures.add(data["Employee"][i])
            employeeTimes.update({data['TimeStamp'][i]: data['Cluster'][i]})

    for i in range(len(exposedTimes)):
        start = list(exposedTimes)[i]
        end = list(exposedTimes)[i] + timedelta(hours=1)
        for j in range(len(employeeTimes)):
            if exposedTimes.get(list(exposedTimes)[i]) == employeeTimes.get(list(employeeTimes)[j]) and \
                    isWithinHour(start, end, list(employeeTimes)[j]):
                temp = data.loc[data['TimeStamp'] == list(employeeTimes)[j], 'Employee']
                exposedEmployees.add(temp.iloc[0])

    return exposedEmployees


data = pandas.read_json("Employee_Data.json")
employees = set()
test = set()
for i in range(len(data)):
    employees.add(data.iloc[i]["Employee"])
newData = clusterData(data)


def submitClick():
    textBox.delete('1.0', 'end')
    exposedEmployees = contactTracing(data, entry.get())
    infectedEmployee = entry.get()
    if exposedEmployees == -1:
        textBox.insert('end', "Invalid employee name, please try again")
    elif len(exposedEmployees) == 0:
        textBox.insert('end', "No employees exposed")
    else:
        textBox.insert('end', exposedEmployees)


#Descriptive scatterplot
def scatterplot1():
    mpl.figure(figsize=(12, 8))
    sea.scatterplot(x='Latitude', y='Longitude', data=data, hue='Employee')
    mpl.legend(bbox_to_anchor=[1, 1])
    mpl.show()


#Descriptive scatterplot
def scatterplot2():
    mpl.figure(figsize=(12, 8))
    palette = ["#FFFFFF", "#0000FF", "#8470FF", "#FF7F24", "#00EEEE", "#006400", "#68228B", "#FF1493", "#5E2612",
               "#8E8E38", "#6E7B8B", "#7CFC00", "#FFF68F", "#DC143C", "#98F5FF", "#FFD39B", "#006400", "#8A360F"]
    sea.scatterplot(x='Latitude', y='Longitude', data=newData, hue='Cluster', legend='full', palette=(palette))
    mpl.legend(bbox_to_anchor=[1, 1])
    mpl.show()


#Descriptive scatterplot
def scatterplot3():
    try:
        textBox.delete('1.0', 'end')
        df = pandas.DataFrame()
        times = []
        start = int(entry2.get().split(",")[0].strip())
        for i in range(len(data)):
            if data['TimeStamp'][i].hour == start:
                df = df.append(data.iloc[i])
                times.append(data['Employee'][i]+", "+str(data['TimeStamp'][i].time()).split(":")[0]+":"+str(data['TimeStamp'][i].time()).split(":")[1])
        mpl.figure(figsize=(16, 8))
        sea.scatterplot(x='Latitude', y='Longitude', data=df, palette='bright', hue=times)
        mpl.legend(bbox_to_anchor=[1, 1])
        mpl.show()
    except:
        textBox.delete('1.0', 'end')
        textBox.insert('end', 'Something went wrong, please try again')


window = tkinter.Tk()
window.geometry("600x700+700+200")
window.title("Covid Contact Tracing")
label = tkinter.Label(text="Enter name of Covid positive employee \n "
                            "from the list of all employees below (case sensitive)")
label.pack()
entry = tkinter.Entry(width=50)
entry.pack()
button = tkinter.Button(window, text="Submit", command=submitClick)
button.pack()
spacer = tkinter.Label(text="\n")
spacer.pack()
empList = tkinter.Listbox(window)
for i in range(len(employees)):
    empList.insert(i, list(employees)[i])
empList.pack()
spacer2 = tkinter.Label(text="\n")
spacer2.pack()
label2 = tkinter.Label(text="Exposed employees")
label2.pack()
textBox = tkinter.Text(window, height=4, width=50)
textBox.pack()
textBox.insert('end', 'This application considers an employee exposed if they were in the same 6ft location within 1 '
                      'hour of an infected employee')
spacer3 = tkinter.Label(text="\n")
spacer3.pack()
button2 = tkinter.Button(window, text="Scatterplot of employee locations", command=scatterplot1)
button2.pack()
button3 = tkinter.Button(window, text="Scatterplot of 6ft clusters", command=scatterplot2)
button3.pack()
spacer4 = tkinter.Label(text="\n")
spacer4.pack()
label3 = tkinter.Label(text="Enter 1 hour timeframe between 9am and 5pm in \n 24hr format below to show employee locations "
                            "within that hour \n(for example '13' would be the hour from 1pm to 2pm)")
label3.pack()
entry2 = tkinter.Entry(width=50)
entry2.pack()
button4 = tkinter.Button(window, text="Submit time", command=scatterplot3)
button4.pack()
window.mainloop()

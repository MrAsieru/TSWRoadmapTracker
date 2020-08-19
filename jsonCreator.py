import re
import json
import urllib.request
sections = ["Next Arrival","Upcoming","In Production","In Planning"]
newUpdate = []

class project:
    def __init__(self,ID,TYPE,NAME,STATUS,DATES,STATUSA):
        self.id = ID
        self.type = TYPE
        self.name = NAME
        self.status = STATUS
        self.dates = DATES
        self.statusA = STATUSA

def getRoadmap():
    finished = 0
    file = open("tempFile.txt","w")
    while(finished != 2):
        rm = input("Please paste the roadmap here") #Get the new roadmap
        if rm != "":
            finished = 0
            file.write(rm+"\n")
        else:
            finished += 1
    file.close

def createObjects():
    date = input("Please enter the day of release, YYYY/MM/DD")
    file = open("tempFile.txt","r")
    status = 0
    for i in file:
        i = i.replace("\n","")
        print(i)
        if (i in sections):
            status += 1
        else:
            TYPE = re.search("\[.*\]",i).group(0).replace("[","").replace("]","")
            try:
                ID = re.search("\] .{4,}-",i).group(0).replace("] ","").replace(" -","")
                NAME = re.search("- .*$",i).group(0).replace("- ","")
            except AttributeError:
                ID = re.search(" .*$",i).group(0).replace("- ","")
                NAME = ""
            STATUS = sections[status - 1]
            newProj = project(ID,TYPE,NAME,STATUS,[date],[STATUS])
            newUpdate.append(newProj)
    file.close

def updateProjects():
    f = urllib.request.urlopen("https://raw.githubusercontent.com/MrAsieru/TSWRoadmapTracker/master/projects.json")
    fD = ""
    for line in f:
        fD = fD + line.decode("utf-8")
    print(fD)
    p_dict = json.loads(fD)["Projects"]
    for pr in p_dict:
        ID = pr["ID"]
        NAME = pr["name"]
        TYPE = pr["type"]
        print(pr["timeline"])
        #DATES = pr["timeline"].["dates"]
        #STATUSA = pr["timeline"].["status"]
        

def updateJSON():
    date = input("Please enter the day of release, YYYY/MM/DD")
    file = open("updatedProjects.json","w")
    file.write("[")
        
#getRoadmap()
#createObjects()

updateProjects()

    
    
    

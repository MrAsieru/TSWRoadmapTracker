import re
import json
import urllib.request
import os
sections = ["Next Arrival","Upcoming","In Production","In Planning"]
newUpdate = []
oldProjects = []
mergedProjects = []
date = ""

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
    global date,newUpdate
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
                ID = re.search("\] .{4,} -",i).group(0).replace("] ","").replace(" -","")
                NAME = re.search("- .*$",i).group(0).replace("- ","")
            except AttributeError:
                ID = re.search(" .*$",i).group(0).replace("- ","")
                NAME = ""
            STATUS = sections[status - 1]
            newProj = project(ID,TYPE,NAME,STATUS,[date],[STATUS])
            newUpdate.append(newProj)
    file.close
    print("len: %s"%len(newUpdate))

def getProjects():
    global oldProjects
    f = urllib.request.urlopen("https://raw.githubusercontent.com/MrAsieru/TSWRoadmapTracker/master/projects.json")
    fD = ""
    for line in f:
        fD = fD + line.decode("utf-8")
    p_dict = json.loads(fD)["Projects"]
    for pr in p_dict:
        ID = pr["id"]
        NAME = pr["name"]
        TYPE = pr["type"]
        DATES = pr["timeline"]["dates"]
        STATUSA = pr["timeline"]["status"]
        proj = project(ID,TYPE,NAME,STATUSA[len(STATUSA)-1],DATES,STATUSA)
        oldProjects.append(proj)

def getNewProjectsIDs():
    global newUpdate
    pList = []
    for proj in newUpdate:
        pList.append(proj.id)
    return pList

def mergeProjects():
    global date, mergedProjects,newUpdate,oldProjects
    mergedProjects = oldProjects.copy()
    IDs = getNewProjectsIDs()
    for mProj in mergedProjects:
        if (mProj.id in IDs):
            mProj.dates.append(newUpdate[IDs.index(mProj.id)].dates)
            mProj.statusA.append(newUpdate[IDs.index(mProj.id)].statusA)
            IDs.remove(mProj.id)
        else:
            if mProj.statusA[len(mProj.statusA) - 1] == "Next Arrival":
                mProj.dates.append(date)
                mProj.statusA.append("Released")
            else:
                mProj.dates.append(date)
                mProj.statusA.append("Canceled")

    for proj in IDs:
        mergedProjects.append(newUpdate[IDs.index(proj)])

def updateJSON():
    global date,mergedProjects
    file = open("updatedProjects.json","w")
    file.write("[")
    print(mergedProjects)
    for proj in mergedProjects:
        file.write("{")
        file.write('"id":')
        file.write('"%s"'%proj.id)
        file.write(',"name":')
        file.write('"%s"'%proj.name)
        file.write(',"type":')
        file.write('"%s"'%proj.type)
        file.write(',"timeline":')
        file.write("{")
        file.write('"dates":[')
        for date in proj.dates:
            file.write('"%s"'%date)
            if date != proj.dates[len(proj.dates)-1]:
                file.write(",")
        file.write('],"status":[')
        for status in proj.statusA:
            file.write('"%s"'%status)
            if status != proj.statusA[len(proj.statusA)-1]:
                file.write(",")
        file.write("]}}")
        if proj != mergedProjects[len(mergedProjects)-1]:
            file.write(",")
    file.write("]")
    file.close

def updatedToCurrentJSON():
    os.rename("projects.json","projectsBefore%s.json"%date)
    os.rename("updatedProjects.json","projects.json")

getRoadmap()            
createObjects()
getProjects()
mergeProjects()
updateJSON()
updatedToCurrentJSON()

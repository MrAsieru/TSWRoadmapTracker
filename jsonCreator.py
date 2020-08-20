import re
import json
import urllib.request
import os
from shutil import copyfile

URL = "https://raw.githubusercontent.com/MrAsieru/TSWRoadmapTracker/master/data.json"
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

def askDate():
    global date
    f = False
    tmpDate = ""
    while not f:
        tmpDate = input("Please enter the day of release, YYYY/MM/DD")
        if re.match("\d{4}\/(0[1-9]|1[0-2])\/(0[1-9]|[1-2][0-9]|3[01])",tmpDate):
            date = tmpDate
            f = True
        else:
            print("Invalid date format: xxxx/xx/xx")

def getRoadmap():
    print("Creating file from pasted data...")
    finished = 0
    file = open("Roadmap-%s.txt"%(date.replace("/","")),"w")
    while(finished != 2):
        rm = input("Please paste the roadmap here") #Get the new roadmap
        if rm != "":
            finished = 0
            file.write(rm+"\n")
        else:
            finished += 1
    file.close

def createNewUpdateObjects():
    print("Creating project update list from data...")
    global date,newUpdate
    file = open("Roadmap-%s.txt"%(date.replace("/","")),"r")
    status = 0
    for i in file:
        i = i.replace("\n","") #Remove the line ending
        if (i in sections): #Check if line is section title
            status += 1
        else:
            TYPE = re.search("\[.*\]",i).group(0).replace("[","").replace("]","")
            try:
                ID = re.search("\] .{4,}? -",i).group(0).replace("] ","").replace(" -","")
                NAME = re.search("- .*$",i).group(0).replace("- ","")
            except AttributeError:
                ID = re.search("] .*$",i).group(0).replace("] ","")
                NAME = ""
            STATUS = sections[status - 1]
            newProj = project(ID,TYPE,NAME,STATUS,[date],[STATUS])
            newUpdate.append(newProj)
    file.close
    print("len: %s"%len(newUpdate))

def getProjects():
    print("Downloading old roadmap data...")
    global oldProjects
    f = urllib.request.urlopen(URL) #Download json data from GitHub
    fD = "" #For decoded data
    for line in f:
        fD = fD + line.decode("utf-8")
    p_dict = json.loads(fD)["Projects"]#Dictionary from json data
    print("Creating old project data...")
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
    print("Merging project data...")
    global date, mergedProjects,newUpdate,oldProjects
    mergedProjects = oldProjects.copy()
    IDs = getNewProjectsIDs()
    for mProj in mergedProjects:
        if (mProj.id in IDs):
            mProj.dates.append(newUpdate[IDs.index(mProj.id)].dates)
            mProj.statusA.append(newUpdate[IDs.index(mProj.id)].statusA)
            IDs.remove(mProj.id)
        else:
            if (mProj.statusA[len(mProj.statusA) - 1] == "Upcoming" or mProj.statusA[len(mProj.statusA) - 1] == "Next Arrival"):
                mProj.dates.append(date)
                mProj.statusA.append("Released")
            elif (mProj.statusA[len(mProj.statusA) - 1] == "In Production" or mProj.statusA[len(mProj.statusA) - 1] == "In Planning"):
                mProj.dates.append(date)
                mProj.statusA.append("Canceled")

    for proj in IDs:
        mergedProjects.append(newUpdate[IDs.index(proj)])

def updateJSON():
    global date,mergedProjects
    print("Generating new json file...")
    file = open("updatedData.json","w")
    file.write("{")
    file.write('"Projects":[')
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
    file.write("]}")
    file.close

def updatedToCurrentJSON():
    print("Saving last projects file...")
    os.remove("data.json")
    os.rename("updatedData.json","data.json")
    copyfile("data.json","data%s.json"%(date.replace("/","")))
             
def main():
    askDate()
    getRoadmap()            
    createNewUpdateObjects()
    #getProjects()
    mergeProjects()
    updateJSON()
    updatedToCurrentJSON()
    
try:
    if __name__ == "__main__":
        main()
except KeyboardInterrupt:
    print("Exiting program")
    exit()

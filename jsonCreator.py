import re
import json
import urllib.request
import os
from datetime import datetime as dt
from shutil import copyfile

DEBUG = False
URL = "https://raw.githubusercontent.com/MrAsieru/TSWRoadmapTracker/master/data.json"
sections = ["Next Arrival","Upcoming","In Production","In Planning"]
newProjects = []
oldProjects = []
mergedProjects = []
newRoadmap = ""
oldRoadmaps = []
mergedRoadmaps = []
date = ""
dtNow = ""
p_dict = ""

class project:
    def __init__(self,ID,TYPE,NAME,STATUS,DATES,STATUSA):
        self.id = ID
        self.type = TYPE
        self.name = NAME
        self.status = STATUS
        self.dates = DATES
        self.statusA = STATUSA

class roadmap:
    def __init__(self,DATE,NA,UP,PR,PL):
        self.date = DATE
        self.na = NA
        self.up = UP
        self.pr = PR
        self.pl = PL


#Ask the roadmap date
def askDate():
    global date,dtNow
    f = False
    tmpDate = ""
    while not f:
        tmpDate = input("Please enter the day of release, YYYY/MM/DD")
        if re.match("\d{4}\/(0[1-9]|1[0-2])\/(0[1-9]|[1-2][0-9]|3[01])",tmpDate):
            date = tmpDate
            f = True
        else:
            print("Invalid date format: xxxx/xx/xx")
    dtNow = str(dt.now()).replace(" ","").replace("-","").replace(":","").split(".")[0]

def JSONtoDict():
    print("Downloading old data...")
    f = urllib.request.urlopen(URL) #Download json data from GitHub
    fD = "" #For decoded data
    for line in f:
        fD = fD + line.decode("utf-8")
    p_dict = json.loads(fD)#Dictionary from json data

def getRoadmapString():
    print("Creating file from pasted data...")
    finished = 0
    if DEBUG:
        file = open("Roadmap-%s-%s.txt"%(date.replace("/",""),dtNow),"w")
    else:
        file = open("Roadmap-%s.txt"%(date.replace("/","")),"w")
    while(finished != 2):
        rm = input("Please paste the roadmap here") #Get the new roadmap
        if rm != "":
            finished = 0
            file.write(rm+"\n")
        else:
            finished += 1
    file.close

def createNewProjectsObjects():
    print("Creating project update list from data...")
    global date,newProjects
    if DEBUG:
        file = open("Roadmap-%s-%s.txt"%(date.replace("/",""),dtNow),"r")
    else:
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
            newProjects.append(newProj)
    file.close
    print("Projects: %s"%len(newProjects))

def getProjects():
    global oldProjects,p_dict
    print("Creating old project data...")
    for pr in p_dict["Projects"]:
        ID = pr["id"]
        NAME = pr["name"]
        TYPE = pr["type"]
        DATES = pr["timeline"]["dates"]
        STATUSA = pr["timeline"]["status"]
        proj = project(ID,TYPE,NAME,STATUSA[len(STATUSA)-1],DATES,STATUSA)
        oldProjects.append(proj)

def getNewProjectsIDs():
    global newProjects
    pList = []
    for proj in newProjects:
        pList.append(proj.id)
    return pList

def mergeProjects():
    print("Merging project data...")
    global date, mergedProjects,newProjects,oldProjects
    mergedProjects = oldProjects.copy()
    IDs = getNewProjectsIDs()
    for mProj in mergedProjects:
        if (mProj.id in IDs):
            mProj.dates.append(newProjects[IDs.index(mProj.id)].dates)
            mProj.statusA.append(newProjects[IDs.index(mProj.id)].statusA)
            IDs.remove(mProj.id)
        else:
            if (mProj.statusA[len(mProj.statusA) - 1] == "Upcoming" or mProj.statusA[len(mProj.statusA) - 1] == "Next Arrival"):
                mProj.dates.append(date)
                mProj.statusA.append("Released")
            elif (mProj.statusA[len(mProj.statusA) - 1] == "In Production" or mProj.statusA[len(mProj.statusA) - 1] == "In Planning"):
                mProj.dates.append(date)
                mProj.statusA.append("Canceled")

    for proj in IDs:
        mergedProjects.append(newProjects[IDs.index(proj)])

def createNewRoadmapObjects():
    print("Creating roadmap from data...")
    global newProjects, newRoadmap, sections
    DATE = date
    NA = []
    UP = []
    PR = []
    PL = []
    for i in newProjects:
        if i.status == sections[0]:
            NA.append(i)
        elif i.status == sections[1]:
            UP.append(i)
        elif i.status == sections[2]:
            PR.append(i)
        elif i.status == sections[3]:
            PL.append(i)

    newRoadmap = roadmap(DATE,NA,UP,PR,PL)

def getRoadmaps():
    print("Creating old roadmap data...")
    global p_dict,oldRoadmaps
    for i in p_dict["Roadmaps"]:
        DATE = p_dict["Roadmaps"].date
        NA = p_dict["Roadmaps"].Projects.NextArrival
        UP = p_dict["Roadmaps"].Projects.Upcoming
        PR = p_dict["Roadmaps"].Projects.InProduction
        PL = p_dict["Roadmaps"].Projects.InPlanning
        nRoadM = roadmap(DATE,NA,UP,PR,PL)
        oldRoadmaps.append(nRoadM)

def mergeRoadmaps():
    global oldRoadmaps,newRoadmap,mergedRoadmaps
    mergedRoadmaps = [newRoadmap]
    if len(oldRoadmaps) > 0:
        mergedRoadmaps.append(oldRoadmaps)

def updateJSON():
    global date,mergedProjects,mergedRoadmaps
    print("Generating new json file...")
    if DEBUG:
        file = open("updatedData-%s.json"%dtNow,"w")
    else:
        file = open("updatedData.json","w")
    file.write("{")
    #Last update
    file.write('"LastUpdate":"%s",'%date)
    
    #Projects
    file.write('"Projects":[')
    for proj in mergedProjects:
        file.write("{")
        file.write('"id":')
        file.write('"%s",'%proj.id)
        file.write('"name":')
        file.write('"%s",'%proj.name)
        file.write('"type":')
        file.write('"%s",'%proj.type)
        file.write('"timeline":')
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
    file.write("],")
    
    #Roadmaps
    file.write('"Roadmaps":[')
    for road in mergedRoadmaps:
        file.write("{")
        file.write('"date":')
        file.write('"%s",'%road.date)
        file.write('"Projects":{')
        file.write('"NextArrival":[')
        for na in road.na:
            file.write("{")
            file.write('"id":')
            file.write('"%s",'%na.id)
            file.write('"name":')
            file.write('"%s",'%na.name)
            file.write('"type":')
            file.write('"%s"'%na.type)
            file.write("}")
            if na != road.na[len(road.na)-1]:
                file.write(",")
        file.write("],")
        file.write('"Upcoming":[')
        for up in road.up:
            file.write("{")
            file.write('"id":')
            file.write('"%s",'%up.id)
            file.write('"name":')
            file.write('"%s",'%up.name)
            file.write('"type":')
            file.write('"%s"'%up.type)
            file.write("}")
            if up != road.up[len(road.up)-1]:
                file.write(",")
        file.write("],")
        file.write('"InProduction":[')
        for pr in road.pr:
            file.write("{")
            file.write('"id":')
            file.write('"%s",'%pr.id)
            file.write('"name":')
            file.write('"%s",'%pr.name)
            file.write('"type":')
            file.write('"%s"'%pr.type)
            file.write("}")
            if pr != road.pr[len(road.pr)-1]:
                file.write(",")
        file.write("],")
        file.write('"InPlanning":[')
        for pl in road.pl:
            file.write("{")
            file.write('"id":')
            file.write('"%s",'%pl.id)
            file.write('"name":')
            file.write('"%s",'%pl.name)
            file.write('"type":')
            file.write('"%s"'%pl.type)
            file.write("}")
            if pl != road.pl[len(road.pl)-1]:
                file.write(",")
        file.write("]")
        file.write("}}")
        if road != mergedRoadmaps[len(mergedRoadmaps)-1]:
            file.write(",")
    file.write("]")    
    file.write("}")
    file.close

def updatedToCurrentJSON():
    if not DEBUG:
        print("Saving last projects file...")
        os.remove("data.json")
        os.rename("updatedData.json","data.json")
        copyfile("data.json","data%s.json"%(date.replace("/","")))
             
def main():
    askDate()
    #JSONtoDict()
    getRoadmapString()            
    createNewProjectsObjects()
    #getProjects()
    mergeProjects()
    createNewRoadmapObjects()
    #getRoadmaps()
    mergeRoadmaps()
    updateJSON()
    updatedToCurrentJSON()
    
try:
    if __name__ == "__main__":
        main()
except KeyboardInterrupt:
    print("Exiting program")
    exit()

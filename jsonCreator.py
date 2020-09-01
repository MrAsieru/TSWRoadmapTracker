#Python 3.8.3
import re
import json
import urllib.request
import os
from datetime import datetime as dt
from shutil import copyfile

DEBUG = False
LOCAL_JSON = True
URL = "https://raw.githubusercontent.com/MrAsieru/TSWRoadmapTracker/master/data.json"

typesCodes = []
statusCodes = []
regionCodes = []
tractionCodes = []
addOnCodes = []
yearsCodes = []

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
    global p_dict
    print("Downloading old data...")
    if not(LOCAL_JSON):
        f = urllib.request.urlopen(URL) #Download json data from GitHub
        fD = "" #For decoded data
        for line in f:
            fD = fD + line.decode("utf-8")
        p_dict = json.loads(fD)#Dictionary from json data
    else:
        with open("dataTmp.json") as json_file:
            p_dict = json.load(json_file)

def getCodes():
    global typesCodes,statusCodes,regionCodes,tractionCodes,addOnCodes,yearsCodes
    typesCodes = p_dict["Codes"]["types"]
    statusCodes = p_dict["Codes"]["status"]
    regionCodes = p_dict["Codes"]["regions"]
    tractionCodes = p_dict["Codes"]["tractions"]
    addOnCodes = p_dict["Codes"]["addOnTypes"]
    yearsCodes = p_dict["Codes"]["years"]

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
        if (i in statusCodes): #Check if line is section title
            status += 1
        elif (i[0] != "["): #Check if new status
            raise Exception("Posible new status found: %s"%i)
        else:
            TYPE = re.search("\[.*\]",i).group(0).replace("[","").replace("]","")
            if not (TYPE in typesCodes):
                raise Exception("Posible new type found: %s"%TYPE)
            try:
                ID = re.search("[A-Z]{3}-[LR][1-7] (0[1-9]|[1-9][0-9])",i).group(0)
                NAME = re.search("- .*$",i).group(0).replace("- ","")
            except AttributeError:
                ID = re.search("] .*$",i).group(0).replace("] ","")
                NAME = ""
            STATUS = statusCodes[status - 1]
            newProj = project(ID,TYPE,NAME,STATUS,[date],[STATUS])
            newProjects.append(newProj)
    file.close
    print("Projects: %s"%len(newProjects))

def checkIdCodes():
    global newProjects,regionCodes,tractionCodes,addOnCodes,yearsCodes
    for p in newProjects:
        if re.match("[A-Z]{3}-[LR][1-7] (0[1-9]|[1-9][0-9])",p.id):
            if not(p.id[0] in regionCodes.keys()):
                raise Exception("Posible new region found: %s"%p.id)
            if not(p.id[1] in tractionCodes.keys() or p.id[2] in tractionCodes.keys()):
                raise Exception("Posible new traction found: %s"%p.id)
            if not(p.id[4] in addOnCodes.keys()):
                raise Exception("Posible new Add-On type found: %s"%p.id)
            if not(p.id[5] in yearsCodes.keys()):
                raise Exception("Posible new years found: %s"%p.id)
        else:
            print("ID with no id style detected: %s"%p.id)

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
    remainingIDs = IDs.copy()
    for mProj in mergedProjects:
        if (mProj.id in IDs):
            mProj.dates.extend(newProjects[IDs.index(mProj.id)].dates)
            mProj.statusA.extend(newProjects[IDs.index(mProj.id)].statusA)
            remainingIDs.remove(mProj.id)
        else:
            print("%s is not appearing, last status %s: [R/C]"%(mProj.id,mProj.statusA[len(mProj.statusA) - 1]))
            uInput = input().upper()
            
            if (uInput == "R"):
                mProj.dates.append(date)
                mProj.statusA.append("Released")
                print("%s -> Released"%mProj.id)
            elif (uInput == "C"):
                mProj.dates.append(date)
                mProj.statusA.append("Canceled")
                print("%s -> Canceled"%mProj.id)

    for proj in remainingIDs:
        mergedProjects.append(newProjects[IDs.index(proj)])

def createNewRoadmapObjects():
    print("Creating roadmap from data...")
    global newProjects, newRoadmap, statusCodes
    DATE = date
    NA = []
    UP = []
    PR = []
    PL = []
    for i in newProjects:
        if i.status == statusCodes[0]:
            NA.append(i)
        elif i.status == statusCodes[1]:
            UP.append(i)
        elif i.status == statusCodes[2]:
            PR.append(i)
        elif i.status == statusCodes[3]:
            PL.append(i)

    newRoadmap = roadmap(DATE,NA,UP,PR,PL)

def getRoadmaps():
    print("Creating old roadmap data...")
    global p_dict,oldRoadmaps
    for i in p_dict["Roadmaps"]:
        DATE = i["date"]
        NA = []
        for j in i["Projects"]["NextArrival"]:
            proj = project(j["id"],j["type"],j["name"],None,None,None)
            NA.append(proj)
        UP = []
        for j in i["Projects"]["Upcoming"]:
            proj = project(j["id"],j["type"],j["name"],None,None,None)
            UP.append(proj)
        PR = []
        for j in i["Projects"]["InProduction"]:
            proj = project(j["id"],j["type"],j["name"],None,None,None)
            PR.append(proj)
        PL = []
        for j in i["Projects"]["InPlanning"]:
            proj = project(j["id"],j["type"],j["name"],None,None,None)
            PL.append(proj)
        nRoadM = roadmap(DATE,NA,UP,PR,PL)
        oldRoadmaps.append(nRoadM)

def mergeRoadmaps():
    global oldRoadmaps,newRoadmap,mergedRoadmaps
    mergedRoadmaps = [newRoadmap]
    if len(oldRoadmaps) > 0:
        mergedRoadmaps.extend(oldRoadmaps)

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
    tmpStr1 = ""
    for proj in mergedProjects:
        tmpStr1 = tmpStr1+"{"
        tmpStr1 = tmpStr1+'"id":'
        tmpStr1 = tmpStr1+'"%s",'%proj.id
        tmpStr1 = tmpStr1+'"name":'
        tmpStr1 = tmpStr1+'"%s",'%proj.name
        tmpStr1 = tmpStr1+'"type":'
        tmpStr1 = tmpStr1+'"%s",'%proj.type
        tmpStr1 = tmpStr1+'"timeline":'
        tmpStr1 = tmpStr1+"{"
        tmpStr1 = tmpStr1+'"dates":['
        tmpStr2 = ""
        for date in proj.dates:
            tmpStr2 = tmpStr2+'"%s"'%date
            tmpStr2 = tmpStr2+","
        tmpStr2 = tmpStr2[:-1]
        tmpStr1 = tmpStr1+tmpStr2
        tmpStr1 = tmpStr1+'],"status":['
        tmpStr2 = ""
        for status in proj.statusA:
            tmpStr2 = tmpStr2+'"%s"'%status
            tmpStr2 = tmpStr2+","
        tmpStr2 = tmpStr2[:-1]
        tmpStr1 = tmpStr1+tmpStr2
        tmpStr1 = tmpStr1+"]}}"
        tmpStr1 = tmpStr1+","
    tmpStr1 = tmpStr1[:-1]
    file.write(tmpStr1)
    file.write("],")
    
    #Roadmaps
    file.write('"Roadmaps":[')
    tmpStr1 = ""
    for road in mergedRoadmaps:
        tmpStr1 = tmpStr1+"{"
        tmpStr1 = tmpStr1+'"date":'
        tmpStr1 = tmpStr1+'"%s",'%road.date
        tmpStr1 = tmpStr1+'"Projects":{'
        tmpStr1 = tmpStr1+'"NextArrival":['
        tmpStr2 = ""
        for na in road.na:
            tmpStr2 = tmpStr2+"{"
            tmpStr2 = tmpStr2+'"id":'
            tmpStr2 = tmpStr2+'"%s",'%na.id
            tmpStr2 = tmpStr2+'"name":'
            tmpStr2 = tmpStr2+'"%s",'%na.name
            tmpStr2 = tmpStr2+'"type":'
            tmpStr2 = tmpStr2+'"%s"'%na.type
            tmpStr2 = tmpStr2+"}"
            tmpStr2 = tmpStr2+","
        tmpStr2 = tmpStr2[:-1]
        tmpStr1 = tmpStr1+tmpStr2
        tmpStr1 = tmpStr1+"],"
        tmpStr1 = tmpStr1+'"Upcoming":['
        tmpStr2 = ""
        for up in road.up:
            tmpStr2 = tmpStr2+"{"
            tmpStr2 = tmpStr2+'"id":'
            tmpStr2 = tmpStr2+'"%s",'%up.id
            tmpStr2 = tmpStr2+'"name":'
            tmpStr2 = tmpStr2+'"%s",'%up.name
            tmpStr2 = tmpStr2+'"type":'
            tmpStr2 = tmpStr2+'"%s"'%up.type
            tmpStr2 = tmpStr2+"}"
            tmpStr2 = tmpStr2+","
        tmpStr2 = tmpStr2[:-1]
        tmpStr1 = tmpStr1+tmpStr2
        tmpStr1 = tmpStr1+"],"
        tmpStr1 = tmpStr1+'"InProduction":['
        tmpStr2 = ""
        for pr in road.pr:
            tmpStr2 = tmpStr2+"{"
            tmpStr2 = tmpStr2+'"id":'
            tmpStr2 = tmpStr2+'"%s",'%pr.id
            tmpStr2 = tmpStr2+'"name":'
            tmpStr2 = tmpStr2+'"%s",'%pr.name
            tmpStr2 = tmpStr2+'"type":'
            tmpStr2 = tmpStr2+'"%s"'%pr.type
            tmpStr2 = tmpStr2+"}"
            tmpStr2 = tmpStr2+","
        tmpStr2 = tmpStr2[:-1]
        tmpStr1 = tmpStr1+tmpStr2
        tmpStr1 = tmpStr1+"],"
        tmpStr1 = tmpStr1+'"InPlanning":['
        tmpStr2 = ""
        for pl in road.pl:
            tmpStr2 = tmpStr2+"{"
            tmpStr2 = tmpStr2+'"id":'
            tmpStr2 = tmpStr2+'"%s",'%pl.id
            tmpStr2 = tmpStr2+'"name":'
            tmpStr2 = tmpStr2+'"%s",'%pl.name
            tmpStr2 = tmpStr2+'"type":'
            tmpStr2 = tmpStr2+'"%s"'%pl.type
            tmpStr2 = tmpStr2+"}"
            tmpStr2 = tmpStr2+","
        tmpStr2 = tmpStr2[:-1]
        tmpStr1 = tmpStr1+tmpStr2
        tmpStr1 = tmpStr1+"]"
        tmpStr1 = tmpStr1+"}}"
        tmpStr1 = tmpStr1+","
    tmpStr1 = tmpStr1[:-1]
    file.write(tmpStr1)
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
    JSONtoDict()
    getCodes()
    getRoadmapString()            
    createNewProjectsObjects()
    checkIdCodes()
    getProjects()
    mergeProjects()
    createNewRoadmapObjects()
    getRoadmaps()
    mergeRoadmaps()
    updateJSON()
    updatedToCurrentJSON()
    
try:
    if __name__ == "__main__":
        main()
except KeyboardInterrupt:
    print("Exiting program")
    exit()

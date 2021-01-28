# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2021/01/27 22:58:35
@Author  :   Geralt 
@Version :   1.0
@Contact :   superj0529@gmail.com
'''
import datetime
import sys
import re
from getHTML import getHTML

from ics import Calendar, Event
from lxml import etree

class UTC(datetime.tzinfo):
    """UTC"""
    def __init__(self,offset = 0):
        self._offset = offset

    def utcoffset(self, dt):
        return datetime.timedelta(hours=self._offset)

    def tzname(self, dt):
        return "UTC +%s" % self._offset

    def dst(self, dt):
        return datetime.timedelta(hours=self._offset)

FIRST_DAY = datetime.datetime(year=2021,month=2,day=28,hour=0,minute=0,second=00,tzinfo=UTC(8))

rule = (((8,30),(9,20)),     #0
        ((9,30),(10,20)),    #1
        ((10,40),(11,30)),    #2
        ((11,40),(12,30)),    #3
        ((14,0),(14,50)),    #4
        ((15,0),(15,50)),    #5
        ((16,10),(17,0)),    #6
        ((17,10),(18,0)),    #7
        ((18,30),(19,20)),    #8
        ((19,30),(20,20)),    #9
        ((20,30),(21,20)),    #10
        ((21,30),(22,20)))   #11

def getinfo(event:(etree._Element)):
    attribs = dict(event.attrib)
    id = int(attribs['id'].strip('TD'))
    rowspan = int(attribs['rowspan']) # 持续时间
    day = int(id/120) # 0-6 : Mon - Sun
    c = int((id%120)/10) # 0-11 : 1rt - 12th 
    return(day,c,rowspan)

def defaultValue(ans:list,default:str,index:int)->str:
    return ans[index] if index<len(ans) else default



def getEvent(calendar:Calendar,event:(etree._Element)):

    
    info = getinfo(event)
    detail = event.xpath("./text()")
    for i in range(0,10,2):
        if i+1 > len(detail):
            break;
        cName = re.compile(r"^([\w ]+)\(")
        cNum = re.compile(r"\(([A-Za-z]+[0-9]+)\)")
        room =  re.compile(r",(\w+)\(")
        hanzi = re.compile(r"\(([\u4e00-\u9fa5]+)\)")
        routine = re.compile(r"([0-9]+-[0-9]+[单|双]*)")
        c_info = {}

        c_info['CourseName'] = defaultValue(cName.findall(detail[i]),"",0)
        c_info['CourseNumber'] = defaultValue(cNum.findall(detail[i]),"",0)
        c_info['Teacher'] = defaultValue(hanzi.findall(detail[i]),"",0)
        c_info['Campus'] = defaultValue(hanzi.findall(detail[i+1]),"浑南校区",0)
        c_info['Room'] = defaultValue(room.findall(detail[i+1]),"",0)
        c_info['Routine'] = defaultValue(routine.findall(detail[i+1]),"",0)

        Rt = c_info['Routine'].strip('单双').split('-')

        wa = int(Rt[0])
        wb = int(Rt[1])
        Rtlist=[]

        if('单' in c_info['Routine']):
            Rtlist = [x for x in range(wa if wa%2!=0 else wa+1 ,wb+1,2)]
        elif('双' in c_info['Routine']):
            Rtlist = [x for x in range(wa if wa%2==0 else wa+1 ,wb+1,2)]
        else:
            Rtlist = [x for x in range(wa ,wb+1,1)]

        for w in Rtlist:
            courseStartTime = FIRST_DAY+datetime.timedelta(
                days=(w-1)*7+(info[0]+1)%7,
                hours=rule[info[1]][0][0],
                minutes=rule[info[1]][0][1])
            courseEndTime = FIRST_DAY+datetime.timedelta(
                days=(w-1)*7+(info[0]+1)%7,
                hours=rule[info[1]+info[2]-1][1][0],
                minutes=rule[info[1]+info[2]-1][1][1])

            calEvent = Event(
                name=c_info['CourseName'],
                begin=courseStartTime,
                end=courseEndTime,
                location=c_info['Room']+' '+c_info['Campus'],
                description=c_info['CourseName']+'：'+c_info['CourseNumber']+'  '+'Teacher：'
                +c_info['Teacher']
            )
            calendar.events.add(calEvent)

            

            # add_event(calendar,
            #     SUMMARY=c_info['CourseName'],
            #     DTSTART=courseStartTime,
            #     DTEND=courseEndTime,
            #     DESCRIPTION=c_info['CourseName']+' : '+c_info['CourseNumber']+'\n'+'Teacher: '
            #     +c_info['Teacher']+'\n'+'addr: '+ c_info['Campus']+' '+c_info['Room'],
            #     LOCATION= c_info['Campus']+' '+c_info['Room'])



def makeEvent(calendar:Calendar,html):
    root = etree.HTML(html)
    script = root.xpath('//*[@id="ExportA"]/script')
    index = re.finditer("var teachers =",script[0].text)
    cindex = []
    for i in index:
        cindex.append(i.span())
    cindex.append((-1,-1))
    courses = [script[0].text[cindex[i][0]:cindex[i+1][0]] for i in range(len(cindex)-1)]

    teacherName = re.compile(r"name:\"([\u4e00-\u9fa5]+)\",lab")
    teacherID = re.compile(r"\[\{id:(\d+),name")
    activity = re.compile(r"activity = new TaskActivity\(([\s\S]+)\);")
    week = re.compile(r"index =(\d+)\*unitCount\+\d+;") #index =3*unitCount+5;
    classNumber = re.compile(r"index =\d+\*unitCount\+(\d+);") #index =3*unitCount+5;

    for course in courses:
        info = {}
        info['teacherName'] = teacherName.findall(course)[0]
        info['teacherID'] = teacherID.findall(course)[0]
        activity_ = activity.findall(course)[0].split(',')
        info['courseName'] = activity_[5]
        info['courseLoc'] = activity_[7]
        onehot = activity_[8].strip('"')
        routine = []
        for w in range(len(onehot)):
            if(onehot[w]=='1'):
                routine.append(w)
        weekday = week.findall(course)
        classNum = classNumber.findall(course)

        for w in routine:
            for i in range(len(weekday)):
                courseStartTime = FIRST_DAY+datetime.timedelta(
                    days=(w-1)*7+(int(weekday[i])+1)%7,
                    hours=rule[int(classNum[i])][0][0],
                    minutes=rule[int(classNum[i])][0][1])
                courseEndTime = FIRST_DAY+datetime.timedelta(
                    days=(w-1)*7+(int(weekday[i])+1)%7,
                    hours=rule[int(classNum[i])][1][0],
                    minutes=rule[int(classNum[i])][1][1])
                calEvent = Event(
                    name=info['courseName'],
                    begin=courseStartTime,
                    end=courseEndTime,
                    location=info['courseLoc'],
                    description=info['courseName']+'  '+'Teacher：'
                    +info['teacherName']
                )
                calendar.events.add(calEvent)




    

if __name__ == "__main__":


    html = getHTML(sys.argv[1],sys.argv[2])
    mycal = Calendar()
    #htmlf=open(sys.argv[1],'r',encoding="utf-8")
    #html=htmlf.read() 

    #root = etree.HTML(html)  
    #tds = root.xpath('//td[contains(@id,"TD")]')

    # for item in tds:
    #     content = dict(item.attrib)
    #     if 'title' in content.keys():
    #         getEvent(mycal,item)
    makeEvent(mycal,html)

    with open('my.ics', 'w', encoding='utf-8') as my_file:
        my_file.writelines(mycal)
    
from ical import *
from lxml import etree
import re

FIRST_DAY = datetime.datetime(year=2021,month=2,day=28,hour=0,minute=0,second=00)

rule = [((8,30),(9,20)),     #0
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
        ((21,30),(22,20))]   #11

def getinfo(event:(etree._Element)):
    attribs = dict(event.attrib)
    id = int(attribs['id'].strip('TD'))
    rowspan = int(attribs['rowspan']) # 持续时间
    day = id/120 # 0-6 : Mon - Sun
    c = (id%120)/10 # 0-11 : 1rt - 12th 
    return(day,c,rowspan)

def makeEvent(calendar:Calendar,event:(etree._Element)):

    attribs = dict(event.attrib)
    info = getinfo(event)
    detail = event.xpath("./text()")
    for i in range(0,10,2):
        if i+1 > len(detail):
            break;
        cName = re.compile(r"^([\w ]+)\(")
        cNum = re.compile(r"\(([A-Za-z]+[0-9]+)\)")
        room =  re.compile(r",(\w+)\(")
        hanzi = re.compile(r"\(([\w ]+)\)")
        routine = re.compile(r"\(([\w\S]+),")
        c_info = {}

        c_info['CourseName'] = cName.findall(detail[i])[0]
        c_info['CourseNumber'] = cNum.findall(detail[i])[0]
        c_info['Teacher'] = hanzi.findall(detail[i])[1]
        c_info['Campus'] = hanzi.findall(detail[i+1])[0]
        c_info['Room'] = room.findall(detail[i+1])[0]
        c_info['Routine'] = routine.findall(detail[i+1])[0]

        Rt = c_info['Routine'].strip('单双').split('-')

        wa = int(Rt[0])
        wb = int(Rt[1])
        Rtlist=[]

        if('单' in c_info['Routine']):
            Rtlist = [x for x in range(wa if wa%2!=0 else wa+1 ,wb+1,2)]
        elif('双' in c_info['Routine']):
            Rtlist = [x for x in range(wa if wa%2==0 else wa+1 ,wb+1,2)]
        else:
            Rtlist = [x for x in range(wa ,wb+1,2)]

        for w in Rtlist:
            add_event(calendar,
                SUMMARY=c_info['CourseName'],
                DTSTART=datetime.datetime(year=2019,month=2,day=19,hour=21,minute=21,second=00),
                DTEND=datetime.datetime(year=2019,month=2,day=19,hour=21,minute=30,second=00),
                DESCRIPTION=c_info['CourseName']+' : '+c_info['CourseNumber']+'\n'+'Teacher: '
                +c_info['Teacher']+'\n'+'addr: '+ c_info['Campus']+' '+c_info['Room'],
                LOCATION= c_info['Campus']+' '+c_info['Room'])


    pass

if __name__ == "__main__":

    htmlf=open('ct.html','r',encoding="utf-8")
    html=htmlf.read() 

    root = etree.HTML(html)  
    tds = root.xpath('//td[contains(@id,"TD")]')

    mycal = Calendar(calendar_name='2020春季')

    for item in tds:
        content = dict(item.attrib)
        if 'title' in content.keys():
            makeEvent(mycal,item)
        


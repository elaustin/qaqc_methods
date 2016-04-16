#!/usr/bin/python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"Fetch Dylos averages from KairosDB"

import StringIO, pycurl, json, csv, sys, re
from datetime import datetime
from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
# from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart


##Replace these vars:
CACERT = "C:Users\Admin\Desktop\cacert4.pem"
log = "C:\Users\Admin\Desktop\DHM_log.txt"
##

#Global vars
URL = "https://replicant.deohs.washington.edu/api/v1/datapoints/query"
AUTH = "query:treelimberice7"
DYLOS_UNITS = ["Dylos2", "Dylos23", "Dylos24", "Dylos25", "Dylos26", "Dylos27", "Dylos28", "Dylos29", "Dylos30", "Dylos31", "Dylos32", "Dylos33", "Dylos34", "Dylos35", "Dylos36", "Dylos37", "Dylos38", "Dylos39", "Dylos40", "Dylos41"]
dylos_names = ["Dylos2 - Niland", "Dylos23 - Ocotillo", "Dylos24 - Calexico Housing", "Dylos25 - Brawley High School", "Dylos26 - Hidalgo", "Dylos27 - Heber", "Dylos28 - CARB Calexico", "Dylos29 - CCV", "Dylos30 - Seeley", "Dylos31 - Frank Wright", "Dylos32 - Kennedy", "Dylos33 - Westmorland", "Dylos34 - Brawley Residence", "Dylos35 - Meadows", "Dylos36 - IID", "Dylos37 - Calipatria", "Dylos38 - Not Installed", "Dylos39 - T.L. Wagonner", "Dylos40 - Alvarez Tax Service", "Dylos41 - El Centro Wilson"]
MONITORS = []
SMTPserver = 'smtp.mail.com'
sender =     'Kairos_Emailer@mail.com'
destination = ['gncarvlin@gmail.com','eseto@uw.edu','jshirai@uw.edu','humberto@ccvhealth.org']
USERNAME = "Kairos_Emailer@mail.com"
PASSWORD = ""
text_subtype = 'plain'  # typical values for text_subtype are plain, html, xml
subject="Kairos Update"


#Functions
def prep_query(u_name):
    "This prepares a data structure to send in JSON format"
    #For health query
    query_data = {"start_relative": {"value": 1, "unit": "days"}, "metrics" : [{"name": u_name, "tags": {}, "aggregators":[{"name":"count", "align_sampling":"false","sampling":{"value":1,"unit":"years"}}]},{"name": u_name, "tags": {"Bin":["bin1"]}, "aggregators":[{"name":"min", "align_sampling":"false","sampling":{"value":1,"unit":"days"}}]}]}
    return query_data

def send_query(db_query):
    "This sends out individual queries using pycurl which calls libcurl"
    buf = StringIO.StringIO()
    req = pycurl.Curl()
    req.setopt(req.URL, URL)
    req.setopt(req.CAINFO, CACERT)
    req.setopt(req.USERPWD, AUTH)
    req.setopt(req.POSTFIELDS, json.dumps(db_query))
    req.setopt(req.WRITEDATA, buf)
    req.setopt(req.POST, 1L)
    req.perform()
    req.close()
    h = json.loads(buf.getvalue())["queries"][0]["sample_size"]
    if (json.loads(buf.getvalue())["queries"][1]["sample_size"]!=0):
        j = json.loads(buf.getvalue())["queries"][1]["results"][0]["values"][0][1]
    else:
        j = -1
    return [h,j]

#Loop through each Dylos unit
count = 0
for dylos in DYLOS_UNITS:
    # Get number of data points uploaded in last 24 hours
    mInfo = send_query(prep_query(dylos))
    health = mInfo[0]
    zero = mInfo[1]
    health_percent = round((100 * health)/1728.0,3)
    if (int(health_percent)>=95):
        health_color = "#08BF0B" #green
    elif ((int(health_percent)>=75) and (int(health_percent) <95)):
        health_color = "#E8A617" #orange
    else:
        health_color = "#DE3333" #red
    if (re.search("Not Installed", dylos_names[count]) or re.search("old name", dylos_names[count])):
        health_color = "#A6A6A6" #grey
    #Test if Dylos reading 0s
    if (zero==0):
        dylosError = True
    else:
        dylosError = False
    MONITORS.append([health_percent,health_color,dylosError])
    count = count + 1

#Send the email
today = datetime.now().strftime("%m/%d/%y")

content="""Dylos Health\n"""
for i in range(0,len(dylos_names)):
    if (MONITORS[i][2]==True):
        line = "%s: %s%% uploaded. Dylos needs maintenance!\n" % (dylos_names[i],MONITORS[i][0])
    else:
        line = "%s: %s%% uploaded\n" % (dylos_names[i],MONITORS[i][0])
    content += line

html_content="""\
<html>
    <head></head>
    <body>
        <p><span style="font-size:medium;">Dylos Health for %s</span><br><br>""" % today
for i in range(0,len(dylos_names)):
    if (MONITORS[i][2]==True):
        line = "<span style=\"color:#DE3333\">%s: %s%% uploaded. Dylos needs maintenance!</span><br>" % (dylos_names[i],MONITORS[i][0])
    else:
        line = "<span style=\"color:%s\">%s: %s%% uploaded</span><br>" % (MONITORS[i][1],dylos_names[i],MONITORS[i][0])
    html_content += line
html_content+="<br>Green is >=95% upload, Orange is >=75% and <95%, Red is <75%, Grey means the unit is not installed or the unit name is deprecated. \"Dylos needs maintenance!\" means that the Dylos is reading all 0s and should be cleaned.</p></body></html>"

try:
    msg = MIMEMultipart('alternative')
    msg['Subject']=       subject
    msg['From']   = sender # some SMTP servers will do this automatically, not all
    msg['To'] = ','.join(destination)
    msg.attach(MIMEText(content, 'plain'))
    msg.attach(MIMEText(html_content,'html'))

    conn = SMTP(SMTPserver)
    conn.set_debuglevel(False)
    conn.login(USERNAME, PASSWORD)
    try:
        conn.sendmail(sender, destination, msg.as_string())
    finally:
        conn.close()

except Exception, exc:
    with open(log, "a") as f:
        line = "today Error: %s\n" % str(exc)
        f.write(line)
    sys.exit( "mail failed; %s" % str(exc) )

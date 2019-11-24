
import mechanize
from bs4 import BeautifulSoup
from http.cookiejar import CookieJar

from datetime import datetime
from datetime import timedelta
import re
import csv
import time

cj = CookieJar()
br = mechanize.Browser()
br.set_cookiejar(cj)
br.open("http://groupspaces.com/ThamesGreenBottles/manage/events/?past")

br.select_form(nr=0)
br.form['username'] = "ChangeMe"
br.form['password'] = "ChangeMe"
br.submit()

d = datetime.today()
lastyear = d - timedelta(days=365)
print (lastyear)
print(d.strftime("%A"))

soup = BeautifulSoup(br.response().read(), "html.parser")
soup.prettify()

#dump the html that contains the historic events.
#events = soup.find_all(id ='events')
#for each in events :
#   print(each)

f = open('crewlist.csv', 'w')


# this gets the date, event and the href link so we can drill down to get the attendees.
items = soup.find_all('div', attrs={'class':'item'})
for i in items :
    x = i.find('span', attrs={'class':'date'})
    y = i.find('h4')
    z = y.find('a')
    a = i.find('a', attrs={'class':'button'})
    #print(x.contents[0] + ", "+z.contents[0])

    #for some reason class : button filters out only the first button. cant be arsed working how to get to the registrations button
    #so hacking the url to point to registrations instead. simples.
    registrations = a['href'].replace("edit","registrations")

    #reformat date so spreadsheets can deal with it without further faff.
    dateStr=re.sub(r"(?<=\d)(st|nd|rd|th)\b", '', x.contents[0])
    # Sometimes "Today" is provided as the day of week, so replace "Today" with day of week or date conversion fails.
    dateStr = dateStr.replace("Today", d.strftime("%A"))

    date_object = datetime.strptime(dateStr, '%A, %d %B %Y')

    # filter out on date.... (this years data or all data older than 1 year
    #if date_object <= lastyear:

    if date_object >= lastyear:
      f.write(str(date_object.strftime('%d/%m/%Y'))+ " "+str(z.contents[0])+'\n')
      print (date_object.strftime('%d/%m/%Y')+ " "+z.contents[0])
      #print(registrations)
      regs = br.open(registrations)
      regsoup = BeautifulSoup(br.response().read(), "html.parser")


      crew = regsoup.find_all('div', attrs={'class':'dataGridNavigator_b'})
      for c in crew :
        peeps = c.find_all('div',attrs={'class':'EmailAddressWrapper'})
        for p in peeps :
            e = p.find('a')
            print(e.contents[0])
            f.write(str(e.contents[0])+'\n')
        # delay prevents GS thinking it's under a DDoS attack - it blacklists your ip addy if this isn't done.
        time.sleep(2)
    else :
        print("ignoring "+ dateStr)



f.flush()

f.close()


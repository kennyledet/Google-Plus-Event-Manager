"""
Copyright 2013 Kendrick Ledet

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from splinter import Browser
from time     import sleep
from dateutil import parser as dtparser
import argparse, json

class GPlusEventManager(object):
    def __init__(self, email, passwd):
        self.email  = email
        self.passwd = passwd
        self.br     = Browser('chrome')
        # to dynamically load jQuery into the HTML head
        self.loadjq = """var head = document.getElementsByTagName('head')[0];
                   var script  = document.createElement('script');
                   script.type = 'text/javascript';
                   script.src  = '//ajax.googleapis.com/ajax/libs/jquery/1.10.1/jquery.min.js';
                   head.appendChild(script);"""

        self.login()


    def create(self, title, desc, date, time):
        """ Create a new Google Plus event """
        self.br.find_by_css('div[guidedhelpid="events_create_event_button"]')[0].click()

        self.br.find_by_css('input[placeholder="Event title"]').fill(title)

        self.br.find_by_css('input[class="g-A-G T4 lUa"]').click()
        self.br.execute_script('document.body.getElementsByClassName("g-A-G T4 lUa")[0].value = ""')
        self.br.find_by_css('input[class="g-A-G T4 lUa"]').type('{}\t'.format(date))

        self.br.execute_script(self.loadjq)
        loaded = False
        while not loaded:
            try:
                self.br.execute_script('$(".EKa")[0].value = ""')
            except Exception, e:
                pass
            else:
                loaded = True

        self.br.find_by_css('input[class="g-A-G T4 EKa"]')[0].type('{}'.format(time))

        self.br.execute_script('document.body.getElementsByClassName("yd editable")[1].innerHTML = "{}"'.format(desc))

        self.br.find_by_css('div[guidedhelpid="sharebutton"]').click()
        self.br.find_by_css('input[class="i-j-h-G-G"]').type('Public\t')
        self.br.find_by_css('div[guidedhelpid="sharebutton"]').click()

        sleep(4)  # wait for double page load
        return self.br.url  # return event url


    def update(self, id, title=None, desc=None, date=None, time=None):
        """ Update a Google Plus event """
        """ TODO: Refactor most of this into create method to reduce redundancy """
        self.br.visit(id)
        # click dropdown to see edit event link
        self.br.find_by_xpath('//*[@id="contentPane"]/div/div/div/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div[2]/div/div[1]').click()
        self.br.find_by_xpath('//*[@id=":o"]/div').click()

        if title:
            self.br.find_by_css('input[placeholder="Event title"]').fill(title)
        if date:
            self.br.find_by_css('input[class="g-A-G T4 lUa"]').click()
            self.br.execute_script('document.body.getElementsByClassName("g-A-G T4 lUa")[0].value = ""')
            self.br.find_by_css('input[class="g-A-G T4 lUa"]').type('{}\t'.format(date))
        if time:
            self.br.execute_script(self.loadjq)
            loaded = False
            while not loaded:
                try:
                    self.br.execute_script('$(".EKa")[0].value = ""')
                except Exception, e:
                    pass
                else:
                    loaded = True

            self.br.find_by_css('input[class="g-A-G T4 EKa"]')[0].type('{}'.format(time))     
        if desc:
            self.br.execute_script('document.body.getElementsByClassName("yd editable")[1].innerHTML = "{}"'.format(desc))


        self.br.find_by_css('div[guidedhelpid="sharebutton"]').click()


    def details(self, id):
        """ Read details of a Google event """
        self.br.visit(id)
        details = {}
        details['title'] = self.br.find_by_css('div[class="Iba"]').text.split('\n')[0]
        details['desc']  = self.br.find_by_css('div[class="T7BsYe"]').text

        #print details
        return details

    def login(self):
        self.br.visit('https://plus.google.com/u/0/events')
        self.br.fill('Email', self.email)
        self.br.fill('Passwd', self.passwd)
        self.br.find_by_name('signIn').click()

# Load config
with open('config.json', 'r') as config:
    settings = json.loads(config.read())

gpem = GPlusEventManager(settings['username'], settings['password'])

def cli_parse():
    '''Parse command-line arguments'''
    options = {'title': None, 'desc': None, 'date': None, 'time': None, 'id': None}
    parser = argparse.ArgumentParser()
    parser.add_argument("action",  help="create to create a new event\nupdate to update an event\ndetails to get event info")
    parser.add_argument("--title", help="event title")
    parser.add_argument("--date",  help="event date")
    parser.add_argument("--id",    help="event id")
    parser.add_argument("--description", help="txt file with description")
    args = parser.parse_args()

    if args.title:
        options['title'] = args.title

    if args.description:
        with open(args.description, 'r') as description:
            options['desc'] = description.read()

    if args.date:
        options['date'] = dtparser.parse(args.date).strftime('%Y-%m-%d')
        options['time'] = dtparser.parse(args.date).strftime('%I:%M %p')

    if args.id:
        options['id'] = args.id

    options['action'] = args.action

    return options

options = cli_parse()

if options['action'] == 'create':
    id = gpem.create(options['title'], options['desc'], options['date'], options['time'])

    print 'Created: {}'.format(id)
elif options['action'] == 'update':
    gpem.update(options['id'], options['title'], options['desc'], options['date'], options['time'])

    print 'Event {} updated'.format(options['id'])
elif options['action'] == 'details':
    details = gpem.details(options['id'])

    print details


"""Testing without CLI args
event = gpem.create('test', 'test', '2013-09-01', '10:45 PM')
print event
gpem.update(event, title='New title')
sleep(2)
gpem.details(event)
"""
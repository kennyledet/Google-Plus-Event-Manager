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
from dateutil import parser as dtparser
import atexit
import argparse
import json


def load_config():
    with open('config.json', 'r') as config:
        return json.loads(config.read())


def cli_parse():
    '''Parse command-line arguments'''
    options = {'title': None, 'desc': None, 'date': None,
               'time': None, 'id': None}

    parser = argparse.ArgumentParser()
    parser.add_argument("action",  help='''use "create" to create a new event\n
                        "update" to update an event\n"details" to get event info''')  # noqa
    parser.add_argument("--title", help="event title")
    parser.add_argument("--date",  help="event date")
    parser.add_argument("--id",    help="event id")
    parser.add_argument("--desc",  help="event description")
    parser.add_argument("--filedesc", help="path to txt file w/ event description",  # noqa
                        type=argparse.FileType('r'))
    parser.add_argument("--otp", help="2-step verification code")
    parser.add_argument("--show", help="1 to display the browser, 0 for invisible virtual display",  # noqa
                        default=0, type=int)

    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        exit(1)

    disp = None
    if not args.show:  # set up invisible virtual display
        from pyvirtualdisplay.smartdisplay import SmartDisplay
        try:
            disp = SmartDisplay(visible=0, bgcolor='black').start()
            atexit.register(disp.stop)
        except:
            if disp:
                disp.stop()
            raise

    if args.title:
        options['title'] = args.title

    if args.desc:
        options['desc'] = args.desc
    elif args.filedesc:
        options['desc'] = args.filedesc.read()

    if args.date:
        options['date'] = dtparser.parse(args.date).strftime('%Y-%m-%d')
        options['time'] = dtparser.parse(args.date).strftime('%I:%M %p')

    if args.id:
        options['id'] = args.id

    if args.otp:
        options['otp'] = args.otp

    options['action'] = args.action

    return options


class GPlusEventManager(object):
    def __init__(self, email, passwd, otp):
        self.email = email
        self.passwd = passwd
        self.br = Browser('firefox')
        atexit.register(self.force_br_quit)
        # To dynamically load jQuery into the HTML head
        self.loadjq = """var head = document.getElementsByTagName('head')[0];
           var script  = document.createElement('script');
           script.type = 'text/javascript';
           script.src  =
                '//ajax.googleapis.com/ajax/libs/jquery/1.10.1/jquery.min.js';
           head.appendChild(script);"""

        self.otp = otp
        self.logged_in = self.login()

    def force_br_quit(self):
        try:
            self.br.quit()
        except:
            pass

    def create(self, title, desc, date, time):
        """ Create a new Google Plus event """
        if not self.logged_in:
            self.br.quit()
            return None

        create_btn = 'div[guidedhelpid="events_create_event_button"]'
        self.br.find_by_css(create_btn)[0].click()

        return self.complete_form(title, desc, date, time, update=False)

    def update(self, id, title=None, desc=None, date=None, time=None):
        """ Update a Google Plus event """
        if not self.logged_in:
            self.br.quit()
            return None

        self.br.visit(id)

        dropdown = 'div[class="A7kfHd q3sPdd"]'
        while self.br.is_element_not_present_by_css(dropdown):
            pass
        self.br.find_by_css(dropdown).click()
        self.br.find_by_xpath('//*[@id=":o"]/div').click()

        return self.complete_form(title, desc, date, time, update=True)

    def complete_form(self, title, desc, date, time, update):
        '''Fill event create/edit form,
           the CSS selectors are valid in both types of form'''

        title_input = 'input[placeholder="Event title"]'
        while self.br.is_element_not_present_by_css(title_input):
            pass
        if title:
            title_placeholder = self.br.find_by_css(title_input)
            title_placeholder.fill(title)
        if date:
            self.br.find_by_css('input[class="g-A-G T4 lUa"]').click()
            rm_date = '''document.body.getElementsByClassName("g-A-G T4 lUa")
                         [0].value = ""'''
            self.br.execute_script(rm_date)
            date_field = 'input[class="g-A-G T4 lUa"]'
            self.br.find_by_css(date_field).type('{}\t'.format(date))
        if time:
            self.br.execute_script(self.loadjq)
            loaded = False
            rm_time = '$(".EKa")[0].value = ""'
            while not loaded:
                try:
                    self.br.execute_script(rm_time)
                except Exception, e:
                    pass
                else:
                    loaded = True

            time_field = 'input[class="g-A-G T4 EKa"]'
            self.br.find_by_css(time_field)[0].type('{}'.format(time))
        if desc:
            set_desc = '''document.body.getElementsByClassName("yd editable")
                         [1].innerHTML = "{}"'''.format(desc)
            self.br.execute_script(set_desc)

        invite_btn = self.br.find_by_css('div[guidedhelpid="sharebutton"]')
        invite_inp = self.br.find_by_css('input[class="i-j-h-G-G"]')

        invite_btn.click()
        if not update:  # If new entry, invite Public group by default
            invite_inp.click()
            invite_inp.type('Public\n')
            invite_btn.click()
            while not self.br.is_text_present('Going ('):
                pass  # wait on page load for new event

        url = self.br.url
        self.br.quit()
        return url  # return event url

    def details(self, id):
        """Read details of a Google event"""
        if not self.logged_in:
            return None

        self.br.visit(id)

        title = self.br.find_by_css('div[class="Iba"]')
        desc = self.br.find_by_css('div[class="T7BsYe"]')

        details['title'] = title.text.split('\n')[0]
        details['desc'] = desc.text

        guest_list = self.br.find_by_css('a[href^="./"]')[2:]
        details['guests'] = [{guest.text: guest['href']}
                             for guest in guest_list]

        return details

    def login(self):
        url = 'https://plus.google.com/u/0/events'

        self.br.visit(url)
        self.br.fill('Email', self.email)
        self.br.fill('Passwd', self.passwd)
        try:
            self.br.find_by_name('signIn').click()
            while self.br.is_element_present_by_name('signIn'):
                pass
            if self.otp:
                self.br.fill('smsUserPin', self.otp)
                self.br.find_by_id('smsVerifyPin').click()
        except Exception, e:
            self.br.quit()
            return False
        else:
            return True


conf = load_config()

if __name__ == '__main__':
    opts = cli_parse()
    gpem = GPlusEventManager(conf['username'], conf['password'], opts.get('otp'))
    if opts['action'] == 'create':
        id = gpem.create(opts['title'], opts['desc'],
                         opts['date'], opts['time'])

        print 'Created: {}'.format(id)
    elif opts['action'] == 'update':
        id = gpem.update(opts['id'], opts['title'], opts['desc'],
                         opts['date'], opts['time'])

        print 'Event {} updated'.format(opts['id'])
    elif opts['action'] == 'details':
        details = gpem.details(opts['id'])

        print details

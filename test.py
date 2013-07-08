'''Testing without CLI args'''

from gplus_event import GPlusEventManager, conf
import time

# Create Event Manager with username/pass, otp code if desired
gpem = GPlusEventManager(conf['username'], conf['password'], None)

# Create a new event passing in basic information
event = gpem.create(title='Test', desc='Test description', date='2013-09-01', time='10:45 PM')  # noqa
print 'Created event: {}'.format(event)
print 'Now we\'re going to edit it..just a sec'
time.sleep(5)

# Update an event by passing the url and any newly desired information
print event
gpem.update(event, title='New title')
time.sleep(2)

# Print the details and guests of an event
gpem.details(event)

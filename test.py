'''Testing without CLI args'''

from gplus_event import GPlusEventManager, conf
import time

# Create Event Manager with username/pass, otp code if desired
gpem = GPlusEventManager(conf['username'], conf['password'], None)

# Create a new event passing in basic information
event = gpem.create(title='Test', desc='Test description', date='2013-09-01', time='10:45 PM')  # noqa
print 'Created event: {}'.format(event)

# Update an event by passing the url and any newly desired information
gpem = GPlusEventManager(conf['username'], conf['password'], None)
gpem.update(event, title='New title')


# Print the details and guests of an event
gpem = GPlusEventManager(conf['username'], conf['password'], None)
gpem.details(event)

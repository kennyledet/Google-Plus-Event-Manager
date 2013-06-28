from pyvirtualdisplay.smartdisplay import SmartDisplay
import atexit
from easyprocess import EasyProcess

try:
    disp = SmartDisplay(visible=0, bgcolor='black').start()
    atexit.register(disp.stop)
except:
    print 'lel'
    if disp:
        disp.stop()
    raise

print 1
print disp
EasyProcess('python gplus_event.py update --id https://plus.google.com/u/0/events/c7gn468spqgqq9hfm1bt6blmros\?partnerid\=gplp0 --title "Fresher test"').call().stderr
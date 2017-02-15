

from Xlib import display
import Xlib
from Xlib import X
import Xlib.XK
import sys
import signal 
import time

import pyxhook

dpy = None
root = None

def handle_event(event):
    print "handle!"
    if (event.type == X.KeyRelease):
        send_key("x")

# from http://shallowsky.com/software/crikey/pykey-0.1 
def send_key(emulated_key):
    shift_mask = 0 # or Xlib.X.ShiftMask
    window = dpy.get_input_focus()._data["focus"]
    keysym = Xlib.XK.string_to_keysym(emulated_key)
    keycode = dpy.keysym_to_keycode(keysym)
    event = Xlib.protocol.event.KeyPress(
        time = int(time.time()),
        root = root,
        window = window,
        same_screen = 0, child = Xlib.X.NONE,
        root_x = 0, root_y = 0, event_x = 0, event_y = 0,
        state = shift_mask,
        detail = keycode
        )
    window.send_event(event, propagate = True)
    event = Xlib.protocol.event.KeyRelease(
        time = int(time.time()),
        root = dpy.screen().root,
        window = window,
        same_screen = 0, child = Xlib.X.NONE,
        root_x = 0, root_y = 0, event_x = 0, event_y = 0,
        state = shift_mask,
        detail = keycode
        )
    window.send_event(event, propagate = True)

def main():
    # current display
    global dpy,root
    dpy = display.Display()
    root = dpy.screen().root

    # we tell the X server we want to catch keyPress event
    root.change_attributes(event_mask = X.KeyPressMask|X.KeyReleaseMask)
    #dpy.allow_events(X.AsyncKeyboard, X.CurrentTime)            
    # just grab the "1"-key for now
    root.grab_key(10, 0, True,X.GrabModeSync, X.GrabModeSync)

    signal.signal(signal.SIGALRM, lambda a,b:sys.exit(1))
    signal.alarm(10)
    while 1:
        event = dpy.next_event()
        print "event'"
        handle_event(event)
        dpy.allow_events(X.AsyncKeyboard, X.CurrentTime)            

if __name__ == '__main__':
    main()

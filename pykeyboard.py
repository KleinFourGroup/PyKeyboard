from Xlib import display
import Xlib
from Xlib import X
from Xlib import XK
import sys
import signal 
import time

import pyxhook

dpy = None
root = None

grabbed = False
timer = None
t_reset = True

buff = ""

freq = "etaoinshrdlcumwfgypbvkjxqz0123456789"
alph = "abcdefghijklmnopqrstuvwxyz0123456789"

to_grab = ["m", "j", "k", "l", "i", "o", "p"]

buff_parse = {"mm": "a",
             "mk": "b",
             "ml": "c",
             "mi": "d",
             "mo": "e",
             "mp": "f"}

def arm(sec = 10):
    signal.signal(signal.SIGALRM, lambda a,b:kill())
    signal.alarm(sec)

def kill():
    print "killing"
    sys.exit(1)

def gen_parse():
    global buff_parse
    let = [x for x in to_grab if not x == "j"]
    
    loc = 0
    for x in let:
        for y in let:
            # print "buff_parse[" + x + y + "] = freq[" + str(loc) + "] = " + freq[loc]
            buff_parse[x + y] = freq[loc]
            loc = loc + 1

def get_code(key):
    keysym = XK.string_to_keysym(key)
    keycode = dpy.keysym_to_keycode(keysym)
    return keycode

def get_char(code):
    keysym = dpy.keycode_to_keysym(code, 0)
    for name in dir(XK):
        if name.startswith("XK_") and getattr(XK, name) == keysym:
            return name.lstrip("XK_")
    return "[%d]" % keysym

def get_type(etype):
    for name in dir(X):
        if name.startswith("Key") and getattr(X, name) == etype:
            return name
    return "[%d]" % etype
    
def grab(ch):
    code = get_code(ch)
    print "  Grabbing " + ch + " - " + str(code)
    root.grab_key(code, 0, True, X.GrabModeSync, X.GrabModeSync)

def ungrab(ch):
    code = get_code(ch)
    print "  Ungrabbing " + ch + " - " + str(code)
    root.ungrab_key(code, 0)

def grab_handler():
    global grabbed
    if not grabbed:
        for ch in to_grab:
            grab(ch)
    else:
        for ch in to_grab:
            ungrab(ch)
    grabbed = not grabbed


def send_key(emulated_key, shift = False):
    shift_mask = 0 # or Xlib.X.ShiftMask
    if shift:
        shift_mask = Xlib.X.ShiftMask
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
    print "Sent " + emulated_key + " " + str(shift)

def handle_event(event):
    print "Handle: " + get_char(event.detail) + " " + get_type(event.type)
    if (event.type == X.KeyPress):
        OnKeyPress(event)
    else:
        OnKeyUp(event)
        
def OnKeyPress(event):
    if event.detail == get_code('grave'):
        global timer, t_reset
        if t_reset:
            timer = time.time()
            t_reset = False
            grab_handler()
    elif grabbed:
        ch = get_char(event.detail)
        print "Buffer: " + buff
        push(ch)
        print "Buffer: " + buff
        process()
        print "Buffer: " + buff

def OnKeyUp(event):
    if event.detail == get_code('grave'):
        global t_reset
        dif = time.time() - timer
        t_reset = True
        print "\t" + str(dif)
        if dif > 0.2:
            kill()



def push(ch):
    global buff
    buff = buff + ch

def process():
    global buff
    if len(buff) < 2:
        return
    elif len(buff) == 2:
        if buff[0] == 'j' and not buff[1] == 'j':
            return
        if buff in buff_parse:
            ch = buff_parse[buff]
            send_key(ch)
            buff = ""
            return
        buff = buff[0]
        return
    elif len(buff) == 3:
        t = buff[1:]
        if t in buff_parse:
            ch = buff_parse[t]
            send_key(ch, True)
            buff = ""
            return
        buff = buff[0]
        return
    else:
        buff = buff[0]
        return
    
def main():
    global dpy, root
    #start the session
    dpy = display.Display()
    root = dpy.screen().root
    gen_parse()
    for l in alph:
        for m in buff_parse:
            if l == buff_parse[m]:
                print l + " --> " + m

    arm(45)
    # we tell the X server we want to catch keyPress event
    root.change_attributes(event_mask = X.KeyPressMask|X.KeyReleaseMask)
    print "Grabbing `"
    grab('grave')
    while True:
        event = dpy.next_event()
        handle_event(event)
        dpy.allow_events(X.AsyncKeyboard, X.CurrentTime)
"""
a --> ml
b --> ik
c --> kp
d --> ki
e --> mm
f --> li

g --> lo
h --> kk
i --> mo
j --> io
k --> ii
l --> ko

m --> lk
n --> mp
o --> mi
p --> im
q --> om
r --> kl

s --> km
t --> mk
u --> lm
v --> il
w --> ll
x --> ip

y --> lp
z --> ok
0 --> ol
1 --> oi
2 --> oo
3 --> op

4 --> pm
5 --> pk
6 --> pl
7 --> pi
8 --> po
9 --> pp
"""

"""
a --> meli
b --> inka
c --> kapo
d --> kain
e --> meme
f --> liin

g --> liom
h --> kaka
i --> meom
j --> inom
k --> inin
l --> kaom

m --> lika
n --> mepo
o --> mein
p --> inme
q --> omme
r --> kali

s --> kame
t --> meka
u --> lime
v --> inli
w --> lili
x --> inpo

y --> lipo
z --> omka
0 --> omli
1 --> omin
2 --> omom
3 --> ompo

4 --> pome
5 --> poka
6 --> poli
7 --> poin
8 --> poom
9 --> popo
"""


if __name__ == '__main__':
    main()

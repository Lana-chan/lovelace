#!/usr/bin/python

import re
import paramiko
import plugins
import sys
import traceback

k = paramiko.RSAKey(filename='bot_key')
#t = paramiko.Transport(('skynet.mynameiser.in',2022))
t = paramiko.Transport(('chat.shazow.net',22))
t.connect(username='lanabot', pkey=k)
chan = t.open_session()
chan.get_pty(term='xterm-256color',width=80,height=25)
chan.invoke_shell()

dePrompt = '\x1b\x5b\x44'
deColor = re.compile('\x1B\[[0-9;]*[a-zA-Z]')
deBell = re.compile('\x07')

plugs = plugins.PluginManager()

# todo: fingerprints
def isAdmin(user):
  if user == 'Lana': return True
  return False
  
def print_error(info):
	print("----- BEGIN -----")
	traceback.print_exception(info[0], info[1], info[2])
	print("-----  END  -----")

# the parsing is dumb, what are you gonna do about it
# (hopefully fork and improve)
def parseLine(str):
  base = deColor.sub('',str)
  head = base[0:3]
  msg = ['','','','']
  #print head
  if head == ' * ': #part/join
    print 'System: '+str
  elif head == '** ': #emote
    print 'Emote: '+str
    base = base[3:]
    msg = [ 'emote', base[0:base.find(' ')], base[base.find(' ')+1:] ]
  elif head == '[PM': #pm
    print 'PM: '+str
    base = base[9:]
    msg = [ 'pm', base[0:base.find(']')], base[base.find(' ')+1:] ]
  elif not head.startswith('['): #chat
    print 'Chat: '+str
    msg = [ 'chat', base[0:base.find(':')], base[base.find(' ')+1:] ]

  #separate cmd and args
  space_pos = msg[2].find(' ')
  if space_pos == -1:
    cmd = msg[2][0:]
    args = None
  else:
    cmd = msg[2][0:space_pos]
    args = msg[2][space_pos+1:]
  msg = [ msg[0], msg[1], cmd, args ]

  #special commands
  if msg[2].startswith('+'):
    if isAdmin(msg[1]):
      load_failed = []
      unload_failed = []
      success = []
      if msg[2] == '+load': load, unload = True, False
      elif msg[2] == '+unload': load, unload = False, True
      elif msg[2] == '+reload': load, unload = True, True
      for name in msg[3].split(' '):
        try:
          if unload:
            unload_failed.append(name)
            plugs.unload(name)
            unload_failed.remove(name)

          if load:
            load_failed.append(name)
            plugs.load(name)
            load_failed.remove(name)

          success.append(name)

        except StandardError, exc:
          print_error(sys.exc_info())
      message_bits = []
      if success:
        if load and unload:
          verb = 'reloaded'
        elif load:
          verb = 'loaded'
        elif unload:
          verb = 'unloaded'
        message_bits.append("Successfully {1}: {0}".format(', '.join(success), verb))
      if load_failed:
        message_bits.append("Failed to load: {0}".format(', '.join(load_failed)))
      if unload_failed:
        message_bits.append("Failed to unload: {0}".format(', '.join(unload_failed)))

      #c.privmsg(e.target, ' - '.join(message_bits))
      chan.sendall(' - '.join(message_bits)+'\r')
  else:
    plugs.dispatch_event(chan, msg[0], msg[1:])
  #todo: send to plugins

buf = ''

while True: #like it's 1999
  #receive incoming lines
  if chan.recv_ready():
    buf = buf + chan.recv(255) #fill buffer with incoming data
    lines = re.split('\r\n', buf) #separate lines from it
    if len(lines) >= 1: #we have a full line
      for index in range(len(lines)-1): #since it splits at newline, last index is always incommplete/empty
        #print lines[index] #print full lines
        line = lines[index].split(dePrompt)
        parseLine(deBell.sub('',line[len(line)-1])) #remove prompt and bell
        #parseLine(lines[index])
      buf = lines[len(lines)-1] #clear buffer, keep incomplete line

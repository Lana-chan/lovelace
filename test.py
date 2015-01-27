def _init(chan):
  chan.sendall('Module init!\r')

def chat(chan, msg):
  if msg[1] == 'hello':
    chan.sendall('Hi '+msg[0]+'!\r')
  if msg[1] == 'whois':
    chan.sendall('/whois '+msg[2]+'\r')

def fingerprint(chan, msg):
  chan.sendall('I received a fingerprint! msg = ['+', '.join(msg)+']\r')

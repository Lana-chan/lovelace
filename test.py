def _init():
  chan.sendall('Module init!\r')

def chat(msg):
  if msg[1] == 'hello':
    chan.sendall('Hi '+msg[0]+'!\r')
  if msg[1] == 'whois':
    chan.sendall('/whois '+msg[2]+'\r')

def fingerprint(msg):
  chan.sendall('I received a fingerprint! msg = ['+', '.join(msg)+']\r')

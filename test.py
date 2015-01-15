def chat(chan, msg):
  if msg[1] == 'hello':
    chan.sendall('Hi '+msg[0]+'!\r')
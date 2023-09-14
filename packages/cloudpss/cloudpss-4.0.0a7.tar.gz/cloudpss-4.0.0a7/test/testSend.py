from messageStreamSend import MessageStreamSend
import os
import time


def next(m):
    m.write({'type': 'debug', 'step': '-1'})
def goto(m,step):
    m.write({'type': 'debug', 'step': step})
def pause(m):
    m.write({'type': 'debug', 'step': 10})

if __name__ == '__main__':
    os.environ['CLOUDPSS_API_URL'] = 'http://10.101.10.45/'
    m = MessageStreamSend('882ad478-11cf-4041-b3cd-017cba15c606')
    
    m.connect()
    
    while m.status != 1:
        time.sleep(1)
    
    while True:
        next(m)
        time.sleep(0.001)
        # cmd = input('input cmd:')
        # if cmd == 'next':
        #     next(m)
        # elif cmd == 'goto':
        #     step = input('input step:')
        #     goto(m,step)
        # elif cmd == 'pause':
        #     pause(m)
        # elif cmd == 'exit':
        #     break
        # else:
        #     print('input error')
    
    
    m.close()
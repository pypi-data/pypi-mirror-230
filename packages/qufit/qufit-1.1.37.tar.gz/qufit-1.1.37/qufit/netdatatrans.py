

import socket, pickle, time
class clientDriver():
    
    def __init__(self, addr=None, port=6969):
#         socket.setdefaulttimeout(100000)
        self.addr = addr
        self.port = port
        
    def connect(self):
        
        client = socket.socket()
        client.settimeout(1000000)
        client.connect((self.addr,self.port))
        print('connected',client)
        self.handle = client
        
    def send_data(self,counts_dict):
        counts_dict = pickle.dumps(counts_dict)
#         print('send ready?')
        self.handle.send(pickle.dumps({'0':'ready?','1':len(counts_dict)}))
        data = self.handle.recv(1024*5000)
        data = pickle.loads(data)
#         print('recv ready!')
        
        if data == 'ready!':
            self.handle.send(counts_dict)
    
    def recv_data(self):
        
        data = self.handle.recv(1024*5000)
        data = pickle.loads(data)
#         print('recv ready?')
        
        if data['0'] == 'ready?':
            length = data['1']
            self.handle.send(pickle.dumps('ready!'))
            counts_dict = b''
            while 1:
    #             print('send ready!')
                counts_dict += self.handle.recv(1024*5000)
                if len(counts_dict) == length:
                    break
            counts_dict = pickle.loads(counts_dict)
        else:
            pass
            
        return counts_dict
    
    def close(self):
        self.handle.close()   
        
        
        
import socket, pickle, time
class serverDriver():
    
    def __init__(self, addr=None, user=1, port=6969):
#         socket.setdefaulttimeout(100000)
        self.addr = addr
        self.user = user
        self.port = port
        
    def mount(self):
        
        server = socket.socket()
        server.settimeout(10000000)
        server.bind((self.addr,self.port))
        server.listen(self.user)
        print('waiting the call')
        conn, addr = server.accept()
        self.handle = conn
        
    def send_data(self,counts_dict):
        counts_dict = pickle.dumps(counts_dict)
#         print('send ready?')
        self.handle.send(pickle.dumps({'0':'ready?','1':len(counts_dict)}))
        data = self.handle.recv(1024*5000)
        data = pickle.loads(data)
#         print('recv ready!')
        
        if data == 'ready!':
            self.handle.send(counts_dict)
    
    def recv_data(self):
        
        data = self.handle.recv(1024*5000)
        data = pickle.loads(data)
#         print('recv ready?')
        
        if data['0'] == 'ready?':
            length = data['1']
            self.handle.send(pickle.dumps('ready!'))
            counts_dict = b''
            while 1:
    #             print('send ready!')
                counts_dict += self.handle.recv(1024*5000)
                if len(counts_dict) == length:
                    break
            counts_dict = pickle.loads(counts_dict)
        else:
            pass
            
        return counts_dict
    
    def close(self):
        self.send_data('close')
        self.handle.close()
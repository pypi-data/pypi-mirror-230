from io import BytesIO
import cbor2
import sys
import urllib.parse
import uuid
import websocket

class PublisherTask:
    def __init__(self, publisher, action, message):
        self.publisher = publisher
        self.action = action
        self.message = message
        self.callback = None
        self.id = str(uuid.uuid4())
        if publisher.connection is None:
            publisher.connection = websocket.create_connection(publisher.url)
    def set_callback(self, callback):
        self.callback = callback
    def send(self):
        message = {}
        message['type'] = self.action
        if self.publisher.authorization is not None:
            message['authorization'] = self.publisher.authorization
        message['message_id'] = self.id
        for key in self.message:
            value = self.message[key]
            if 'content' == key and isinstance(value, str):
                value = value.encode('utf-8')
            message[key] = value
        request = cbor2.dumps(message)
        self.publisher.connection.send_binary(request)
        complete = False
        while not complete:
            frame = self.publisher.connection.recv_frame()
            response = cbor2.loads(frame.data)
            if response['reply_to'] != self.id:
                continue
            if not response['ok']:
                raise Exception('Web service returned error: %s' % str(response))
            if self.action == 'convert':
                if 'complete' in response:
                    complete = response['complete']
            else:
                complete = True
            self.callback(response)

class Publisher:
    def __init__(self, url, authorization=None):
        self.url = url
        self.authorization = authorization
        url_comps = urllib.parse.urlparse(url)
        self.scheme = url_comps.scheme
        self.host = url_comps.netloc
        self.port = None
        self.path = url_comps.path
        lsi = self.path.rindex('/')
        self.path = self.path[:lsi + 1]
        self.connection = None
        host_comps = self.host.split(':', 1)
        if len(host_comps) > 1:
            self.port = int(host_comps[1])
            self.host = host_comps[0]
    def build(self, action, message):
        return PublisherTask(self, action, message)
    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None


import json
from typing import List
from tornado import gen, httpclient, httputil, ioloop, websocket


APPLICATION_JSON = 'application/json'

DEFAULT_CONNECT_TIMEOUT = 60
DEFAULT_REQUEST_TIMEOUT = 60


class FairyWebSocketClient:
    """Base for web socket clients.
    """
    
    def __init__(self, *, connect_timeout=DEFAULT_CONNECT_TIMEOUT,
                 request_timeout=DEFAULT_REQUEST_TIMEOUT):
        
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout

    @staticmethod
    def request_body_builder(method, parameters: List, need_response: bool = False):
        """
        
        :param method:
        :param parameters:
        :param need_response: whether you need the websocket server
            to give you a response immediately for receiving your request
        :return:
        """
        return json.dumps({
            "jsonrpc": "2.0",
            "method": method,
            "params": parameters,
            "needresponse": need_response,
            "id": 1,
        }, separators=(',', ':'))

    def connect(self, url):
        """Connect to the server.
        :param str url: server URL.
        """
        headers = httputil.HTTPHeaders({'Content-Type': APPLICATION_JSON})
        request = httpclient.HTTPRequest(url=url,
                                         connect_timeout=self.connect_timeout,
                                         request_timeout=self.request_timeout,
                                         headers=headers)
        ws_conn = websocket.WebSocketClientConnection(request)
        ws_conn.connect_future.add_done_callback(self._connect_callback)
    
    def send(self, data):
        """Send message to the server
        :param str data: message.
        """
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is closed.')
        self._ws_connection.write_message(data)
    
    def close(self):
        """Close connection.
        """
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is already closed.')
        self._ws_connection.close()
    
    def _connect_callback(self, future):
        if future.exception() is None:
            self._ws_connection = future.result()
            self._on_connection_success()
            self._read_messages()
        else:
            self._on_connection_error(future.exception())
    
    @gen.coroutine
    def _read_messages(self):
        while True:
            msg = yield self._ws_connection.read_message()
            if msg is None:
                self._on_connection_close()
                break
            
            self._on_message(msg)
    
    def _on_message(self, msg):
        """This is called when new message is available from the server.
        :param str msg: server message.
        """
        pass
    
    def _on_connection_success(self):
        """This is called on successful connection ot the server.
        """
        pass
    
    def _on_connection_close(self):
        """This is called when server closed the connection.
        """
        pass
    
    def _on_connection_error(self, exception):
        """This is called in case if connection to the server could
        not established.
        """
        pass


class TestFairyWebSocketClient(FairyWebSocketClient):
    
    def _on_message(self, msg):
        print(msg)
        # deadline = time.time() + 1
        # ioloop.IOLoop().instance().add_timeout(
        #     deadline, functools.partial(self.send, str(int(time.time()))))
    
    def _on_connection_success(self):
        print('Connected!')
        # self.send(str(int(time.time())))
        # content = self.request_body_builder("subscribecommittingblock", [], need_response=True)
        # print(content)
        # self.send(content)
        # content = self.request_body_builder("subscribecontractevent", [[],[]], need_response=True)
        # print(content)
        # self.send(content)
        content = self.request_body_builder("subscribe", ["block_added"])
        print(content)
        self.send(content)
    
    def _on_connection_close(self):
        print('Connection closed!')
    
    def _on_connection_error(self, exception):
        print('Connection error: %s', exception)


def main():
    client = TestFairyWebSocketClient()
    client.connect('ws://localhost:16869')
    
    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        client.close()


if __name__ == '__main__':
    main()
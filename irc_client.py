import socket
from threading import Thread, Lock
from typing import Callable, List, Any
import certifi
import ssl
#from util import get_user_from_raw, get_message_from_raw

class IrcClient():
    """
    Singleton class for connecting to Twitch's IRC chat server.
    Uses socket with SSL functionality
    """
    _instance = None

    def __new__(self):
        if self._instance == None:
            self._instance = super(IrcClient, self).__new__(self)
            self._host: str
            self._port: int
            self._user: str
            self._oauth: str
            self._channel: str
            self._connection: Any = None
            self._connection_lock = Lock()
            self._send_lock = Lock()
            self._message_handlers_lock = Lock()
            self._message_handlers: List[Callable[[str], None]] = []

        return self._instance

    def __del__(self):
        if self._connection is not None: self.disconnect()

    def connect(self, host: str, port: int, user: str, oauth: str, channel: str) -> None:
        """
        Connects to the IRC chat using socket, saves socket
        object to self._connection SSL certificated provided
        by certifi module
        """
        if not self.check_config(host, port, user, oauth, channel):
            raise RuntimeError('Configuration check failed')

        with self._connection_lock:
            if self._connection is None:
                self._connection = socket.socket()
                self._connection = ssl.wrap_socket(self._connection,
                    ca_certs=certifi.where(),
                    server_side=False)

                try: self._connection.connect((host, port))
                except socket.gaierror:
                    raise RuntimeError('Connection attempt failed')

                self._connection.send(f'PASS {oauth}\r\n'.encode('utf-8'))
                self._connection.send(f'NICK {user}\r\n'.encode('utf-8'))
                self._connection.send(f'USER {user} {host} : {user}\r\n'.encode('utf-8'))
                self._connection.send(f'JOIN {channel}\r\n'.encode('utf-8'))
                self._host = host
                self._port = port
                self._user = user
                self._oauth = oauth
                self._channel = channel
                self._message_thread = Thread(target=self._message_loop, name='IrcMessageThread')
                self._message_thread.start()
            else: raise RuntimeError('The client is already connected')

    def disconnect(self) -> None:
        """
        Performs safe disconnect informing host about it
        _connection should be None after that
        """
        with self._connection_lock:
            connection = self._connection
            self._connection = None

        if connection is not None:
            connection.send(f'PART {self._channel}\r\n'.encode('utf-8'))
            connection.shutdown(socket.SHUT_RDWR)
            connection.close()
        else: raise RuntimeError('The client is not connected')

        if self._message_thread is not None: self._message_thread.join()
        else: raise RuntimeError('The message thread is not running')

    def reconnect(self) -> bool:
        """
        Performs reconnect in case of Twitch server maintenance
        """
        with self._connection_lock:
            if self._connection is not None:
                self._connection.send(f'PART {self._channel}\r\n'.encode('utf-8'))
                self._connection.shutdown(socket.SHUT_RDWR)
                self._connection.close()
            else: raise RuntimeError('The client is not connected')

            self._connection = socket.socket()
            self._connection = ssl.wrap_socket(self._connection,
                ca_certs=certifi.where(),
                server_side=False)

            try: self._connection.connect((self._host, self._port))
            except socket.gaierror:
                raise RuntimeError('Connection attempt failed')

            self._connection.send(f'PASS {self._oauth}\r\n'.encode('utf-8'))
            self._connection.send(f'NICK {self._user}\r\n'.encode('utf-8'))
            self._connection.send(f'USER {self._user} {self._host} : {self._user}\r\n'.encode('utf-8'))
            self._connection.send(f'JOIN {self._channel}\r\n'.encode('utf-8'))

        return True

    def is_connected(self) -> bool:
        """
        Checks if connection is established, returns boolean
        """
        return self._connection is not None

    @staticmethod
    def check_config(H: str, P: int, N: str, O: str, C: str) -> bool:
        """
        Checks if config data format is correct
        """
        if H != 'irc.twitch.tv': return False
        if not isinstance(P, int): return False
        if P != 6697: return False
        if not isinstance(N, str): return False
        if not isinstance(O, str): return False
        if O[:6] != 'oauth:': return False
        if C[0] != '#': return False
        return True

    @staticmethod
    def _get_user_from_raw(msg: str) -> str:
        """
        Gets user from message string
        """
        end: int = msg.find('!')
        return msg[1:end]

    def _get_message_from_raw(self, msg: str) -> str:
        """
        Gets message from message string
        """
        index: int = msg.find(self._channel) + len(self._channel) + 2
        return msg[index:]

    def _send_data(self, data) -> None:
        """
        Sends raw data taking into account connection/packet limitations
        """
        with self._send_lock:
            data_sent: int = 0

            while data_sent < len(data):
                data_sent += self._connection.send(data[data_sent:])

    def _message_loop(self) -> None:
        """
        Waits for message data to be recieved, after that
        calls _process_message
        """
        buffer: str = ""

        while self._connection is not None:
            message_end: int = buffer.find('\r\n')

            if message_end == -1:
                try: buffer += self._connection.recv(1024).decode('utf-8')
                except OSError: return
            else:
                message:str = buffer[:message_end]
                buffer = buffer[message_end + 2:]
                self._process_message(message)

    def send_message(self, message: str) -> None:
        """
        Wraps a string in IRC specific stuff, also encodes to
        UTF-8 to be sent using _send_raw
        """
        if self._connection is not None:
            self._send_data(f'PRIVMSG {self._channel} :{message}\r\n'.encode('utf-8'))
        else: raise RuntimeError('The client is not connected')

    def clear_chat(self) -> None:
        if self._connection is not None:
            self.send_message('/clear')
        else: raise RuntimeError('The client is not connected')

    def clear_user(self, user: str) -> None:
        pass

    def remove_message(self, user: str, message_id: str, message: str) -> None:
        pass

    def start_hosting(self, channel: str) -> None:
        if self._connection is not None:
            self.send_message(f'/host {channel}')
        else: raise RuntimeError('The client is not connected')

    def server_notice(self, message_id, message) -> None:
        pass

    def user_notice(self, message:  str) -> None:
        pass

    def get_roomstate(self, room='') -> None:
        pass

    def get_userstate(self, user: str) -> None:
        pass

    def _process_message(self, message: str) -> None:
        """
        Bounces back the ping message, calls handler function
        passing user generated messages
        """
        if message[:4] == 'PING':
            self._send_data(f'PONG {message[4:]}\r\n'.encode('utf-8'))
            return
        elif message[:9] == 'RECONNECT':
            self.reconnect()
            return
        else:
            sm = message.split()[0]
            lu = self._user.lower()
            if (sm == ':tmi.twitch.tv' or sm == f':{lu}.tmi.twitch.tv' or
                message.split('!')[0] == f':{lu}'): return

        with self._message_handlers_lock:
            for message_handler in self._message_handlers:
                message_handler(self._get_user_from_raw(message), self._get_message_from_raw(message))

    def register_message_handler(self, message_handler: Callable[[str], None]) -> None:
        """
        Registers a callable function to be a message handler.
        Each handler can only take one string parameter and
        should return nothing
        """
        with self._message_handlers_lock:
            if message_handler not in self._message_handlers:
                self._message_handlers.append(message_handler)
            else: raise RuntimeError('Tried to register the same handler twice')

    def unregister_message_handler(self, message_handler: Callable[[str], None]) -> None:
        """
        removes a message handler if in self._message_handlers
        """
        with self._message_handlers_lock:
            if message_handler in self._message_handlers:
                self._message_handlers.remove(message_handler)
            else: raise RuntimeError('Tried to remove non existant handler')

    @classmethod
    def handlerfunction(cls, message_handler: Callable[[str], None]):
        """
        ### DECORATOR ###
        Decorated functions are added to the class' set of handlers, not instance's
        """
        with IrcClient()._message_handlers_lock:
            if message_handler not in IrcClient()._message_handlers:
                IrcClient()._message_handlers.append(message_handler)
            else: raise RuntimeError('Tried to register the same handler twice')

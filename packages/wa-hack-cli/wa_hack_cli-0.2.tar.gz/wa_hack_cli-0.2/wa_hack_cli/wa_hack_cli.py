#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" wa_hack cli client """
from __future__ import print_function
from __future__ import absolute_import
import threading
import hashlib
import argparse
import socket
import base64
import random
import time
import datetime
import sys

# try:
#    reload(sys)
#    sys.setdefaultencoding('utf8')
# except BaseException:
#    pass

STDOUT_ENCODING = sys.stdout.encoding or sys.getfilesystemencoding()

VERSION = "0.2"
CONFIG_DIC = {
    'status': 'offline',
}
DH_DIC = {}

DEBUG = False

CLI_INTRO = """wa_hack  v{cliversion}

Copyright (c) 2023 Grindelsack

This software is provided free of charge. Copying and redistribution is
encouraged.

If you appreciate this software and you would like to support future
development please consider donating to me.

Type /help for available commands
"""


class DHhelper(object):
    """ class to compute diffie hellman key material """

    @staticmethod
    def randomprime(p_v, q_v):
        """ generate random primes """
        print_debug(f'DHhelper.randomprime(): {p_v} {q_v}')
        while True:
            n_v = random.randint(p_v, q_v)
            if n_v % 2 == 0:
                continue
            prime = True
            for x_v in range(3, int(n_v**0.5 + 1), 2):
                if n_v % x_v == 0:
                    prime = False
                    break
            if prime:
                return n_v

    @staticmethod
    def randomint(p_v, q_v):
        """ generate a random integer """
        print_debug(f'DHhelper.randomprime(): {p_v} {q_v}')
        return random.randint(p_v, q_v)

    @staticmethod
    def modcompute(base, secret, prime):
        """ computation modulus """
        print_debug(f'DHhelper.modcompute(): {secret} {prime}')
        return (base**secret) % prime

    @staticmethod
    def hash_it(text):
        """ create sha224 hash """
        print_debug(f'DHhelper.hash_it(): {text}')
        return hashlib.sha224(str(text).encode('utf-8')).hexdigest()


class TCPclient(object):
    """ tcp client class """
    def __init__(self):
        self.thread_receive = threading.Thread(target=self.receive)
        self.thread_receive.daemon = True
        self.cli_sock = None

    def stop(self):
        """ stop a connection, disconnect and set connection status to "offline" """
        self.cli_sock.close()
        CONFIG_DIC['status'] = 'offline'
        self.print_out('Disconnected from remote host...')

    def run(self, server, port, retry_timer=3):
        """ establish a tcp connection to a remote server """
        print_debug(f'TCPclient.run(): {server} {port}')
        retry = 0
        while retry < retry_timer:
            # global cli_sock
            self.cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cli_sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096)
            try:
                self.cli_sock.connect((server, port))
                try:
                    CONFIG_DIC['status'] = 'online'
                except Exception:
                    pass
                self.print_out('Connected to remote host...')
                retry = 0
                break
            except Exception as err:
                self.print_out(f'Unable to connect. Error: {err}')
                retry += 1
                self.cli_sock.close()
                self.cli_sock = None
        if retry == 3:
            self.print_out('Unable to connect. Retry counter exceeded...')
            self.cli_sock.close()
            # self.cli_sock = None
            # sys.exit(0)

    def receive_threat_start(self):
        """ start threat """
        print_debug('TCPclient.receive_threat_start()')
        self.thread_receive.start()

    @staticmethod
    def b64_decode(text):
        """ base64 decode """
        print_debug(f'TCPclient.b64_decode(): {text}')
        return base64.b64decode(text)

    @staticmethod
    def b64_encode(text):
        """ base64 encode """
        print_debug(f'TCPclient.b64_encode(): {text}')

        try:
            return base64.b64encode(text.encode('utf8'))
        except BaseException:
            return base64.b64encode(text)

    def dh_send(self):
        """ dh send """
        print_debug('TCPclient.dh_send()')
        # start diffie hellman key exchange
        dhh = DHhelper()
        sprime = dhh.randomprime(1000000, 10000000)
        sbase = dhh.randomint(1, sprime - 1000)
        secret = dhh.randomint(1, 10000)
        result = dhh.modcompute(sbase, secret, sprime)
        string = f'dhsend {sprime}:{sbase}:{result}'
        self.send(string, '')
        print_debug(f'TCPclient.dh_send() ended with: {sprime} {sbase} xxx')
        return sprime, sbase, secret

    @staticmethod
    def dh_receive(data, secret, sprime):
        """ dh_receive """
        print_debug(f'TCPclient.dh_receive(): {data} xxx {sprime}')
        (_sinin, b_gen) = data.decode().split(' ', 1)
        # print(b_gen,dh_dic['sPrime'],dh_dic['secret'])
        dhh = DHhelper()
        return dhh.hash_it(dhh.modcompute(int(b_gen), secret, sprime))

    @staticmethod
    def hash_it(text, salt):
        """ create a sha224 hash by using a predefined salt """
        print_debug(f'TCPclient.hash_it(): {text} {salt}')
        return hashlib.sha224(f'{text}#:{salt}'.encode('utf-8')).hexdigest()

    def hashtext(self, text, salt):
        """ hash a text and return text and hash """
        print_debug(f'TCPclient.hashtext(): {text} {salt}')
        myhash = self.hash_it(text, salt)
        print_debug(f'TCPclient.hashtext() ended with: {text} {myhash}')
        return f'{text}#:{myhash}'

    def send(self, text, salt):
        """ send a message """
        print_debug(f'TCPclient.send(): {text} {salt}')
        if salt or text.startswith('dhsend'):
            # salt hash text with SHA224 to protect integrity
            if salt:
                text = self.hashtext(text, salt)
            # encode text
            encode = self.b64_encode(text)
            # calculate and attach length
            encode = f"{len(encode)} {encode.decode('utf-8')}".encode()
            self.cli_sock.send(encode)
        else:
            self.print_out('SALT IS MISSING...')

    def check_integrity(self, message, salt):
        """ check integrity """
        print_debug(f'TCPclient.check_integrity(): {message} {salt}')
        (message, mhash) = message.decode('utf-8').split('#:', 1)
        myhash = self.hash_it(message, salt)
        if mhash == myhash:
            result = self.format_message(message)
        else:
            result = f'INTEGRITY CHECK FAILED!\n{message}'

        return result

    def format_message(self, msg):
        """ format mesasge """

        try:
            sender, message = msg.split(' - ')

            grp, grp_sender = sender.split('#')
            if grp_sender != 'None':
                grp = f'{grp} [{grp_sender}]'
            msg = ' - '.join([grp, message])
        except Exception:
            pass

        return msg

    def receive_single(self):
        """  recieve data of upto 1024b from a socket """
        print_debug('TCPclient.receive_single()')
        data = self.cli_sock.recv(1024)
        return self.b64_decode(data)

    def receive(self):
        """ recieve data """
        print_debug('TCPclient.receive()')
        while True:
            data = self.cli_sock.recv(1024)
            stw = b'dhsend'
            if data:
                try:
                    data = self.b64_decode(data)
                    if 'salt' in CONFIG_DIC:
                        print("")
                        message = self.check_integrity(data, CONFIG_DIC['salt'])
                        self.print_out(message)
                    elif data.startswith(stw):
                        CONFIG_DIC['salt'] = self.dh_receive(data, DH_DIC['secret'], DH_DIC['sPrime'])
                    else:
                        self.print_out('RECIEVED MESSAGE WITHOUT HAVING A SALT!')
                        self.print_out(data)
                except BaseException:
                    self.print_out(f'RECEIVED INVALID DATA! got: "{data.decode()}"')
                    CONFIG_DIC['status'] = 'offline'
                    sys.exit(0)
            else:
                self.print_out('\nDisconnected from server')
                CONFIG_DIC['status'] = 'offline'
                sys.exit(0)

    @staticmethod
    def print_prompt():
        """ print status prompt """
        print_debug('TCPclient.print_prompt()')
        print(f"[{CONFIG_DIC['status']}]:")

    @staticmethod
    def print_out(text):
        """ print_out """
        print_debug(f'TCPclient.print_out(): {text}')
        if text:
            now = datetime.datetime.now().strftime('%H:%M:%S')
            try:
                print(f'{now} {text}\n'.encode(STDOUT_ENCODING).decode('utf-8'))
            except Exception:
                print('{now} {text}\n'.encode('utf8').decode('utf-8'))


class CommandLineInterface(object):
    """ cli class """
    def __init__(self):
        self.tcpc = TCPclient()
        CLIParser(self)

    def check_command(self, command):
        """ check command """
        print_debug(f'CommandLineInterface.check_command(): {command}')
        if command in ['help', 'H']:
            self.print_help()
        elif command in ['connect', 'L']:
            self.connect_server()
        # elif(command == 'disconnect'):
        #    self.disconnect_server()
        elif command == 'show config':
            self.show_config()
        elif command in ['generate salt', 'G']:
            (DH_DIC['sPrime'], DH_DIC['sBase'], DH_DIC['secret']) = self.tcpc.dh_send()
        elif command in ['quit', 'Q']:
            self.quit()
        elif command.startswith('server'):
            self.set_server(command)
        elif 'salt' in CONFIG_DIC:
            if command.startswith('routes announce'):
                self.tcpc.send(command, CONFIG_DIC['salt'])
            elif command == 'show groups':
                self.tcpc.send(command, CONFIG_DIC['salt'])
            elif command == 'database delete':
                self.tcpc.send(command, CONFIG_DIC['salt'])
            elif command.startswith('location send'):
                self.send_location(command, CONFIG_DIC['salt'])
            elif command.startswith('image send'):
                self.send_image(command, CONFIG_DIC['salt'])
            elif command.startswith('message'):
                self.send_message(command, CONFIG_DIC['salt'])
            else:
                if command:
                    self.print_out(f'unknown command: "/{command}"')
                    self.print_help()
        else:
            self.print_out('we are missing a salt!')

    def check_server_config(self):
        """ check server config """
        print_debug('CommandLineInterface.check_server_config()')
        if 'server' in CONFIG_DIC and 'port' in CONFIG_DIC:
            if CONFIG_DIC['status'] == 'offline':
                result = True
            else:
                self.print_out('You are already online. Run /disconnect first.')
                result = False
        else:
            self.print_out('configuration incomplete. Set server and port first')
            result = False

        return result

    def connect_server(self):
        """ connect to server """
        print_debug('CommandLineInterface.connect_server()')
        status = self.check_server_config()
        if status:
            # self.print_out('connect')
            try:
                self.tcpc.run(CONFIG_DIC['server'], CONFIG_DIC['port'])
                self.tcpc.receive_threat_start()
            except BaseException:
                pass

    @staticmethod
    def decode_input(cmd):
        """ decode input """
        print_debug(f'CommandLineInterface.decode_input(): {cmd}')
        result = cmd
        return result

    def disconnect_server(self):
        """ disconnect_server """
        print_debug('CommandLineInterface.disconnect_server()')
        if CONFIG_DIC['status'] == 'online':
            # self.print_out('diconnect')
            self.tcpc.stop()

    def exec_cmd(self, cmdinput):
        """ execute command """
        print_debug(f'CommandLineInterface.exec_cmd(): {cmdinput}')
        cmdinput = cmdinput.rstrip()

        # skip empty commands
        if not len(cmdinput) > 1:
            return

        if cmdinput.startswith("/"):
            cmdinput = cmdinput[1:]
        else:
            self.print_help()
            return

        self.check_command(cmdinput)

    @staticmethod
    def get_prompt():
        """ get prompt """
        print_debug('CommandLineInterface.get_prompt()')
        return f"[{CONFIG_DIC['status']}]:"

    @staticmethod
    def print_intro():
        """ print cli intro """
        print_debug('CommandLineInterface.print_intro()')
        print(CLI_INTRO.format(cliversion=VERSION))

    @staticmethod
    def print_out(text):
        """ print text """
        print_debug('CommandLineInterface.print_out()')
        if text:
            now = datetime.datetime.now().strftime('%H:%M:%S')
            print(f'{now} {text}\n')

    def print_prompt(self):
        """ print prompt """
        print_debug('CommandLineInterface.print_prompt()')
        print(self.get_prompt())

    @staticmethod
    def print_help():
        """ print help """
        print_debug('CommandLineInterface.print_help()')
        helper = """-------------------------------------------------------------------------------
/connect   /L                                  connect to server
/database     delete                           delete msgstore.db - USE CAREFULLY!
/generate  /G salt                             generate salt via diffie hellmann key exchange
/image        send     <number> <file>         send image
/location     send     <number> <lat,long>     send location
/message      send     <number> <content>      send message
/help      /H                                  print list of avaialble commands
/routes       announce <number>,<number>       set message routing
/server                <server>:<port>         set server
/show         config                           show configuration dictionary
/show         groups                           show groups we belong to
/quit      /Q                                  quit
"""
        print(helper)

    def quit(self):
        """ quit (whatever) """
        print_debug('CommandLineInterface.quit()')
        if CONFIG_DIC['status'] == "online":
            self.disconnect_server()
        # self.print_out('You are online. Run /disconnect first.')
        sys.exit(0)

    def send_something(self, mtype, text, salt):
        """ put some text on the wire """
        print_debug(f'CommandLineInterface.send_something(): {mtype} {text} {salt}')
        if CONFIG_DIC['status'] == 'online':
            (command, action, payload) = text.split(' ', 2)
            if command == mtype and action == 'send':
                try:
                    (recipient, message) = payload.split(' "', 1)
                    message = message.lstrip('"')
                    message = message.rstrip('"')
                    b64_message = self.tcpc.b64_encode(message)
                    # print(b64_message.decode())
                    text = f'{mtype} send {recipient} {b64_message.decode()}'
                    self.tcpc.send(text, salt)
                except BaseException:
                    self.print_out('text to be send must be surrounded by "')
            else:
                self.print_out('invalid syntax')
        else:
            self.print_out('you are not online. Connect first')

    def send_image(self, text, salt):
        """ send image -> this is incomplete!!! """
        print_debug(f'CommandLineInterface.send_image(): {text} {salt}')
        if CONFIG_DIC['status'] == 'online':
            try:
                (_command, _subcommand, recipient, ifile) = text.split(' ', 3)
                try:
                    ifile = ifile.lstrip('"')
                    ifile = ifile.rstrip('"')
                    with open(ifile, 'rb').read() as fso:
                        b64_img = self.tcpc.b64_encode(f'{ifile}#:{fso}')
                        text = f'image send {recipient} {b64_img}'
                        self.tcpc.send(text, salt)
                except Exception as err:
                    self.print_out(f'file not found: {err}')
            except Exception:
                self.print_out('invalid syntax')
        else:
            self.print_out('you are not online. Connect first')

    def send_location(self, text, salt):
        """ send location """
        print_debug(f'CommandLineInterface.send_location(): {text} {salt}')
        self.send_something('location', text, salt)

    def send_message(self, text, salt):
        """ send message """
        print_debug(f'CommandLineInterface.send_message(): {text} {salt}')
        self.send_something('message', text, salt)

    def show_config(self):
        """ show config """
        print_debug('CommandLineInterface.show_config()')
        for ckey, kvalue in CONFIG_DIC.items():
            self.print_out(f'{ckey}:{kvalue}')

    def start(self):
        """ start """
        print_debug('CommandLineInterface.start()')
        self.print_intro()

        while True:
            cmd = input(self.get_prompt()).strip()
            cmd = self.decode_input(cmd)
            self.exec_cmd(cmd)

    def set_server(self, text):
        """ setup server """
        print_debug(f'CommandLineInterface.set_server(): {text}')
        try:
            (_sinin, serverport) = text.split()
            (server, port) = serverport.split(':')
            # validate server port
            try:
                port = int(port)
                if port <= 65535:
                    # validate server ip
                    if valid_ip(server):
                        # print(server,port,salt)
                        CONFIG_DIC['server'] = server
                        CONFIG_DIC['port'] = port
                    else:
                        self.print_out(f'{server} is not a valid ip address')
                else:
                    self.print_out(f'{port} is not a valid portnumber')
            except BaseException:
                self.print_out(f'{port} is not a valid portnumber')

        except BaseException:
            self.print_out('server must be specified with /server <ip>:<port>')


class CLIParser(object):
    """ cli parser """

    cli = None

    def __init__(self, cli=None):
        parser = argparse.ArgumentParser()

        parser.add_argument("-d", "--debug",
                            action="store_true",
                            help="Show debug messages",
                            dest='debug',)

        parser.add_argument("-c", "--config",
                            action='store',
                            help='config-file to load',
                            dest='cfgfile',)
        results = parser.parse_args()

        self.cli = cli
        if results.cfgfile:
            self.load_cfg(results.cfgfile)

    def load_cfg(self, ifile):
        """ load config """
        print_debug('CLIParser.load_cfg()')
        # try:
        with open(ifile, 'r', encoding='utf8') as fha:
            for lin in fha:
                line = lin.rstrip()
                if line.startswith('sleep'):
                    try:
                        (_sleep, tme) = line.split(' ', 1)
                        time.sleep(int(tme))
                    except BaseException:
                        time.sleep(1)
                else:
                    if line.startswith('#') is False:
                        self.cli.check_command(line)

        # except BaseException:
        #    print('config file {0} not found...'.format(file))
        #    sys.exit(0)


def valid_ip(address):
    """ validate ip address """
    # pylint: disable=r1716
    print_debug(f'valid_ip(): {address}')
    try:
        host_bytes = address.split('.')
        valid = [int(b) for b in host_bytes]
        valid = [b for b in valid if b >= 0 and b <= 255]
        return len(host_bytes) == 4 and len(valid) == 4
    except BaseException:
        return False


def simple_send(srv, port, recipient, text):
    """ example sender """
    print_debug(f'simple_send(): {srv} {port} {recipient} {text}')

    tcpc = TCPclient()
    if tcpc:
        try:
            # connect to server
            tcpc.run(srv, port)
            (sprime, _sbase, secret) = tcpc.dh_send()
            data = tcpc.receive_single()
            salt = tcpc.dh_receive(data, secret, sprime)
            # encode text utf8 then base64 and send it
            try:
                text = tcpc.b64_encode(text.decode(sys.getfilesystemencoding()).encode('utf8'))
            except Exception:
                text = tcpc.b64_encode(text.encode('utf8'))
            dtext = text.decode('utf-8')
            tcpc.send(f'message send {recipient} "{dtext}"', salt)
            # close connection
            tcpc.stop()
        except Exception:
            print('connection error. Aborting....')
            sys.exit(0)


def simple_receive(srv, port, routes):
    """ example receiver """
    print_debug(f'simple_send(): {srv} {port} {routes}')

    tcpc = TCPclient()
    if not routes.startswith('routes announce'):
        routes = f'routes announce {routes}'
    if tcpc:
        try:
            tcpc.run(srv, port)
            (sprime, _sbase, secret) = tcpc.dh_send()
            data = tcpc.receive_single()
            salt = tcpc.dh_receive(data, secret, sprime)
            CONFIG_DIC['salt'] = salt
            tcpc.send(routes, salt)
            data = tcpc.receive_single()
            tcpc.receive()
            # close connection
            tcpc.stop()
        except KeyboardInterrupt:
            # close connection
            tcpc.stop()
            raise
        except BaseException:
            print('connection error. Aborting....')
            sys.exit(0)


def rand_sleep(max_value):
    """ random sleep """
    print_debug(f'rand_sleep(): {max_value}')
    val = random.randint(0, max_value - 1)
    # print(val)
    time.sleep(val)


def print_debug(text):
    """ little helper to print debug messages """
    if DEBUG:
        print(f'{datetime.datetime.now()}: {text}')


if __name__ == "__main__":

    CLI = CommandLineInterface()
    CLI.start()

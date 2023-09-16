import ctypes
import functools
import multiprocessing
import os
import random
import socket
import sys
import threading
import time
from threading import Thread

# multiprocessing.freeze_support()


class GFW_Interface:
    local_socket = ""

    def __init__(
        self,
        num_fragment,
        listen_PORT,
        Cloudflare_IP,
        Cloudflare_port,
        from_cmd=False,
        GFW_Timeout=10,
    ):
        self.num_fragment = num_fragment
        self.listen_PORT = listen_PORT  # pyprox listening to 127.0.0.1:listen_PORT
        self.Cloudflare_IP = Cloudflare_IP
        self.Cloudflare_port = Cloudflare_port
        self.timeout_in_socksets = GFW_Timeout
        # self.mainThread = threading.Thread(target=self.start_tunnel)
        # self.mainThread.start()
        self.init_localsocket()
        self.mainThread = threading.Thread(target=self.start_tunnel)
        self.mainThread.daemon = True
        self.mainThread.start()
        # self.mainThread.join()
        # if from_cmd:
        #     self.mainThread = threading.Thread(target=self.start_tunnel)
        #     self.mainThread.daemon = True
        #     self.mainThread.start()
        #     self.mainThread.join()
        # else:
        #     self.mainThread = multiprocessing.Process(target=self.start_tunnel)
        #     self.mainThread.start()

    def init_localsocket(self):
        self.local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.local_socket.settimeout(self.timeout_in_socksets)
        self.local_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.local_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def stop(self):
        print("**Stop GFW is called***")
        self.loop = False
        # self.local_socket.setblocking(False)
        try:
            self.local_socket.close()
        except:
            print("error closing..")
        # GFW_thread_id = self.mainThread.ident
        # ctypes.pythonapi.PyThreadState_SetAsyncExc(
        #     GFW_thread_id, ctypes.py_object(SystemExit)
        # )
        # self.mainThread.join(1)

        try:
            self.local_socket.close()
        except:
            pass

        try:
            self.mainThread.kill()
            self.mainThread.terminate()

        except:
            pass
        # self.mainThread.join()
        print(f"Subprocess {self.mainThread.name} alive: {self.mainThread.is_alive}")
        # self.mainThread.join(2)

    @staticmethod
    def timeout(timeout):
        def deco(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                res = [
                    Exception(
                        "1366_function [%s] timeout [%s seconds] exceeded!"
                        % (func.__name__, timeout)
                    )
                ]

                def newTargetFunc():
                    try:
                        res[0] = func(*args, **kwargs)
                    except Exception as e:
                        res[0] = e

                t = Thread(target=newTargetFunc)
                t.daemon = True
                try:
                    t.start()
                    t.join(timeout)
                except Exception as je:
                    print("error starting thread")
                    raise je
                ret = res[0]
                if isinstance(ret, BaseException):
                    raise ret
                return ret

            return wrapper

        return deco

    def start_tunnel(self):
        self.loop = True
        # Define the local listening address and port
        local_host = "0.0.0.0"
        local_port = self.listen_PORT

        # # Define the remote server address and port
        remote_host = self.Cloudflare_IP
        remote_port = self.Cloudflare_port
        print(
            f"Main func is started-> local::{local_host}:{local_port}\nremote::{remote_host}:{remote_port} "
        )
        while self.loop:
            try:
                # Create the local listening socket

                # try:
                self.init_localsocket()
                self.local_socket.bind((local_host, local_port))
                self.local_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.local_socket.listen(20)

            except Exception as problem:
                print(f"High level exeception: {problem}")
            #

            print(f"Listening on {local_host}:{local_port}...")
            while self.loop:
                print(f"number of threads: {len(threading.enumerate())}")
                print("waiting for new connection...")
                try:
                    time.sleep(0.1)
                    client_socket, client_address = self.local_socket.accept()
                    client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    print(
                        f"Accepted connection from {client_address[0]}:{client_address[1]}"
                    )
                    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    remote_socket.connect((remote_host, remote_port))
                    remote_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    remote_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    print(f"Connected to remote server {remote_host}:{remote_port}")
                    #################
                    self.trans_rec(client_socket, remote_socket)
                    ##################
                except Exception as problem:
                    print(f"Error 770: {problem}")
                    if "completed immediately" in str(problem):
                        print("continue")
                        continue

                    # if "1366" in str(e):
                    #     remote_socket.close()
                    #     continue
                    try:
                        client_socket.close()
                        remote_socket.close()
                    except Exception as e:
                        print(f"Error 990: {e}")
                        continue
                    print("\n***Connection closed***\n")
                    # time.sleep(0.1)

    # @timeout(1)
    def trans_rec(self, client_socket, remote_socket):
        client_to_server_thread = self.forward_data(
            client_socket, remote_socket, "client_to_server"
        )
        random_number = random.random() * 0.5
        time.sleep(random_number)
        server_to_client_thread = self.forward_data(
            remote_socket, client_socket, "server_to_client"
        )

        # client_to_server_thread.join(0.5)
        # server_to_client_thread.join()

    def forward_data(
        self, src_socket: socket.socket, dst_socket: socket.socket, mode: str
    ):
        def forward():
            loop_counter = 1
            socketsize = self.generate_random_number_about(1000, 0.75)
            rand = self.generate_random_number_about(self.timeout_in_socksets, 0.2)

            @self.timeout(rand)
            def rec():
                return src_socket.recv(socketsize)

            while self.loop:
                try:
                    data = rec()
                    # print(f"while counter : {while_counter}")
                    # print(f"len data is: {len(data)}")
                    if data:
                        if loop_counter <= 1 and mode == "client_to_server":
                            self.send_data_in_fragment(data, dst_socket)
                        else:
                            # dst_socket.sendall(data)
                            dst_socket.sendall(data)
                    else:
                        raise Exception("No data execption***")
                except Exception as e:
                    print(f"Err occured: in {mode} {e}")
                    try:
                        src_socket.close()
                        dst_socket.close()
                    except:
                        pass
                    break
                loop_counter += 1

        thread = threading.Thread(target=forward)
        thread.daemon = True
        thread.start()
        return thread

    def generate_random_number_about(self, number, ratio=0.15):
        deviation = number * ratio
        min_value = int(number - deviation)
        max_value = int(number + deviation)
        return random.randint(min_value, max_value)

    # @timeout(2)
    def send_data_in_fragment(self, data: list, sock: socket.socket):
        L_data = len(data)
        rand = self.generate_random_number_about(self.num_fragment)
        indices = random.sample(
            range(1, L_data - 1),
            rand - 1,
        )
        indices.sort()
        print("indices=", indices)

        i_pre = 0
        for i in indices:
            fragment_data = data[i_pre:i]
            i_pre = i
            # sock.sendall(fragment_data)
            sock.sendall(fragment_data)
            # time.sleep(0.1)

        fragment_data = data[i_pre:L_data]
        sock.sendall(fragment_data)
        print("----------finish------------")


# Start the tunne
if __name__ == "__main__":
    multiprocessing.freeze_support()
    try:
        num_fragment = int(sys.argv[4])
        listen_PORT = int(sys.argv[2])  # pyprox listening to 127.0.0.1:listen_PORT
        Cloudflare_IP = sys.argv[1]
        Cloudflare_port = int(sys.argv[3])
        GFW_Interface(
            num_fragment, listen_PORT, Cloudflare_IP, Cloudflare_port, True, 5
        )
    except:
        listen_PORT = 2500
        num_fragment = 75
        Cloudflare_IP = "bruce.ns.cloudflare.com"
        Cloudflare_port = 8443
        GFW_Interface(
            num_fragment, listen_PORT, Cloudflare_IP, Cloudflare_port, True, 10
        )
    while True:
        time.sleep(10)
        ##########################################################
        #########################################################

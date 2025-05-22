import argparse
import os
import socket
import threading
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

BUFFER_SIZE = 65536  # 64KB

class SyncHandler(FileSystemEventHandler):
    def __init__(self, root_dir, file_meta):
        self.root_dir = root_dir
        self.file_meta = file_meta
        self.target_file = "database.db"
        self.init_file_meta()

    def init_file_meta(self):
        target_path = os.path.join(self.root_dir, self.target_file)
        if os.path.exists(target_path):
            self._update_meta(target_path)

    def _update_meta(self, path):
        rel_path = os.path.relpath(path, self.root_dir)
        if rel_path != self.target_file:
            return
        stat = os.stat(path)
        self.file_meta[rel_path] = {
            'mtime': stat.st_mtime,
            'size': stat.st_size
        }

    def on_modified(self, event):
        if not event.is_directory:
            rel_path = os.path.relpath(event.src_path, self.root_dir)
            if rel_path == self.target_file:
                self._update_meta(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            rel_path = os.path.relpath(event.src_path, self.root_dir)
            if rel_path == self.target_file:
                self._update_meta(event.src_path)

def handle_client(conn, file_meta, root_dir):
    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    try:
        # 发送元数据
        meta_json = json.dumps(file_meta)
        meta_data = meta_json.encode()
        conn.send(len(meta_data).to_bytes(4, 'big'))
        conn.sendall(meta_data)

        # 等待请求
        while True:
            cmd = conn.recv(1024).decode().strip()
            if not cmd:
                break

            if cmd.startswith('GET'):
                filename = cmd.split(' ', 1)[1]
                filepath = os.path.join(root_dir, filename)

                if os.path.exists(filepath):
                    filesize = os.path.getsize(filepath)
                    conn.send(filesize.to_bytes(4, 'big'))
                    with open(filepath, 'rb') as f:
                        while True:
                            data = f.read(BUFFER_SIZE)
                            if not data:
                                break
                            conn.sendall(data)
                else:
                    conn.send(b'\x00\x00\x00\x00')
    finally:
        conn.close()

def start_server(host, port, sync_dir):
    file_meta = {}
    observer = Observer()
    event_handler = SyncHandler(sync_dir, file_meta)
    observer.schedule(event_handler, sync_dir, recursive=True)
    observer.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")

        try:
            while True:
                conn, addr = s.accept()
                print(f"Connected: {addr}")
                client_thread = threading.Thread(
                    target=handle_client,
                    args=(conn, file_meta, sync_dir)
                )
                client_thread.start()
        finally:
            observer.stop()
            observer.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=9999)
    parser.add_argument('--dir', default='./server_files')
    args = parser.parse_args()

    os.makedirs(args.dir, exist_ok=True)

    start_server(args.host, args.port, args.dir)

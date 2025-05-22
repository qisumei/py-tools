import argparse
import os
import socket
import json
import time

BUFFER_SIZE = 65536  # 64KB，提升传输效率

def sync_files(server_host, server_port, local_dir):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # 关闭 Nagle 算法
            s.settimeout(5)
            s.connect((server_host, server_port))
            
            # 接收元数据长度
            meta_size = int.from_bytes(s.recv(4), 'big')
            meta_data = b''
            while len(meta_data) < meta_size:
                chunk = s.recv(min(BUFFER_SIZE, meta_size - len(meta_data)))
                if not chunk:
                    break
                meta_data += chunk
            server_meta = json.loads(meta_data.decode())

            # 获取本地文件信息
            target_file = "database.db"
            file_path = os.path.join(local_dir, target_file)
            local_meta = {}
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                local_meta[target_file] = {
                    'mtime': stat.st_mtime,
                    'size': stat.st_size
                }

            server_file = server_meta.get(target_file)
            local_file = local_meta.get(target_file)
            need_sync = False

            if not local_file or (server_file and (
                server_file['mtime'] > local_file['mtime'] or 
                server_file['size'] != local_file['size'])):
                need_sync = True

            if need_sync:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 检测到更新")
                s.send(f"GET {target_file}".encode())

                size = int.from_bytes(s.recv(4), 'big')
                if size > 0:
                    received = 0
                    os.makedirs(local_dir, exist_ok=True)
                    with open(file_path, 'wb') as f:
                        while received < size:
                            chunk = s.recv(min(BUFFER_SIZE, size - received))
                            if not chunk:
                                break
                            f.write(chunk)
                            received += len(chunk)
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 同步完成，接收 {received} 字节")
                else:
                    print("服务器文件不存在")
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 文件已是最新版本")

    except Exception as e:
        print(f"连接异常: {str(e)}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True)
    parser.add_argument('--port', type=int, default=9999)
    parser.add_argument('--dir', default='./client_files')
    args = parser.parse_args()

    os.makedirs(args.dir, exist_ok=True)

    while True:
        sync_files(args.server, args.port, args.dir)
        time.sleep(1)

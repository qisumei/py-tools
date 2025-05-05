import argparse
import os
import socket
import json
import time

def sync_files(server_host, server_port, local_dir):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # 设置超时时间
            s.connect((server_host, server_port))
            
            # 接收元数据
            meta_size = int.from_bytes(s.recv(4), 'big')
            meta_data = b''
            while len(meta_data) < meta_size:
                chunk = s.recv(min(4096, meta_size - len(meta_data)))
                if not chunk:
                    break
                meta_data += chunk
            server_meta = json.loads(meta_data.decode())

            # 获取本地元数据
            local_meta = {}
            target_file = "database.db"  # 指定同步文件
            file_path = os.path.join(local_dir, target_file)
            
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                local_meta[target_file] = {
                    'mtime': stat.st_mtime,
                    'size': stat.st_size
                }

            # 文件对比逻辑
            need_sync = False
            server_file = server_meta.get(target_file)
            local_file = local_meta.get(target_file)

            if not local_file or (server_file and 
                (server_file['mtime'] > local_file['mtime'] or 
                 server_file['size'] != local_file['size'])):
                need_sync = True

            # 执行同步
            if need_sync:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 检测到更新")
                s.send(f"GET {target_file}".encode())
                
                # 接收文件内容
                size = int.from_bytes(s.recv(4), 'big')
                if size > 0:
                    content = b''
                    while len(content) < size:
                        chunk = s.recv(min(4096, size - len(content)))
                        if not chunk:
                            break
                        content += chunk
                    
                    # 保存文件
                    os.makedirs(local_dir, exist_ok=True)
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 同步完成")
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
    
    if not os.path.exists(args.dir):
        os.makedirs(args.dir)
    
    # 持续运行检测
    while True:
        sync_files(args.server, args.port, args.dir)
        time.sleep(1)  # 1秒检测间隔
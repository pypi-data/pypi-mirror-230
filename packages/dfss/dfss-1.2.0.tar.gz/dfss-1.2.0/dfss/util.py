import paramiko
import socket
import stat
import os

def is_remote_directory(remote_path,sftp):
    try:
        remote_attributes = sftp.stat(remote_path)
        return stat.S_ISDIR(remote_attributes.st_mode)
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Failed to determine directory: {e}")
        return False

def download_file_from_sophon_sftp(remote_path,local_path):
    server_list = [
        ("106.37.111.18", 32022),
        ("172.26.175.10", 32022),
    ]

    hostname = None
    port = None
    username = 'open'
    password = 'open'



    for server in server_list:
        ip, port_to_check = server
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, port_to_check))
            if result == 0:
                hostname = ip
                port = port_to_check
                break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            sock.close()

    if hostname is None or port is None:
        print("No available servers found. Exiting.")
        exit()

    print(f'using server address: {hostname}:{port}')
    transport = paramiko.Transport((hostname, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    if is_remote_directory(remote_path, sftp) is True:
        print("do not support download dir.")
        exit()

    remote_path = os.path.normpath(remote_path)
    local_path = os.path.normpath(local_path)
    local_item = os.path.basename(remote_path)
    if os.path.isdir(local_path) is True:
        local_path = os.path.join(local_path, local_item)
    directory = os.path.dirname(local_path)
    if os.path.isdir(directory) is False:
        os.makedirs(directory)
    print(f'download file from {remote_path} -> {local_path}')
    sftp.get(remote_path, local_path)
    sftp.close()
    transport.close()

if __name__ == "__main__":
    remote_path = '/编译用工具链/gcc-linaro-6.3.1-2017.05-x86_64_aarch64-linux-gnu.tar.xz'
    local_path = '/home/zzt/workspace/dfn-1.1.0 copy/test/'
    download_file_from_sophon_sftp(remote_path,local_path)
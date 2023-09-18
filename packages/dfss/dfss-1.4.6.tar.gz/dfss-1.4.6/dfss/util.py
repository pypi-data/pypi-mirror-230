import paramiko
from progressbar import ProgressBar, Percentage, Bar, FileTransferSpeed, ETA
import socket
import stat
import os


def is_remote_directory(remote_path, sftp):
    try:
        remote_attributes = sftp.stat(remote_path)
        return stat.S_ISDIR(remote_attributes.st_mode)
    except Exception as e:
        print('Failed to determine directory:', str(e))
        exit(-1)


def format_file_size(file_size_bytes):
    if file_size_bytes < 1024:
        return "{} B".format(file_size_bytes)
    elif file_size_bytes < 1024 ** 2:
        return "{:.2f} KB".format(file_size_bytes / 1024)
    elif file_size_bytes < 1024 ** 3:
        return "{:.2f} MB".format(file_size_bytes / (1024 ** 2))
    elif file_size_bytes < 1024 ** 4:
        return "{:.2f} GB".format(file_size_bytes / (1024 ** 3))
    else:
        return "{:.2f} TB".format(file_size_bytes / (1024 ** 4))


def download_file_from_sophon_sftp(remote_path, local_path):
    server_list = [
        ("106.37.111.18", 32022, 'open', 'open'),
        ("172.26.175.10", 32022, 'oponIn', 'oponIn'),
    ]

    hostname = None
    port = None
    username = None
    password = None

    for server in server_list:
        ip, port_to_check, user, passwd = server
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, port_to_check))
            if result == 0:
                hostname = ip
                port = port_to_check
                username = user
                password = passwd
                break
        except Exception as e:
            print('An error occurred:', str(e))
        finally:
            sock.close()

    if hostname is None or port is None or username is None or password is None:
        print("No available servers found. Exiting.")
        exit(-1)
    try:
        transport = paramiko.Transport((hostname, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        if is_remote_directory(remote_path, sftp) is True:
            print("do not support download dir.")
            exit(-1)

        local_path = os.path.normpath(local_path)
        local_item = os.path.basename(remote_path)
        if os.path.isdir(local_path) is True:
            local_path = os.path.join(local_path, local_item)
        directory = os.path.dirname(local_path)
        if os.path.isdir(directory) is False:
            os.makedirs(directory)
        remote_file_size = sftp.stat(remote_path).st_size
        print('download file from', remote_path, '->', local_path, ', size:',
              format_file_size(remote_file_size), '...')
        widgets = [ETA(), ' | ', Percentage(), Bar(), FileTransferSpeed()]
        pbar = ProgressBar(widgets=widgets, maxval=remote_file_size).start()

        def progress_callback(x, y):
            pbar.update(x)
        sftp.get(remote_path, local_path, callback=progress_callback)
        pbar.finish()
        sftp.close()
        transport.close()
    except Exception as e:
        print('An error occurred:', str(e))


def upload_file_to_sophon_sftp(remote_path, local_path):
    server_list = [
        ("106.37.111.18", 32022, 'customerUploadAccount', '1QQHJONFflnI2BLsxUvA'),
        ("172.26.175.10", 32022, 'customerUploadAccount', '1QQHJONFflnI2BLsxUvA'),
    ]

    hostname = None
    port = None
    username = None
    password = None

    for server in server_list:
        ip, port_to_check, user, passwd = server
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, port_to_check))
            if result == 0:
                hostname = ip
                port = port_to_check
                username = user
                password = passwd
                break
        except Exception as e:
            print('An error occurred:', str(e))
        finally:
            sock.close()

    if hostname is None or port is None or username is None or password is None:
        print("No available servers found. Exiting.")
        exit(-1)
    try:
        transport = paramiko.Transport((hostname, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        local_path = os.path.normpath(local_path)
        if not os.path.isfile(local_path):
            print(local_path, 'is not a file.')
            exit(-1)
        remote_file_size = os.path.getsize(local_path)
        print('up file from', local_path, '-> open@sophgo.com:/', remote_path, 'size:',
              format_file_size(remote_file_size), '...')
        widgets = [ETA(), ' | ', Percentage(), Bar(), FileTransferSpeed()]
        pbar = ProgressBar(widgets=widgets, maxval=remote_file_size).start()

        def progress_callback(x, y):
            pbar.update(x)
        sftp.put(local_path, remote_path,
                 callback=progress_callback, confirm=False)
        pbar.finish()
        sftp.close()
        transport.close()
    except Exception as e:
        print('An error occurred:', str(e))

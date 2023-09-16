import argparse as arg
import os

from dfss.util import download_file_from_sophon_sftp

def dfss_parser():
    parser = arg.ArgumentParser(description     = "download_file_from_sophon_sftp",
                                formatter_class = arg.ArgumentDefaultsHelpFormatter,
                                prog            = "python -m dfss")
    required_group = parser.add_argument_group("required", "required parameters for compilation")
    required_group.add_argument("--url",
                                type    = str,
                                help    = "url to remote sftp file")
    return parser
if __name__ == "__main__":
    parser = dfss_parser()
    a = parser.parse_args()
    print(f'download from {a.url}')
    if a.url is not None:
        if a.url.startswith("open@sophgo.com:"):
            file_path = a.url[len("open@sophgo.com:"):]
            download_file_from_sophon_sftp(file_path,'./')
        else:
            print(f'please from open@sophgo.com download')
    
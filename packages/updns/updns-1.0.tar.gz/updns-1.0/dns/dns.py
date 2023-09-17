import socket
import traceback
import platform


def resolve_domain():
    """
    解析域名，返回IP地址列表
    """
    ip_list = []
    try:
        # 解析域名，返回一个IP地址列表
        addrs = socket.getaddrinfo('home.w0rk.top', None)
        for addr in addrs:
            ip = addr[4][0]
            ip_list.append(ip)
    except:
        traceback.print_exc()
    return ip_list[0]


def main():
    FILE_NAME = r"C:\Windows\System32\drivers\etc\hosts" if ("Windows" in platform.system()) else "/etc/hosts"
    print(f"\nhosts文件位置：{FILE_NAME}\n")
    with open(FILE_NAME, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    domain_ip = str(resolve_domain())
    a = False
    for i in lines:
        if "001.gov" in i:
            a = True
            lines[lines.index(i)] = f'{domain_ip}   001.gov\n'
    if not a:
        lines.append(f'{domain_ip}    001.gov\n')
    # 再更新文件
    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"\n已更新hosts：'home.w0rk.top'\n{domain_ip}  001.gov\n")


if __name__ == '__main__':
    main()

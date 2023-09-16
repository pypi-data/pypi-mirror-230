import socket as S
import ipaddress as ipaddr
import os
import sys

def is_private(ip):
    """
    Check if an ip address is a private ip address.
    """
    return ipaddr.ip_address(ip).is_private


def is_loopback(ip):
    """
    Check if an ip address is a loopback ip address.
    """
    return ipaddr.ip_address(ip).is_loopback


def get_all_ip():
    if sys.platform == "win32":
        l = S.getaddrinfo(S.gethostname(), None, S.AF_INET)
        l += S.getaddrinfo(S.gethostname(), None, S.AF_INET6)
        return [e[4][0] for e in l]
    elif sys.platform == "linux":
        return os.popen("hostname -I").read().strip().split(" ")


def filter_public(ip_list):
    return [ip for ip in ip_list if ipaddr.ip_address(ip).is_global]

def get_all_public_ip():
    return filter_public(get_all_ip())


def get_inet_ipv4():
    """
    Get ip that has the connection to the internet. If the host is behind a NAT, 
    this function may still return private ip address.
    """
    with S.socket(S.AF_INET, S.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]


def get_inet_ipv6():
    """
    Get IPv6 address that has the connection to the internet. If the host is behind a NAT, 
    this function may still return private ip address.
    """
    with S.socket(S.AF_INET6, S.SOCK_DGRAM) as s:
        s.connect(("2001:4860:4860::8888", 80))
        return s.getsockname()[0]


def get_all_inet_ip():
    """
    Get all ip addresses that has the connection to the internet. If the host is behind a NAT, 
    this function may still return private ip address.
    """
    return [get_inet_ipv4(), get_inet_ipv6()]


def get_ip_by_inet(use_ipv6 = False):
    """
    Use inet.me to get the ip address that has the connection to the internet. The ip address 
    returned may not be the ip address of the host if the host is behind a NAT.
    """
    host = "ident.me"
    
    with S.socket(S.AF_INET6 if use_ipv6 else S.AF_INET, S.SOCK_STREAM) as s:
        s.connect((host, 80))
        s.send(b"GET / HTTP/1.1\r\n")
        s.send(b"Host: ident.me\r\n")
        s.send(b"User-Agent: Python Raw Socket\r\n")
        s.send(b"Connection: close\r\n")
        s.send(b"\r\n")
        
        res = (s.recv(2048) or b'').decode("utf-8")
        lines = res.split("\r\n")
        if lines[0] and lines[0].split(" ")[-1] == 'OK':
            return lines[-1]
    return None

def get_all_ip_by_inet():
    """
    Use inet.me to get all ip addresses that has the connection to the internet. The ip address 
    returned may not be the ip address of the host if the host is behind a NAT.
    """
    return [get_ip_by_inet(), get_ip_by_inet(use_ipv6=True)]
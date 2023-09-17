import sys
from datetime import datetime
from net_operations.lib.funcs import generate_from_template
from net_operations.lib.funcs import check_ip_as_argv
from net_operations.lib.classes.NetOperations import NetOperations
from net_operations.lib.cisco.brases_funcs import make_cisco_base_statistics
from net_operations.lib.cisco.brases_funcs import make_cisco_static_hosts_report
from net_operations.lib.cisco.brases_funcs import (
    generate_cisco_full_hosts_report_list)
from net_operations.lib.cisco.brases_funcs import make_cisco_full_report


def hw_report_gen(report_func, template) -> None:

    if sys.argv[1]:
        ip = sys.argv[1]
    else:
        ip = input('Введите IP-адрес устройства: ')
    vendor = "huawei"

    conn = NetOperations(ip, vendor)
    try:
        conn.establish_connection()
        report_dic = report_func(conn)
        report_str = generate_from_template(template, report_dic)
        time = str(datetime.now()).replace(' ', '_').replace(':', '.')
        filename = f'{time}_{ip}.md'
        with open(filename, 'w') as dst:
            dst.write(report_str)
        print(f'Report for {ip} saved as {filename}.')
    except Exception as error:
        print('Something gone wrong.')
        print(f'Error is "{error}"')


def cisco_host_brief_report(ip: str = None) -> None:
    if not ip:
        ip = check_ip_as_argv()
    try:
        conn = NetOperations(ip, "cisco")
        conn.establish_connection()
        stat_dict = make_cisco_base_statistics(conn)
        conn.close()
        make_cisco_static_hosts_report(stat_dict, ip)
    except Exception as error:
        print("There are some error:")
        print(error)


def cisco_host_full_report(ip: str = None) -> None:
    if not ip:
        ip = check_ip_as_argv()
    try:
        conn = NetOperations(ip, "cisco")
        conn.establish_connection()
        full_report = generate_cisco_full_hosts_report_list(conn)
        make_cisco_full_report(full_report, ip)
    except Exception as error:
        print("There are some error:")
        print(error)

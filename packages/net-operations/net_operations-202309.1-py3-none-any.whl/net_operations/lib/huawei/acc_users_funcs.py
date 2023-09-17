from net_operations.lib.constants import CX600_LICENSE
from net_operations.lib.constants import T_BAS_LICENSE, T_BAS_INTFS
from net_operations.lib.huawei.main_info_funcs import get_hw_license_list
from datetime import datetime
import re


def check_hw_value(value, abscence='-'):
    return value if value != abscence else None


def get_huawei_domains(conn) -> dict:
    domains = {}
    output = conn.send_commands('display domain')
    reg = re.compile(r" +(\S+) +\S+ +\d+ +\d+ +(\d+)")
    for item in reg.finditer(output):
        name, online = item.groups()
        domains.update({name: {'online': online}})
    return domains


def get_huawei_domain_info(conn, domain) -> dict:
    command = f'display domain {domain}'
    output = conn.send_commands(command)
    r_authen_sch = r'Authentication-scheme-name +: +(\S+)'
    r_acct_sch = r'Accounting-scheme-name +: +(\S+)'
    r_author_sch = r'Authorization-scheme-name +: +(\S+)'
    r_online = r'Online-number +: +(\S+)'
    r_dns_ipv4 = r'DNS-IP-address +: +(\S+)'
    r_dns_ipv6 = r'DNS-IPV6-address +: +(\S+)'
    r_redirect = r'Web-URL +: +(\S+)'
    r_radius = r'RADIUS-server-template +: +(\S+)'
    r_tacacs = r'HWTACACS-server-template +: +(\S+)'
    r_ip_pool = r'IP-address-pool-name +: +(\S+)'
    r_nat_ug = r'User-group nat +: +(\S+), +.*'
    r_nat_inst = r'User-group nat +: +\S+, +(\S+),'
    regexps = [
        ("authen_scheme", r_authen_sch),
        ("account_scheme", r_acct_sch),
        ("author_scheme", r_author_sch),
        ("online", r_online),
        ("redirect_url", r_redirect),
        ("radius_server", r_radius),
        ("tacacs_server", r_tacacs),
        ("default_ip_pool", r_ip_pool),
        ("nat_user_group", r_nat_ug),
        ("nat_instance", r_nat_inst)
    ]
    info_dict = {"name": domain}
    for key, regexp in regexps:
        reg = re.compile(regexp)
        if reg.search(output):
            info_dict[key] = check_hw_value(reg.search(output).group(1))
    reg4 = re.compile(r_dns_ipv4)
    reg6 = re.compile(r_dns_ipv6)
    for dns4 in reg4.finditer(output):
        dns = dns4.group(1)
        info_dict.setdefault('dns_ipv4', []).append(check_hw_value(dns))
    for dns6 in reg6.finditer(output):
        dns = dns6.group(1)
        info_dict.setdefault('dns_ipv6', []).append(check_hw_value(dns))
    return {domain: info_dict}


def get_huawei_bas_interfaces(conn) -> dict:
    r_bas_line = r'(\S+) +(\S+) +\S+ +(\d+)'
    bas_intf_dict = {}
    output = conn.send_commands('display bas-interface')
    for item in re.finditer(r_bas_line, output):
        bas, type_, online = item.groups()
        bas_intf_dict.update({bas: {'type': type_, 'online': online}})
    return bas_intf_dict


def get_huawei_bas_intf_info(conn, bas_intf) -> dict:
    r_preauth = r'Pre-authentication default domain +: +(\S+)'
    r_authen = r'Authentication default domain +: +(\S+)'
    r_authen_method = r'Authentication method +: +\[(\S+)\]'
    r_opt82 = r'Client option82 +: +(\S+)'
    r_vrf = r'Vpn Instance +: +(\S+)'
    basif_list = [
        (r_preauth, 'preauth_domain', None),
        (r_authen, 'authen_domain', None),
        (r_authen_method, 'authen_method', None),
        (r_opt82, 'opt82', None),
        (r_vrf, 'vrf', 'GRT'),
    ]
    command = f'display bas-interface {bas_intf}'
    output = conn.send_commands(command)
    info_dict = {}
    for regexp, key, default in basif_list:
        searched = re.search(regexp, output)
        if searched:
            info_dict[key] = check_hw_value(searched.group(1))
        else:
            info_dict[key] = default
    return {bas_intf: info_dict}


def get_hw_all_bas_info(conn):
    rbp_info = get_hw_all_rbp_info(conn)
    bas_intf_dict = get_huawei_bas_interfaces(conn)
    bas_intf_list = list(bas_intf_dict.keys())
    bas_statics = get_hw_static_users(conn)
    for intf in bas_intf_list:
        bas_intf_dict[intf]["name"] = intf
        bas_intf_dict[intf].update(get_huawei_bas_intf_info(conn, intf)[intf])
        rbp_name = "-"
        for rbp in rbp_info:
            if intf in rbp['rbp_intf']:
                rbp_name = rbp["name"]
        bas_intf_dict[intf]['static_qty'] = str(len(bas_statics.get(intf, '')))
        bas_intf_dict[intf]["rbp_name"] = rbp_name
    return bas_intf_dict


def get_huawei_radius_gr_info(conn, rsg_name) -> dict:
    r_authen_srv = (r"Authentication-server *: +"
                    r"IP:(\S+) +Port: *(\S+) +Weight\[(\d+)\].*\n"
                    r"(?: +Vpn: +(\S+))*")
    r_account_srv = (r"Accounting-server *: +"
                     r"IP:(\S+) +Port: *(\S+) +Weight\[(\d+)\].*\n"
                     r"(?: +Vpn: +(\S+))*")
    r_src_intf = r"Source interface +: +(\S+)"
    r_csi = r"Calling-station-id include +: +(\S+)"
    command = f"display radius-server configuration group {rsg_name}"
    output = conn.send_commands(command)
    rad_conf = {
        "name": rsg_name,
        "authen_servers": [],
        "account_servers": [],
        "src_interface": None,
        "call_station_id": None
    }
    iterable_keys = [("authen_servers", r_authen_srv),
                     ("account_servers", r_account_srv)]
    noniter_keys = [("src_interface", r_src_intf),
                    ("call_station_id", r_csi)]
    for key, regexp in iterable_keys:
        reg = re.compile(regexp)
        for group in reg.finditer(output):
            ip, port, weight, vrf = group.groups()
            srv_dict = {
                "ip": ip,
                "port": port,
                "weight": weight,
                "vrf": vrf
            }
            rad_conf[key].append(srv_dict)
    for key, regexp in noniter_keys:
        searched = re.search(regexp, output)
        res = None
        if searched:
            res = check_hw_value(searched.group(1))
        rad_conf[key] = res
    return rad_conf


def get_huawei_total_users(conn):
    r_normal = r"Normal users +: *(?P<normal>\d+)"
    r_rui_loc = r"RUI Local users +: *(?P<rui_local>\d+)"
    r_rui_rem = r"RUI Remote users +: *(?P<rui_remote>\d+)"
    r_radius = r"Radius authentication +: *(?P<radius_auth>\d+)"
    r_noauth = r"No authentication +: *(?P<no_auth>\d+)"
    r_total = r"Total users +: *(?P<total>\d+)"
    values = [r_normal, r_rui_loc, r_rui_rem, r_radius, r_noauth, r_total]
    users_dict = {
        "ipv4": {
            "normal": None,
            "rui_local": None,
            "rui_remote": None,
            "radius_auth": None,
            "no_auth": None,
            "total": None
        },
        "ipv6": {
            "normal": None,
            "rui_local": None,
            "rui_remote": None,
            "radius_auth": None,
            "no_auth": None,
            "total": None
        },
    }
    for ip_type in users_dict.keys():
        command = f"display access-user ip-type {ip_type} summary"
        output = conn.send_commands(command)
        for regexp in values:
            searched = re.search(regexp, output)
            if searched:
                users_dict[ip_type].update(searched.groupdict())
    return users_dict


def normalize_total_users(tot_users):
    for type_ in tot_users:
        for key, value in tot_users[type_].items():
            if value is None:
                tot_users[type_][key] = "0"


def get_hw_intf_with_statics(conn, with_output=True):
    r_intf = r"(\S+) +\d\S+ +\S+ +\S+ +\S+"
    output = conn.send_commands("display static-user")
    reg = re.compile(r_intf)
    intf = list(sorted({intf.group(1) for intf in reg.finditer(output)}))
    return (intf, output) if with_output else intf


def get_hw_static_user_verbose(conn, ip_address, ip_type="ipv4"):
    types = {"ipv4": "ip-address", "ipv6": "ipv6-address"}
    command = f"display static-user {types[ip_type]} {ip_address}"
    output = conn.send_commands(command)
    r_domain = r"Static user domain +: *(\S+)"
    r_gateway = r"Static user Gateway +: *(\S+)"
    pairs = (r_domain, "domain"), (r_gateway, "gateway")
    ver_dict = {}
    for regexp, key in pairs:
        searched = re.search(regexp, output)
        if searched:
            ver_dict[key] = check_hw_value(searched.group(1))
        else:
            ver_dict[key] = None
    return ver_dict


def get_hw_static_users(conn):
    interfaces, output = get_hw_intf_with_statics(conn)
    users_dict = {intf: [] for intf in interfaces}
    for intf in interfaces:
        r_values = fr"{intf} +(\d\S+) +(\S+) +(\S+) +(\S+)\n +(\S+).*\n +(\S+)"
        reg = re.compile(r_values)
        for item in reg.finditer(output):
            vlans, ipv4_add, mac, vrf, ipv6_add, ipv6_pref = map(check_hw_value,
                                                                 item.groups())
            if "/" in vlans:
                s_vlan, c_vlan = vlans.split("/")
            else:
                s_vlan = vlans
                c_vlan = None
            dict_upd = {
                "ipv4_address": ipv4_add,
                "s_vlan": s_vlan,
                "c_vlan": c_vlan,
                "mac": mac,
                "vrf": vrf,
                "ipv6_address": ipv6_add,
                "ipv6_delegated_prefix": ipv6_pref
                }
            ver_dict = get_hw_static_user_verbose(conn, ipv4_add)
            dict_upd.update(ver_dict)
            users_dict[intf].append(dict_upd)
    return users_dict


def get_hw_bas_licenses(conn):
    all_lic = get_hw_license_list(conn)
    bas_licenses = []
    for lic in all_lic:
        name = lic['name']
        if any([name in CX600_LICENSE['BRAS'], name in CX600_LICENSE['HA']]):
            bas_licenses.append(lic)
    return bas_licenses


def get_hw_rbp_list(conn):
    output = conn.send_commands('display remote-backup-profile')
    r_rbp = r' +0x\S+ +(\S+)'
    rbp_list = [item.group(1) for item in re.finditer(r_rbp, output)]
    return rbp_list


def get_hw_rbp_info(conn, rbp_name):
    command = f'display remote-backup-profile {rbp_name}'
    output = conn.send_commands(command)
    r_rbs = r"Remote-backup-service *: *(\S+)"
    r_vrrp = (r" *VRRP-ID *: *(?P<vrrp_id>\S+)\n"
              r" *VRRP-Interface *: *(?P<vrrp_intf>\S+)\n"
              r" *Access-Control *: *(?P<acc_ctrl>\S+)\n"
              r" *State *: *(?P<own_state>\S+)\n"
              r" *Peer State *: *(?P<peer_state>\S+)\n")
    r_split_1 = r" *Interface *:\n"
    r_split_2 = r" *Forwarding Configured *:"
    rbp_intf = re.split(r_split_2, re.split(r_split_1, output)[-1])[0].split()
    vrrp = []
    for item in re.finditer(r_vrrp, output):
        vrrp.append(item.groupdict())
    searched = re.search(r_rbs, output)
    if searched:
        rbs = searched.group(1)
    else:
        rbs = None
    rbp_dict = {
        "name": rbp_name,
        "rbs": rbs,
        "vrrp": vrrp,
        "rbp_intf": rbp_intf
    }
    return rbp_dict


def get_hw_all_rbp_info(conn) -> list:
    rbps = get_hw_rbp_list(conn)
    rbp_list = [get_hw_rbp_info(conn, rbp) for rbp in rbps]
    return rbp_list


def normalize_dicts_from_list_for_table(data, const):
    normalized = []
    for item in data:
        for key, value in const.items():
            new_value = item[key] + (value - len(item[key])) * " "
            item[key] = new_value
        normalized.append(item)
    return normalized


def get_hw_bas_report_dict(conn):
    total_users = get_huawei_total_users(conn)
    normalize_total_users(total_users)
    licenses = normalize_dicts_from_list_for_table(
        get_hw_bas_licenses(conn), T_BAS_LICENSE)
    bas_intfs = list(get_hw_all_bas_info(conn).values())
    domain_list = list(
        {item.get(key) for item in bas_intfs for key in ["preauth_domain",
                                                         "authen_domain"]})
    domains_info = []
    rsgs = set()
    for domain in domain_list:
        domain_info = get_huawei_domain_info(conn, domain)[domain]
        rsg = domain_info.get("radius_server")
        if rsg:
            rsgs.add(rsg)
        domains_info.append(domain_info)
    bas_interfaces = normalize_dicts_from_list_for_table(bas_intfs, T_BAS_INTFS)
    radius_info = []
    for rsg in list(rsgs):
        rsg_info = get_huawei_radius_gr_info(conn, rsg)
        radius_info.append(rsg_info)
    bas_report = {
        "report_time": str(datetime.utcnow()),
        "device_ip": conn.ip,
        "total_users": total_users,
        "licenses": licenses,
        "bas_interfaces": bas_interfaces,
        "domains_info": domains_info,
        "radius_info": radius_info
    }
    return bas_report

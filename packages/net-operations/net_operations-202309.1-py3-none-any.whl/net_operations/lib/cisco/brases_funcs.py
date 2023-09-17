import re
import copy
import ipaddress
import itertools
from datetime import datetime
from net_operations.lib.funcs import convert_wcard_to_netmask
from net_operations.lib.classes.NetOperations import NetOperations


def get_cisco_interfaces_policies(conn: NetOperations,
                                  waittime: int = 60) -> dict:

    '''
    Parses output of filtered "show run" and Generates dictionary
    with interfaces and binded to them policies.
    Output example:

    {
        'Port-channel1.11000668': {'isg': 'SRVC'},
        'Port-channel1.24': {'input': 'SHAPE10Mb', 'output': 'SHAPE10Mb'},
        'Port-channel1.61': {'output': 'SHAPE200Mb'}
    }
    '''

    command = "show run | include ^interface|^ service-policy"
    if conn.connection_type == "ssh":
        output = conn.send_commands(command, waittime=waittime,
                                    recv_val=4000000)
    else:
        output = conn.send_commands(command, waittime=waittime)
    output = output.replace('\r\n', '\n').replace(
        '\n service-policy ', '\t').replace('interface ', '')
    policies_dict = {}
    for interface in output.split('\n'):
        if len(interface.split('\t')) > 1:
            subif, *policies = interface.split('\t')
            policies_dict[subif] = {}
            for policy in policies:
                if 'input' in policy:
                    policies_dict[subif]['input'] = policy.replace('input ',
                                                                   '')
                elif 'output' in policy:
                    policies_dict[subif]['output'] = policy.replace(
                        'output ', '')
                elif 'type control' in policy:
                    policies_dict[subif]['isg'] = policy.replace(
                        'type control ', '')
    return policies_dict


def get_cisco_routes_by_interfaces(conn: NetOperations,
                                   waittime: int = 20) -> tuple:

    '''
    Parse output of "show run part ip-static-route" and generates
    tuple of two dicts:
     - subif_dict contains subinterfaces and attached static routes;
     - route_dict contains host static routes as keys and dicts with
       subinterfaces that routes attached to.
    Example of subif_dict:
    {
        'Port-channel1.3000': ['10.81.224.2 255.255.255.255'],
        'Port-channel2.40240602': ['37.208.100.3 255.255.255.255'],
        'Port-channel2.40240603': ['37.208.100.5 255.255.255.255'],
        'Port-channel2.40240604': ['37.208.100.6 255.255.255.255'],
        'Port-channel2.40240900': ['37.208.100.2 255.255.255.255']
    }
    Example of route_dict:
    {'10.81.224.2 255.255.255.255': {'input': None,
                                    'isg': None,
                                    'output': None,
                                    'subif': 'Port-channel1.3000'},
    '37.208.100.2 255.255.255.255': {'input': None,
                                    'isg': None,
                                    'output': None,
                                    'subif': 'Port-channel2.40240900'},
    '37.208.100.3 255.255.255.255': {'input': None,
                                    'isg': None,
                                    'output': None,
                                    'subif': 'Port-channel2.40240602'},
    '37.208.100.5 255.255.255.255': {'input': None,
                                    'isg': None,
                                    'output': None,
                                    'subif': 'Port-channel2.40240603'},
    '37.208.100.6 255.255.255.255': {'input': None,
                                    'isg': None,
                                    'output': None,
                                    'subif': 'Port-channel2.40240604'}}
    '''

    command = 'show run part ip-static-route'
    if conn.connection_type == "ssh":
        output = conn.send_commands(command, waittime=waittime,
                                    recv_val=4000000)
    else:
        output = conn.send_commands(command, waittime=waittime)
    output = output.replace('\r\n', '\n')
    reg_interface = (r'ip route (?:vrf \S+ )?\S+ \S+ ((?:Port-channel\d+)'
                     r'(?:[.]\d+)*|(?:(?:Ten)*GigabitEthernet\d+(?:/\d+)*)'
                     r'(?:[.]\d+)*)')
    subif_iter = re.finditer(reg_interface, output)
    subif_list = [item.group(1) for item in subif_iter]
    subif_list = list(sorted(set(subif_list)))
    subif_dict = {subif: [] for subif in subif_list}
    route_dict = {}
    for key in subif_dict.keys():
        key_reg = fr'ip route (?:vrf \S+ )?((?:\S+) (?:\S+)) {key}'
        key_iter = re.finditer(key_reg, output)
        if key_iter:
            for route in key_iter:
                subif_dict[key].append(route.group(1))
                route_dict[route.group(1)] = {
                    'subif': key,
                    'input': None,
                    'output': None,
                    'isg': None}
    return subif_dict, route_dict


def make_cisco_base_statistics_from_dict(policies_dict: dict,
                                         route_dict: dict) -> dict:
    for route in route_dict.keys():
        subif_values = policies_dict.get(route_dict[route]['subif'], None)
        if subif_values:
            for key, value in subif_values.items():
                route_dict[route][key] = value
    return route_dict


def make_cisco_base_statistics(conn: NetOperations, wait1: int = 60,
                               wait2: int = 60) -> dict or None:

    '''
    Generates dict with host static routes as keys and their additional info
    such as connected subinterfaces, used policies, etc
    Example of stat_dict:
    {'10.81.224.2 255.255.255.255': {'input': None,
                                    'isg': None,
                                    'output': 'DOMOFON_10M',
                                    'subif': 'Port-channel1.3000'},
    '37.208.100.2 255.255.255.255': {'input': None,
                                    'isg': 'B2B_ISG_IP',
                                    'output': None,
                                    'subif': 'Port-channel2.40240900'},
    '37.208.100.3 255.255.255.255': {'input': None,
                                    'isg': 'B2B_ISG_IP',
                                    'output': None,
                                    'subif': 'Port-channel2.40240602'},
    '37.208.100.5 255.255.255.255': {'input': None,
                                    'isg': 'B2B_ISG_IP',
                                    'output': None,
                                    'subif': 'Port-channel2.40240603'},
    '37.208.100.6 255.255.255.255': {'input': None,
                                    'isg': 'B2B_ISG_IP',
                                    'output': None,
                                    'subif': 'Port-channel2.40240604'}}
    '''

    policy_dict = get_cisco_interfaces_policies(conn, wait1)
    if policy_dict:
        _, route_dict = get_cisco_routes_by_interfaces(conn, wait2)
    else:
        return None
    stat_dict = copy.deepcopy(route_dict)
    for route in route_dict.keys():
        subif_values = policy_dict.get(route_dict[route]['subif'], None)
        if subif_values:
            for key, value in subif_values.items():
                stat_dict[route][key] = value
    return stat_dict


def get_cisco_unique_used_policies(policies_dict: dict) -> set:

    '''
    Takes policies dictionary and generates set of used policies.
    Example of unique_policies:
    {'DOMOFON_10M',
    'LEASED_22',
    'SHAPE5Mb',
    'SHAPE700Mb'}
    '''

    unique_policies = set()
    for interface in policies_dict.keys():
        for _type, policy in policies_dict[interface].items():
            if _type != "isg" and "copp" not in policy.lower():
                unique_policies.add(policy)
    return unique_policies


def get_cisco_classes_from_policy_map(conn: NetOperations,
                                      pmap: str, waittime: int = 0.5) -> list:

    '''
    Takes name of policy-map and get information about contained classes.
    Returns list of names of class
    '''

    reg_class = r" *[Cc]lass (\S+)"
    com_pm = f"show policy-map {pmap}"
    output = conn.send_commands(com_pm, waittime)
    return [item.group(1) for item in re.finditer(reg_class, output)]


def get_cisco_pmaps_with_classes_normalized(conn: NetOperations,
                                            pmaps: list or set,
                                            waittime: int = 0.5) -> dict:
    full_pmaps_dict = {}
    for pmap in pmaps:
        cmaps = get_cisco_classes_from_policy_map(conn, pmap, waittime)
        full_pmaps_dict[pmap] = {cmap: {"rate": None, "cpe": []} for
                                 cmap in cmaps}
    return full_pmaps_dict


def get_cisco_unique_used_classes(conn: NetOperations,
                                  pmaps: list or set,
                                  waittime: int = 0.5) -> list:
    cmaps = []
    for pmap in pmaps:
        cmaps += get_cisco_classes_from_policy_map(conn, pmap, waittime)
    unique_classes = list(set(cmaps))
    return unique_classes


def get_cisco_ips_from_classes(conn: NetOperations, cmaps: list or set,
                               waittime: int = 0.5) -> dict:

    '''
    Returns dict with classes as keys and sets of tuples with ip-address and
    wildcard of that class as values.
    Example of cmap_ips_dict:
    {
        'SRG88244': {('46.250.88.244', None)},
        'SRG88247': {('46.250.88.247', None)},
        'SRG88252': {('46.250.88.252', None)},
        'SUNLIGHT': {('176.222.18.26', None)},
        'SVYAZNOY_Kogalym': {('176.222.18.56', None)},
        'Sushi-Market-Region': {('176.222.18.47', None)}
    }

    '''

    reg_ace_src = (r" +\d+ permit ip(?: host)? (?P<ip>(?:[0-9]{1,3}[.]){3}"
                   r"[0-9]{1,3}) ?(?P<wildcard>(?:[0-9]{1,3}[.]){3}"
                   r"[0-9]{1,3})? any")
    reg_ace_dst = (r" +\d+ permit ip any(?: host)? (?P<ip>(?:[0-9]{1,3}[.]){3}"
                   r"[0-9]{1,3})(?: (?P<wildcard>(?:[0-9]{1,3}[.]){3}"
                   r"[0-9]{1,3}))?")
    reg_cm = r"Match access-group (?:name )(?P<acl>\S+)"
    cmap_ips_dict = {cmap: set() for cmap in cmaps}
    for cmap in cmap_ips_dict.keys():
        com_cm = f"show class-map {cmap}"
        out_cm = conn.send_commands(com_cm, waittime)
        searched_acl = re.search(reg_cm, out_cm)
        if searched_acl:
            acl = searched_acl.group(1)
            com_acl = f"show ip access-list {acl}"
            acl_out = conn.send_commands(com_acl)
            for pair in re.finditer(reg_ace_src, acl_out):
                cmap_ips_dict[cmap].add(pair.groups())
            for pair in re.finditer(reg_ace_dst, acl_out):
                cmap_ips_dict[cmap].add(pair.groups())
    return cmap_ips_dict


def get_cisco_cmap_rate_in_pmap(conn: NetOperations, pmap: str,
                                waittime: int = 1) -> dict:
    reg_cir = r" +(?:cir|rate) +(?P<cir>\d+) \((?P<measurement>\S+)\)"
    pmap_rate_dict = {pmap: {}}
    for cmap in get_cisco_classes_from_policy_map(conn, pmap):
        com_cl = f"show policy-map {pmap} class {cmap}"
        cl_out = conn.send_commands(com_cl, waittime=waittime)
        if re.search(reg_cir, cl_out):
            pmap_rate_dict[pmap][cmap] = re.search(reg_cir, cl_out).groupdict()
    return pmap_rate_dict


def get_cisco_rates_in_all_pmaps(conn: NetOperations,
                                 pmaps: set or list,
                                 ) -> dict:

    '''
    Takes connection and set or list of policy-maps.
    Returns dict with policy-maps as keys and dict of classes and binded to
    them rates as values.
    Example of pmaps_rate_dict:
    {
        'DOMOFON_10M': {'SRG21494': {'cir': '10485760', 'measurement': 'bps'}},
        'LEASED_23': {'SRG214147': {'cir': '5242880', 'measurement': 'bps'},
                    'SRG214148': {'cir': '5242880', 'measurement': 'bps'},
                    'SRG214149': {'cir': '5242880', 'measurement': 'bps'},
                    'SRG214150': {'cir': '5242880', 'measurement': 'bps'}},
        'LEASED_499': {'SRG1802': {'cir': '10485760', 'measurement': 'bps'},
                        'SRG1803': {'cir': '104857600', 'measurement': 'bps'},
                        'SRG1814': {'cir': '104857600', 'measurement': 'bps'}}
    }
    '''

    pmaps_rate_dict = {}
    for pmap in pmaps:
        pmaps_rate_dict.update(get_cisco_cmap_rate_in_pmap(conn,
                                                           pmap))
    return pmaps_rate_dict


def get_cisco_intf_ip_info(conn: NetOperations, waittime: int = 45) -> dict:

    '''
    Returns dict with interfaces as keys and dict with list of ip-addresses
    in form of ipv4 address object and unnumbered intf source.
    Example of int_dict:
    {
        'Port-channel1.221': {
            'addresses': [],
            'unnumbered': 'Loopback77'},
        'Port-channel1.227': {
            'addresses': [IPv4Interface('176.222.18.129/27')],
            'unnumbered': None},
        'Port-channel1.229': {
            'addresses': [IPv4Interface('176.222.18.193/29')],
            'unnumbered': None},
        'Port-channel1.23': {
            'addresses': [IPv4Interface('92.246.214.225/28'),
                          IPv4Interface('92.246.214.145/28')],
            'unnumbered': None}
    }
    '''

    command = "show run | i ^(interface| ip (address|unnumbered))"
    output: str = conn.send_commands(command, waittime=waittime)
    output: str = output.replace("\r\n", "\n").replace("\n ip ", "\t")
    output: str = output.replace("interface ", "")
    intf_dict: dict = {}
    for line in output.split("\n"):
        line = line.split("\t")
        if len(line) > 1:
            intf, *ips = line
            intf_dict[intf] = {"unnumbered": None, "addresses": []}
            for item in ips:
                if "unnumbered" in item:
                    intf_dict[intf]["unnumbered"] = item.replace("unnumbered ",
                                                                 "")
                else:
                    raw_ip = item.replace("address ", "").replace(" secondary",
                                                                  "")
                    ip_intf = ipaddress.ip_interface(raw_ip.replace(" ", "/"))
                    intf_dict[intf]["addresses"].append(ip_intf)
    return intf_dict


def get_normalized_subif_dict(policies_dict: dict,
                              subif_dict: dict,
                              intf_dict: dict) -> dict:

    norm_subif_dict = copy.deepcopy(policies_dict)
    kv_pairs = {
        "input": None,
        "output": None,
        "static": {"cpe": []},
        "connected": {"cpe": []},
        "unnumbered": None}

    for subif in norm_subif_dict.keys():
        for key, value in kv_pairs.items():
            if not norm_subif_dict[subif].get(key):
                norm_subif_dict[subif][key] = copy.deepcopy(value)

    for key in subif_dict.keys():
        mid_dict = {"static": {"cpe": subif_dict[key]}}
        norm_subif_dict[key].update(mid_dict)

    for intf in norm_subif_dict.keys():
        norm_subif_dict[intf].update(intf_dict.get(intf))

    return norm_subif_dict


def update_cisco_full_pmaps_dict(full_pmaps_dict: dict,
                                 pmaps_rate_dict: dict,
                                 cmap_ips_dict: dict) -> dict:

    '''
    {'LEASED_23': {'SRG214146': {'cpe': [IPv4Interface('92.246.214.146/32')],
                                 'rate': {'cir': '5242880',
                                          'measurement': 'bps'}},
                   'SRG214147': {'cpe': [IPv4Interface('92.246.214.147/32')],
                                 'rate': {'cir': '5242880',
                                          'measurement': 'bps'}},
                   'SRG214148': {'cpe': [IPv4Interface('92.246.214.148/32')],
                                 'rate': {'cir': '5242880',
                                          'measurement': 'bps'}},
                   'SRG214149': {'cpe': [IPv4Interface('92.246.214.149/32')],
                                 'rate': {'cir': '5242880',
                                          'measurement': 'bps'}},
                   'SRG214150': {'cpe': [IPv4Interface('92.246.214.150/32')],
                                 'rate': {'cir': '5242880',
                                          'measurement': 'bps'}}},
     'LEASED_499': {'SRG21466': {'cpe': [IPv4Interface('92.246.214.66/32')],
                                 'rate': {'cir': '104857600',
                                          'measurement': 'bps'}},
                    'SRG21467': {'cpe': [IPv4Interface('92.246.214.67/32')],
                                 'rate': {'cir': '104857600',
                                          'measurement': 'bps'}},
                    'SRG21468': {'cpe': [IPv4Interface('92.246.214.68/32')],
                                 'rate': {'cir': '1048576000',
                                          'measurement': 'bps'}}}
    '''

    for pmap, cmaps in full_pmaps_dict.items():
        for cmap in cmaps.keys():
            rate = copy.deepcopy(pmaps_rate_dict[pmap].get(cmap))
            full_pmaps_dict[pmap][cmap]["rate"] = rate
            ip_set = cmap_ips_dict[cmap]
            ips = []
            for ip, wcard in ip_set:
                if not wcard:
                    mask = "255.255.255.255"
                else:
                    mask = convert_wcard_to_netmask(wcard)
                ip_intf = ipaddress.ip_interface(f"{ip}/{mask}")
                ips.append(ip_intf)
            full_pmaps_dict[pmap][cmap]["cpe"] = ips
    return full_pmaps_dict


def flatten_cisco_full_pmaps_dict(full_pmaps_dict: dict) -> dict:
    '''
    Example of flatten_dict:
    {'LEASED_23': [
        [IPv4Interface('92.246.214.146/32'), '5242880bps', 'SRG214146'],
        [IPv4Interface('92.246.214.147/32'), '5242880bps', 'SRG214147'],
        [IPv4Interface('92.246.214.148/32'), '5242880bps', 'SRG214148'],
        [IPv4Interface('92.246.214.149/32'), '5242880bps', 'SRG214149'],
        [IPv4Interface('92.246.214.150/32'), '5242880bps', 'SRG214150']],
    'LEASED_499': [
        [IPv4Interface('92.246.214.66/32'), '104857600bps', 'SRG21466'],
        [IPv4Interface('92.246.214.67/32'), '104857600bps', 'SRG21467'],
        [IPv4Interface('92.246.214.68/32'), '1048576000bps','SRG21468']]}
    '''
    flatten_pmaps = {}
    for pmap, classes in full_pmaps_dict.items():
        cpes = []
        for cmap in classes.keys():
            if not (classes[cmap]["rate"] is None):
                rate = (classes[cmap]["rate"]["cir"] +
                        classes[cmap]["rate"]["measurement"])
            else:
                rate = ""
            for cpe in classes[cmap]["cpe"]:
                cpes.append([cpe, rate, cmap])
        flatten_pmaps[pmap] = cpes
    return flatten_pmaps


def update_cisco_norm_subif_dict_with_cpes(norm_subif_dict: dict,
                                           flatten_pmaps: dict) -> dict:
    updated_dict = copy.deepcopy(norm_subif_dict)
    for subinterface in updated_dict.keys():
        pmap_in = updated_dict[subinterface]["input"]
        pmap_out = updated_dict[subinterface]["output"]
        pmaps = [pmap_in, pmap_out]
        cpes = []
        for pmap in pmaps:
            if pmap and flatten_pmaps.get(pmap):
                cpes += flatten_pmaps[pmap]
        updated_dict[subinterface]["connected"]["cpe"] = cpes
    for key, value in updated_dict.items():
        if len(value["connected"]["cpe"]) < 1 and len(value["addresses"]) > 0:
            conn_cpes = []
            for ip_intf in value["addresses"]:
                for cpe_ip in get_cpe_ips_from_interface(ip_intf):
                    conn_cpes.append([cpe_ip, "", ""])
            updated_dict[key]["connected"]["cpe"] += conn_cpes
    return updated_dict


def get_cpe_ips_from_interface(ip_interface: ipaddress.IPv4Interface) -> list:

    '''
    Takes ipaddress ip_interface object and returns list of ip_interface
    objects with ip addresses of hosts from start ip_interface network.
    Example of all_hosts_intf:
        [IPv4Interface('46.250.88.18/29'),
        IPv4Interface('46.250.88.19/29'),
        IPv4Interface('46.250.88.20/29'),
        IPv4Interface('46.250.88.21/29'),
        IPv4Interface('46.250.88.22/29')]
    '''

    mask = ip_interface.netmask
    all_hosts = list(ip_interface.network.hosts())
    all_hosts.remove(ip_interface.ip)
    all_hosts_intf = list(map(ipaddress.ip_interface,
                              map(lambda x: str(x[0]) + "/" + str(x[1]),
                                  zip(all_hosts, itertools.repeat(mask)))))
    return all_hosts_intf


def get_cisco_list_of_static_hosts(updated_dict: dict) -> list:

    '''
    Returns list of lists of static hosts routes with needed information.
    Elements are:
    ---------------------------------------------------------------------
    | ip | mask | intf | pmap_in | pmap_out | isg | rate | class | type |
    ---------------------------------------------------------------------
    | 1  |  2   |   3  |    4    |    5     |  6  |   7  |   8   |   9  |
    ---------------------------------------------------------------------
    Example of fin_list_static:
    [
        ['10.81.224.2', '255.255.255.255', 'Port-channel1.3000', None,
         'DOMOFON_10M', None, '', '', 'static-route'],
        ['37.208.100.3', '255.255.255.255', 'Port-channel2.40240602', None,
         None, 'B2B_ISG_IP', '', '', 'static-route'],
        ['37.208.100.6', '255.255.255.255', 'Port-channel2.40240604', None,
         None, 'B2B_ISG_IP', '', '', 'static-route'],
        ['37.208.100.2', '255.255.255.255', 'Port-channel2.40240900', None,
         None, 'B2B_ISG_IP', '', '', 'static-route']
    ]
    '''

    fin_list_static = []
    for subif in updated_dict.keys():
        static_cpes = updated_dict[subif]["static"].get("cpe", [])
        pmap_in = updated_dict[subif].get("input")
        pmap_out = updated_dict[subif].get("output")
        isg = updated_dict[subif].get("isg")
        if len(static_cpes) > 0:
            for cpe in static_cpes:
                ip, mask = cpe.split(" ")
                rate = ""
                cmap = ""
                sublist = [ip, mask, subif, pmap_in,
                           pmap_out, isg, rate, cmap, "static-route"]
                fin_list_static.append(sublist)
    return fin_list_static


def get_cisco_list_of_connected_hosts(updated_dict: dict) -> list:

    fin_list_connected = []
    for subif in updated_dict.keys():
        connected_cpes = updated_dict[subif]["connected"].get("cpe", [])
        pmap_in = updated_dict[subif].get("input")
        pmap_out = updated_dict[subif].get("output")
        isg = updated_dict[subif].get("isg")
        if len(connected_cpes) > 0:
            for cpe in connected_cpes:
                intf, rate, cmap = cpe
                ip = str(intf.ip)
                mask = str(intf.netmask)
                sublist = [ip, mask, subif, pmap_in, pmap_out,
                           isg, rate, cmap, "connected"]
                fin_list_connected.append(sublist)
    return fin_list_connected


def generate_cisco_static_hosts_report_dict(target: str,
                                            w_long: int = 60) -> dict:
    conn = NetOperations(target, "cisco")
    conn.establish_connection()
    stat_dict = make_cisco_base_statistics(conn, w_long, w_long)
    conn.close()
    return stat_dict


def make_cisco_static_hosts_report(stat_dict: dict, ip: str) -> None:
    output_filename = (str(datetime.now()).replace(':', '-').replace(' ', '_')
                       + f'-simple-static-hosts-report-{ip}.txt')
    header = ['Network', 'Mask', 'Subinterface', 'Input', 'Output', 'ISG']
    with open(output_filename, 'w') as dst:
        dst.write('\t'.join(header) + '\n')
        for route in stat_dict.keys():
            sif = stat_dict[route]['subif']
            out = stat_dict[route]['output']
            inp = stat_dict[route]['input']
            isg = stat_dict[route]['isg']
            net, mask = route.split(' ')
            line = '\t'.join(map(str, [net, mask, sif, inp, out, isg])) + '\n'
            dst.write(line)
    print('Результат находится в файле ' + output_filename)


def generate_cisco_full_hosts_report_list(conn: NetOperations,
                                          w_short: int = 0.5,
                                          w_long: int = 60) -> list:
    policies_dict = get_cisco_interfaces_policies(conn, w_long)
    subif_dict, _ = get_cisco_routes_by_interfaces(conn, w_long)
    intf_dict = get_cisco_intf_ip_info(conn)
    unique_policies = get_cisco_unique_used_policies(policies_dict)
    unique_classes = get_cisco_unique_used_classes(conn, unique_policies)
    cmap_ips_dict = get_cisco_ips_from_classes(conn, unique_classes, w_short)
    pmaps_rate_dict = get_cisco_rates_in_all_pmaps(conn, unique_policies)
    norm_pmaps_dict = get_cisco_pmaps_with_classes_normalized(conn,
                                                              unique_policies)
    full_pmaps_dict = update_cisco_full_pmaps_dict(norm_pmaps_dict,
                                                   pmaps_rate_dict,
                                                   cmap_ips_dict)
    flatten_pmaps = flatten_cisco_full_pmaps_dict(full_pmaps_dict)
    norm_subif_dict = get_normalized_subif_dict(policies_dict,
                                                subif_dict,
                                                intf_dict)
    updated_dict = update_cisco_norm_subif_dict_with_cpes(norm_subif_dict,
                                                          flatten_pmaps)
    fin_list_static = get_cisco_list_of_static_hosts(updated_dict)
    fin_list_connected = get_cisco_list_of_connected_hosts(updated_dict)
    full_report_list = fin_list_static + fin_list_connected
    return full_report_list


def make_cisco_full_report(full_report_list: list, ip: str) -> None:
    output_filename = (str(datetime.now()).replace(':', '-').replace(' ', '_')
                       + f'-full-report-{ip}.txt')
    header = ["IP", "Mask", "Interface", "PMAP_IN", "PMAP_OUT",
              "ISG", "Rate", "Class", "Type"]
    with open(output_filename, "w") as dst:
        dst.write('\t'.join(header) + '\n')
        for cpe in full_report_list:
            line = "\t".join(list(map(str, cpe))) + "\n"
            dst.write(line)
    print('Результат находится в файле ' + output_filename)

from net_operations import templates_path
from net_operations.lib.script_funcs import hw_report_gen
from net_operations.lib.huawei.acc_users_funcs import get_hw_bas_report_dict
from net_operations.lib.huawei.nat_funcs import get_nat_report_dict
from net_operations.lib.script_funcs import cisco_host_full_report
from net_operations.lib.script_funcs import cisco_host_brief_report


def hw_bas_report():
    template = templates_path + "/bas_report.md.jinja2"
    return hw_report_gen(get_hw_bas_report_dict, template)


def hw_nat_report():
    template = templates_path + "/nat_report.md.jinja2"
    return hw_report_gen(get_nat_report_dict, template)


def cs_host_brief_report():
    return cisco_host_brief_report()


def cs_host_full_report():
    return cisco_host_full_report()

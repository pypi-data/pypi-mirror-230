from dnsdefender.utils.whitelist import check_whitelist


def get_takeover_a_records(dns_records, elastic_ips, whitelist_ips):
    takeovers = []
    for record in dns_records:
        for ip in record["records"]:
            if not check_whitelist(whitelist_ips,ip) and ip not in elastic_ips:
                takeovers.append(record)
    return takeovers


def get_takeover_cnames(cnames, aws_cnames_map):
    takeovers = []
    for cname in cnames:
      if cname['records'][0] not in aws_cnames_map:
        takeovers.append(cname)
    return takeovers
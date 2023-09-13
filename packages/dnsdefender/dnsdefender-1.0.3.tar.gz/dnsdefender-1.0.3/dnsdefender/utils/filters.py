import ipaddress


def filter_ips_by_subnets(ip_list):
    filtered_ips = []
    subnet_list = ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'] #SUBNET_LIST define it globally

    for ip_str in ip_list:
        if(ip_str["type"]!="A"):
            filtered_ips.append(ip_str)
            continue
        ip = ipaddress.ip_address(ip_str["records"][0])
        is_in_subnet = False
        
        for subnet_str in subnet_list:
            subnet = ipaddress.ip_network(subnet_str)
            if ip in subnet:
                is_in_subnet = True
                break
        
        if not is_in_subnet:
            filtered_ips.append(ip_str)
    
    return filtered_ips

def filter_cnames(cname_list):
    cname_map = {}  # Map to store relationships between CNAMEs
    final_cnames = []  # List to store the final CNAMEs

    # Create a map of CNAME relationships
    for entry in cname_list:
        if entry['type'] == 'CNAME':
            cname_map[entry['name']] = {
                'records': entry['records'][0],
                'source': entry['source'],
                'zone_name': entry['zone_name']
            }

    # Identify the final CNAMEs
    for cname, target in cname_map.items():
        if target['records'] not in cname_map:
            final_cnames.append({'type': 'CNAME', 'name': cname, 'records': [target['records']], 'source': target['source'], 'zone_name': target['zone_name']})
    
    return final_cnames

def get_cnames(dns_records):
    cnames = []
    for record in dns_records:
        if record["type"] == "CNAME":
            cnames.append(record)
    return cnames

def get_a_records(dns_records):
    a_records = []
    for record in dns_records:
        if record["type"] == "A":
            a_records.append(record)
    return a_records

def get_aws_cnames_map(ec2_instances, load_balancers, globalaccelerators):
    aws_cnames_map = {}
    for instance in ec2_instances:
        if instance.get("PublicDnsName"):
            aws_cnames_map[instance["PublicDnsName"]] = instance["State"]["Name"]

    for lb in load_balancers:
        if lb.get("DNSName"):
            aws_cnames_map[lb["DNSName"]] = True

    for ga in globalaccelerators:
        if ga.get("DnsName"):
            aws_cnames_map[ga["DnsName"]] = True
    return aws_cnames_map

def get_elastic_ips_map(elastic_ips):
    elastic_ips_map = {}
    for ip in elastic_ips:
        elastic_ips_map[ip] = True
    return elastic_ips_map

def get_ip_fron_ec2_instance(cname):
    ip_part = cname["records"][0].split(".")
    ip = ip_part[0].split("-")[1:5]
    ip = ".".join(ip)
    return ip

def get_ec2_instances_from_cnames(cnames):

    ec2_instances_list = []
    for cname in cnames:
        if cname["records"][0][0:4] == "ec2-":
            ip = get_ip_fron_ec2_instance(cname)
            ec2_instances_list.append({"type": cname["type"], "name": cname["name"], "records": cname["records"], "source": cname["source"], "zone_name": cname["zone_name"], "public_ip": ip})

    return ec2_instances_list

def get_load_balancers_from_cnames(cnames):

    load_balancers_list = []
    for cname in cnames:
        parts = cname["records"][0].split(".")
        for part in parts:
            if(part == 'elb'):
                load_balancers_list.append(cname)
                break

    return load_balancers_list

def get_aws_globalaccelerators_from_cnames(cnames):

    aws_globalaccelerators_list = []
    for cname in cnames:
        parts = cname["records"][0].split(".")
        for part in parts:
            if(part == 'awsglobalaccelerator'):
                aws_globalaccelerators_list.append(cname)
                break

    return aws_globalaccelerators_list


def get_other_entries_from_cnames(cnames, ec2_instances, load_balancers, aws_globalaccelerators):

    ec2_load_balancers_ga_map = {}

    for instance in ec2_instances:
        ec2_load_balancers_ga_map[instance["name"]] = True

    for lb in load_balancers:
        ec2_load_balancers_ga_map[lb["name"]] = True
    
    for ga in aws_globalaccelerators:
        ec2_load_balancers_ga_map[ga["name"]] = True

    other_entries = []

    for cname in cnames:
        if cname["name"] not in ec2_load_balancers_ga_map:
            other_entries.append(cname)

    return other_entries
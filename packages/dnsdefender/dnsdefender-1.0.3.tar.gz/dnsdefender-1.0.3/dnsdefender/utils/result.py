from dnsdefender.utils.whitelist import check_whitelist

def is_takeover_vulnerable(ip, elastic_ips_map, whitelist_ips):
    if not check_whitelist(whitelist_ips, ip) and ip not in elastic_ips_map:
        return True
    else:
        return False

def is_cname_unused(cname, aws_cnames_map):
    if cname["records"][0] not in aws_cnames_map:
        return True
    else:
        return False

def is_instance_stopped(cname, aws_cnames_map):
    if aws_cnames_map[cname["records"][0]] == "stopped":
        return True
    else:
        return False

def compare_old_new_dns_records(old_entries, latest_entries):
    print("Comparing old and new DNS records")
    new_entries = []
    updated_entries = []
    deleted_entries = []

    old_entries_map = {}
    new_entries_map = {}

    for entry in latest_entries:
        new_entries_map[entry["name"]] = entry


    for entry in old_entries:
        old_entries_map[entry["name"]] = entry


    for entry in latest_entries:
        if entry["name"] not in old_entries_map:
            new_entries.append(entry)
        elif entry not in old_entries:
            entry["old_record"] = old_entries_map[entry["name"]]
            updated_entries.append(entry)

    for entry in old_entries:
        if entry["name"] not in new_entries_map:
            deleted_entries.append(entry)

    return new_entries, updated_entries, deleted_entries



def get_unused_records(records_to_check, other_entries, whitelist_ips, elastic_ips_map, aws_cnames_map, old_dns_entries, latest_dns_entries):
    result = {
      "takeovers": [],
      "unused_cnames": [],
      "stopped_ec2": []
    }
    for record in records_to_check:
        if record["type"] == "A":
            if is_takeover_vulnerable(record["records"][0], elastic_ips_map, whitelist_ips):
                result["takeovers"].append(record)
        elif record["type"] == "CNAME":
            if is_cname_unused(record, aws_cnames_map):
                if "public_ip" in record and is_takeover_vulnerable(record["public_ip"], elastic_ips_map, whitelist_ips):
                    result["takeovers"].append(record)
                else:
                    result["unused_cnames"].append(record)
            elif is_instance_stopped(record, aws_cnames_map):
                result["stopped_ec2"].append(record)
    
    for record in other_entries:
        if is_cname_unused(record, aws_cnames_map):
            if is_takeover_vulnerable(record["records"][0], elastic_ips_map, whitelist_ips):
                result["takeovers"].append(record)

    if(len(old_dns_entries) != 0):
        new_entries, updated_entries, deleted_entries = compare_old_new_dns_records(old_dns_entries, latest_dns_entries)
        results = { **result, "updated_entries": updated_entries, "new_entries": new_entries, "deleted_entries": deleted_entries }
    return results

def print_results(results):
    if(len(results["takeovers"]) == 0):
        print("No takeover found!!")
    else:
        print("Takeovers:")
        for record in results["takeovers"]:
            print(record)
    
    if(len(results["unused_cnames"]) == 0):
        print("No unused CNAME found!!")
    else:
        print("Unused CNAMEs:")
        for record in results["unused_cnames"]:
            print(record)


    if(len(results["stopped_ec2"]) == 0):
        print("No stopped EC2 instance found!!")
    else:
        print("Stopped EC2s:")
        for record in results["terminated_ec2"]:
            print(record)

    if(len(results["new_entries"]) == 0):
        print("No new entry found!!")
    else:
        print("New entries:")
        for record in results["new_entries"]:
            print(record)

    if(len(results["updated_entries"]) == 0):
        print("No updated entry found!!")
    else:
        print("Updated entries:")
        for record in results["updated_entries"]:
            print(record)

    if(len(results["deleted_entries"]) == 0):
        print("No deleted entry found!!")
    else:
        print("Deleted entries:")
        for record in results["deleted_entries"]:
            print(record)
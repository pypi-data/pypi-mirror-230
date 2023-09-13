
def get_eips(ec2, region):
    # super annoying, boto3 doesn't have a native paginator class for describe_addresses
    elastic_ips = []
    while True:
        addresses_dict = []
        if addresses_dict and "NextToken" in addresses_dict:
            addresses_dict = client.describe_addresses(
                NextToken=addresses_dict["NextToken"]
            )
        else:
            addresses_dict = ec2.describe_addresses()
        for eip_dict in addresses_dict["Addresses"]:
            elastic_ips.append(eip_dict["PublicIp"])
        if "NextToken" not in addresses_dict:
            break

    nic_paginator = ec2.get_paginator("describe_network_interfaces")
    for resp in nic_paginator.paginate():
        for interface in resp.get("NetworkInterfaces", []):
            if interface.get("Association"):
                nic_public_ip = interface["Association"]["PublicIp"]
                elastic_ips.append(nic_public_ip)
    return elastic_ips
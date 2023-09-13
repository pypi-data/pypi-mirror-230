
route53_zone_records_set = {}

def get_route53_hosted_zones(route53, next_zone=None):
    """Recursively returns a list of hosted zones in Amazon Route 53."""
    if next_zone:
        response = route53.list_hosted_zones_by_name(
            DNSName=next_zone[0], HostedZoneId=next_zone[1]
        )
    else:
        response = route53.list_hosted_zones_by_name()
    hosted_zones = response["HostedZones"]
    # if response is truncated, call function again with next zone name/id
    if response["IsTruncated"]:
        hosted_zones += get_route53_hosted_zones(
            route53, (response["NextDNSName"], response["NextHostedZoneId"])
        )
    return hosted_zones

def get_route53_zone_records(route53, zone_id, next_record=None):
    """Recursively returns a list of records of a hosted zone in Route 53."""
    if next_record:
        response = route53.list_resource_record_sets(
            HostedZoneId=zone_id,
            StartRecordName=next_record[0],
            StartRecordType=next_record[1],
        )
    else:
        response = route53.list_resource_record_sets(HostedZoneId=zone_id)
    zone_records = response["ResourceRecordSets"]

    # if response is truncated, call function again with next record name/id
    if response["IsTruncated"]:
        zone_set_record_key = response["NextRecordName"] + "_" + response["NextRecordType"]
        if zone_set_record_key in route53_zone_records_set == False:
            zone_records += get_route53_zone_records(
                route53, zone_id, (response["NextRecordName"], response["NextRecordType"])
            )
            route53_zone_records_set.add(zone_set_record_key)
    return zone_records

def get_route53_records(route53, zones_to_check):
    dns_records = []
    hosted_zones = get_route53_hosted_zones(route53)
    for zone in hosted_zones:
        if len(zones_to_check)==0 or zone["Name"] in zones_to_check:
            zone_records = get_route53_zone_records(route53, zone["Id"])
            for record in zone_records:
                # we aren't interested in alias records
                if record.get("AliasTarget"):
                    # skip
                    pass
                else:
                    a_records = []
                    for r53value in record["ResourceRecords"]:
                        a_records.append(r53value["Value"])
                    r53_obj = {"type": record["Type"], "name": record["Name"], "records": a_records, "source": "aws_route53", "zone_name": zone["Name"]}
                    dns_records.append(r53_obj)
    return dns_records
import CloudFlare

def get_cloudflare_records(cloudflaretoken, zones_to_check):
    
    cf = CloudFlare.CloudFlare(token=cloudflaretoken, raw=True)
    dns_records = []
    # get zone names
    cloudflare_zones = []
    try:
        page_number = 0
        while True:
            page_number += 1
            raw_results = cf.zones.get(
                params={"per_page": 100, "page": page_number}
            )
            zones = raw_results["result"]
            for zone in zones:
                zone_id = zone["id"]
                zone_name = zone["name"]
                cloudflare_zones.append({"name": zone_name, "id": zone_id})
            total_pages = raw_results["result_info"]["total_pages"]
            if page_number == total_pages:
                break
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit("Failed to retreive zones %d %s - api call failed" % (e, e))
    
    # get dns records for zones

    for zone in cloudflare_zones:
        if(len(zones_to_check)==0 or zone["name"] in zones_to_check):
            try:
                page_number = 0
                while True:
                    page_number += 1
                    raw_results = cf.zones.dns_records.get(
                        zone["id"], params={"per_page": 100, "page": page_number}
                    )
                    cf_dns_records = raw_results["result"]
                    for record in cf_dns_records:
                        if record.get("content"):
                            dns_records.append(
                                {   
                                    "type": record["type"],
                                    "name": record["name"],
                                    "records": [record["content"]],
                                    "source": "cloudflare",
                                    "zone_name": zone["name"]
                                }
                            )
                    total_pages = raw_results["result_info"]["total_pages"]
                    if page_number == total_pages:
                        break
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                exit("Failed to retreive DNS records %d %s - api call failed" % (e, e))
    return dns_records
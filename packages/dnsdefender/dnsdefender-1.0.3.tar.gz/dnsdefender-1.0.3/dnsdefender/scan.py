#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This CLI tool can be used to scan for dangling elastic IPs in your AWS accounts by correlating data
betwen Route53 records and Elastic IPs / IPs in your AWS account.

.. currentmodule:: dnsdefender.scan
.. moduleauthor:: pradhuman_baid 
"""
import csv
import datetime
import sys
import requests
import click
from .__init__ import Info, pass_info
import boto3
import base64
import json as json_lib
import awsipranges
from slack_sdk.webhook import WebhookClient
from botocore.exceptions import ClientError
from dnsdefender.utils.takeover import get_takeover_a_records, get_takeover_cnames
from dnsdefender.aws.ec2 import get_ec2_instances
from dnsdefender.utils.whitelist import parseWhitelistFile, check_whitelist
from dnsdefender.aws.route53 import get_route53_records
from dnsdefender.aws.eips import get_eips
from dnsdefender.aws.lb import get_load_balancers
from dnsdefender.utils.result import get_unused_records, print_results
from dnsdefender.cloudFlare.records import get_cloudflare_records
from dnsdefender.utils.filters import get_cnames, get_a_records, get_aws_cnames_map, get_elastic_ips_map, get_ec2_instances_from_cnames, get_load_balancers_from_cnames, filter_cnames, filter_ips_by_subnets, get_other_entries_from_cnames, get_aws_globalaccelerators_from_cnames
from dnsdefender.utils.old_dns_entries import get_old_dns_entries, update_old_dns_entries
from dnsdefender.aws.globalaccelerator import get_all_global_accelerators
from dnsdefender.utils.constants import Result_keys

@click.group(
    help="Commands that help you scan your AWS account for dangling elastic IPs"
)
@click.pass_context
def cli(ctx: click.Context):
    """CLI handler for scanning actions"""
    pass

# ascii art

logo_b64 = "G1swbSAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAbWzMxbeKWhBtbMW3iloQbWzA7MzFt4paE4paEG1sxbeKWhOKWhOKWhOKWhBtbMG0NCiAgICAgIBtbMW3iloQbWzMybeKWhBtbMzdt4paEG1swbSAgICAbWzE7MzI7NDJt4paAG1szN23iloAbWzQwbeKWhBtbMG0gIBtbMTszMm3iloQbWzM3OzQybeKWgBtbMzJt4paAG1swbSAgICAgICAgICAgICAgG1sxOzMybeKWhOKWhOKWhBtbMzc7NDJt4paAG1szMm3iloAbWzQwbeKWiBtbMG0gIBtbMTszMjs0Mm3iloAbWzM3beKWgBtbMzJt4paEG1szN23iloAbWzBtICAgIBtbMTs0Mm3iloAbWzMyOzQwbeKWiBtbMG0gICAgIBtbMzFt4paEG1sxOzQxbeKWhBtbNDBt4paI4paIG1swOzMxbeKWiOKWgOKWgOKWgOKWiBtbMTs0MW3iloTiloDiloAbWzQwbeKWiOKWhBtbMG0NCiAgIBtbMTszMm3iloQbWzQybeKWgOKWgBtbMDszMm3ilojiloDilogbWzE7NDJt4paAG1szN23iloAbWzMyOzQwbeKWhBtbMG0gG1szMm3ilogbWzE7Mzc7NDJt4paEG1szMjs0MG3ilogbWzBtICAbWzE7MzJt4paIG1swOzMybeKWiBtbMzdtICAgIBtbMzJt4paEG1sxOzM3OzQybeKWgBtbMDszMm3ilogbWzE7Mzc7NDJt4paAG1szMm3iloAbWzM3OzQwbeKWhBtbMG0gICAgG1sxOzMybeKWiBtbMDszMm3ilojilogbWzE7NDJt4paEG1swOzMybeKWiBtbMTs0Mm3iloAbWzA7MzJt4paIG1sxOzM3OzQybeKWgBtbMG0gG1sxOzMyOzQybeKWhBtbMDszMm3ilojiloDilogbWzE7NDJt4paA4paA4paA4paAG1swOzMybeKWiBtbMTs0Mm3iloQbWzBtICAgG1szMW3iloQbWzE7NDFt4paAG1s0M23iloDiloAbWzMzOzQxbeKWhBtbNDBt4paE4paEG1swbSAbWzE7MzNt4paE4paE4paE4paEG1swOzMxbeKWhBtbMTs0MW3iloTiloTiloAbWzQwbeKWiOKWhBtbMG0NCiAgIBtbMTszMm3ilogbWzA7MzJt4paI4paAG1szN20gIBtbMTszMm3iloAbWzQybeKWhOKWhBtbMDszMm3ilogbWzM3bSAbWzMybeKWgOKWiBtbMW3ilogbWzBtICAbWzE7MzI7NDJt4paAG1s0MG3ilpEbWzBtICAgG1sxOzMybeKWiBtbMDszMm3ilojiloAbWzFt4paIG1s0Mm3iloQbWzA7MzJt4paA4paIG1sxOzQybeKWgBtbMG0gIBtbMTszMm3ilogbWzA7MzJt4paIG1sxbeKWkRtbMDszMm3iloDiloQbWzE7Mzdt4paEG1swbSAbWzE7MzJt4paIG1swOzMybeKWiBtbMzdtICAbWzE7MzJt4paAG1swbSAbWzE7MzI7NDJt4paEG1swOzMybeKWiBtbMTszNzs0Mm3iloQbWzMyOzQwbeKWgOKWgBtbMG0gG1sxOzMybeKWgBtbMG0gIBtbMzFt4paI4paIG1sxOzQxbeKWhBtbMDszM23ilojilojilojilogbWzFt4paIG1swbSAbWzMzbeKWiOKWiBtbMTszMTs0M23iloQbWzQwbeKWiBtbMDszMW3ilogbWzMzOzQxbeKWhBtbMTs0M23iloAbWzQxbeKWhBtbMzFt4paEG1s0MG3ilojilogbWzBtDQogIBtbMTszMm3iloQbWzQybeKWgBtbMDszMm3ilogbWzM3bSAgICAgIBtbMzJt4paAG1szN20gIBtbMTszMjs0Mm3iloQbWzA7MzJt4paIG1sxOzQybeKWgOKWgBtbMDszMm3ilogbWzE7NDJt4paEG1swbSAgIBtbMTszMm3ilogbWzM3OzQybeKWhBtbMG0gIBtbMTszMm3iloAbWzBtICAbWzE7MzI7NDJt4paAG1swbSAgIBtbMzJt4paIG1sxbeKWkRtbMDszMm3iloQbWzFt4paE4paEG1swbSAgG1sxOzMybeKWiBtbMG0gICAgG1sxOzMybeKWiBtbMDszMm3ilogbWzE7Mzc7NDJt4paAG1swbSAgICAgG1szMW3ilojilpEbWzFt4paIG1swbSAgG1szM23ilogbWzFt4paIG1swbSAgG1sxOzMxbeKWhBtbMDszMzs0MW3iloAbWzMxOzQwbeKWiBtbMTs0MW3iloAbWzA7MzFt4paAG1szN20gIBtbMzNt4paIG1sxbeKWiBtbMDszMW3ilojilogbWzFt4paIG1swbQ0KICAbWzE7MzJt4paIG1swOzMybeKWiBtbMW3ilpEbWzBtICAbWzE7MzJt4paE4paE4paEG1szN23iloQbWzBtICAgG1sxOzMybeKWiBtbMDszMm3ilojiloAbWzM3bSAbWzMybeKWiBtbMW3ilogbWzBtICAgG1sxOzMybeKWiBtbMDszMm3ilogbWzM3bSAgICAbWzMybeKWiBtbMW3ilogbWzBtICAgIBtbMzJt4paA4paA4paA4paIG1sxOzQybeKWgBtbMG0gICAgIBtbMzJt4paEG1sxOzM3OzQybeKWhBtbMDszMm3ilogbWzFt4paIG1swbSAgICAgG1sxOzMxbeKWiBtbNDFt4paEG1s0MG3ilogbWzBtICAbWzMzbeKWiBtbMW3ilogbWzBtIBtbMzFt4paEG1sxOzQxbeKWgBtbMDszMW3ilogbWzE7NDNt4paAG1swbSAgIBtbMzNt4paE4paIG1sxOzQxbeKWgBtbMzFt4paEG1swOzMxbeKWkRtbMW3ilogbWzBtDQogIBtbMTszMm3ilogbWzA7MzJt4paIG1sxOzM3OzQybeKWgBtbMG0gIBtbMTszMm3iloAbWzA7MzJt4paI4paIG1sxbeKWiBtbMG0gIBtbMTszMm3iloQbWzQybeKWgBtbMDszMm3ilpEbWzM3bSAgG1szMm3ilogbWzFt4paIG1swbSAgICAbWzE7MzI7NDJt4paEG1swOzMybeKWiOKWhBtbMzdtIBtbMzJt4paEG1sxbeKWiBtbMG0gICAbWzMybeKWhBtbMW3iloQbWzBtICAgIBtbMzJt4paIG1szN20gICAgIBtbMTszMm3ilogbWzA7MzJt4paIG1sxbeKWkeKWiBtbMG0gICAgIBtbMzFt4paIG1sxbeKWiBtbNDFt4paAG1swbSAgG1szM23ilogbWzE7MzE7NDNt4paEG1s0MG3ilogbWzQxbeKWgBtbMDszMW3iloAbWzMzbeKWiOKWiBtbMTs0M23iloDiloDiloAbWzA7MzNt4paIG1szN20gG1szMW3ilojilogbWzFt4paIG1swbQ0KICAbWzE7MzJt4paAG1s0Mm3iloQbWzA7MzJt4paIG1sxbeKWhOKWhBtbMDszMm3iloTilpHilojilogbWzE7Mzc7NDJt4paAG1swbSAbWzE7MzJt4paA4paI4paAG1swbSAgG1szMm3ilpHilogbWzE7Mzc7NDJt4paAG1swbSAgIBtbMzJt4paEG1sxbeKWgBtbNDJt4paEG1swOzMybeKWiOKWgBtbMW3iloAbWzBtICAgG1szMm3iloDilogbWzFt4paRG1swOzMybeKWhBtbMTszNzs0Mm3iloAbWzA7MzJt4paIG1sxbeKWiBtbMG0gICAgICAbWzE7MzI7NDJt4paEG1swOzMybeKWiBtbMzdtIBtbMW3iloQbWzBtICAgIBtbMzFt4paR4paIG1sxOzQxbeKWgBtbNDBt4paE4paEG1swOzMxbeKWiBtbMTs0MW3iloAbWzA7MzFt4paIG1szN20gIBtbMzNt4paIG1sxOzQzbeKWhBtbMG0gICAgG1szMW3ilogbWzFt4paI4paAG1swbQ0KIBtbMzJt4paIG1szN20gIBtbMTszMjs0Mm3iloQbWzM3beKWgBtbMzI7NDBt4paIG1swOzMybeKWgBtbMW3iloAbWzQybeKWhBtbMzdt4paEG1szMm3iloQbWzBtICAbWzMybeKWhBtbMzdtICAbWzMybeKWiBtbMTszNzs0Mm3iloQbWzA7MzJt4paIG1sxbeKWiBtbMG0gICAbWzE7MzJt4paAG1swbSAgG1szMm3ilogbWzFt4paEG1swbSAgIBtbMTszMjs0Mm3iloAbWzBtIBtbMzJt4paA4paIG1sxOzQybeKWhOKWhBtbNDBt4paAG1szN23iloAbWzBtICAgICAgG1sxOzMybeKWiBtbMDszMm3ilogbWzM3bSAbWzMybeKWgBtbMzdtICAgICAbWzMxbeKWgOKWkRtbMW3ilogbWzQxbeKWhBtbMDszMW3ilogbWzE7NDFt4paAG1szMzs0M23iloAbWzQwbeKWiBtbMG0gG1szM23ilogbWzFt4paIG1swbSAbWzMxbeKWhBtbMTs0MW3iloQbWzA7MzFt4paIG1sxOzQxbeKWhBtbNDBt4paAG1swbQ0KICAgIBtbMTszMm3iloAbWzQybeKWhBtbMG0gICAbWzE7MzJt4paIG1swOzMybeKWiBtbMW3ilogbWzBtICAbWzMybeKWgBtbMzdtICAbWzE7MzI7NDJt4paEG1szN23iloDiloAbWzMyOzQwbeKWiBtbMzdt4paEG1swbSAgIBtbMzJt4paEG1szN20gG1sxOzMybeKWiBtbMDszMm3ilogbWzE7Mzc7NDJt4paAG1swbSAgICAgG1sxbeKWhBtbMG0gICAgICAgICAgIBtbMTszMjs0Mm3iloQbWzBtICAgICAgICAgG1szMW3iloDiloAbWzE7NDFt4paEG1swOzMxbeKWiBtbMTs0MW3iloAbWzQwbeKWiBtbMDszMW3ilojilojilojilogbWzE7NDFt4paE4paEG1s0MG3iloAbWzBtDQogICAgG1szMm3iloQbWzE7Mzdt4paEG1swbSAgICAbWzMybeKWkRtbMW3ilogbWzBtICAgICAbWzE7MzJt4paAG1s0Mm3iloTiloQbWzA7MzJt4paA4paAG1szN20gIBtbMTszMm3iloDiloAbWzBtICAbWzE7MzJt4paAG1swbSAgICAgICAbWzE7MzJt4paEG1swbSAgICAgICAgICAgICAgICAgICAgICAgIBtbMTszMW3iloDiloAbWzA7MzFt4paAG1sxbeKWgOKWgOKWgOKWgBtbMG0NCiAgICAbWzMybeKWgOKWgBtbMzdtICAgIBtbMzJt4paIG1sxbeKWgBtbMG0gICAgIBtbMTszMm3iloQbWzBtIBtbMTszMm3iloQbWzA7MzJt4paEG1sxOzM3beKWhBtbMDszMm3iloQbWzFt4paE4paEG1szN23iloQbWzBtICAbWzE7MzI7NDJt4paA4paAG1szN23iloQbWzBtICAgICAgG1szMm3iloTilogbWzE7Mzc7NDJt4paAG1szMjs0MG3ilogbWzA7MzJt4paEG1sxOzM3beKWhBtbMzJt4paEG1swbSAbWzE7MzI7NDJt4paEG1swOzMybeKWiBtbMTszNzs0Mm3iloAbWzA7MzJt4paIG1sxOzM3OzQybeKWgBtbMzJt4paAG1swOzMybeKWiBtbMTs0Mm3iloAbWzQwbeKWiBtbMG0gG1sxOzMybeKWhOKWhOKWhBtbMDszMm3iloTilojilogbWzE7Mzc7NDJt4paAG1swbSAgG1sxOzMybeKWiBtbNDJt4paA4paAG1szN23iloAbWzMybeKWgBtbMzc7NDBt4paEG1swbQ0KICAgICAbWzE7MzI7NDJt4paEG1swbSAgIBtbMzJt4paIG1sxbeKWiBtbMzdt4paEG1swbSAgICAgIBtbMzJt4paEG1sxOzQybeKWgBtbMDszMm3ilojilojiloDiloDilogbWzE7Mzc7NDJt4paAG1szMm3iloAbWzBtIBtbMTszMm3ilogbWzA7MzJt4paI4paIG1szN20gIBtbMzJt4paIG1sxOzQybeKWgBtbMzc7NDBt4paIG1swbSAbWzMybeKWiOKWiBtbMW3ilojilojiloDiloAbWzM3beKWgBtbMG0gG1sxOzMybeKWgBtbNDJt4paEG1swbSAbWzE7MzJt4paIG1swOzMybeKWiOKWiBtbMzdtICAbWzMybeKWgBtbMzdtIBtbMTszMjs0Mm3iloQbWzM3beKWgBtbMDszMm3iloDiloAbWzFt4paA4paA4paIG1swbSAgG1sxOzMybeKWiOKWkRtbMG0gIBtbMzJt4paA4paIG1szN20NCiAgICAbWzE7MzJt4paEG1swbSAgICAbWzMybeKWgBtbMW3ilogbWzBtICAgICAgIBtbMTszMm3iloQbWzBtIBtbMzJt4paIG1sxOzQybeKWgBtbMDszMm3iloTiloTilojilogbWzFt4paAG1swbSAbWzE7MzI7NDJt4paAG1swOzMybeKWiBtbMTszNzs0Mm3iloAbWzBtICAbWzE7MzJt4paAG1swOzMybeKWiOKWiBtbMzdtICAbWzMybeKWgOKWgOKWiBtbMTs0Mm3iloAbWzQwbeKWhBtbMG0gICAgIBtbMTszMm3ilpHilojilogbWzBtICAgG1sxOzMybeKWhBtbNDJt4paAG1swOzMybeKWiOKWiBtbMTs0Mm3iloAbWzQwbeKWiBtbMG0gICAbWzE7MzJt4paEG1swOzMybeKWiOKWiOKWiBtbMTszNzs0Mm3iloAbWzA7MzJt4paI4paIG1szN20NCiAgICAgICAgICAgICAgICAgIBtbMzJt4paAG1szN20gG1szMm3ilogbWzE7NDJt4paEG1swOzMybeKWgBtbMW3iloDilojilpEbWzA7MzJt4paEG1szN20gG1sxOzMybeKWiBtbMDszMm3ilogbWzFt4paRG1swbSAgIBtbMTszMm3ilogbWzA7MzJt4paIG1szN20gICAgIBtbMzJt4paA4paI4paIG1sxOzM3beKWhBtbMG0gICAbWzE7MzJt4paRG1szN23ilogbWzA7MzJt4paI4paEG1szN20gIBtbMTszMjs0Mm3iloDiloQbWzA7MzJt4paIG1sxbeKWiBtbMG0gICAgIBtbMTszMm3ilogbWzM3OzQybeKWhBtbMDszMm3ilojiloQbWzFt4paAG1s0Mm3iloQbWzA7MzJt4paEG1szN20NCiAgICAgICAgICAbWzE7MzJt4paAG1swbSAgICAgG1sxOzMybeKWhBtbNDJt4paEG1swOzMybeKWgBtbMzdtIBtbMzJt4paIG1sxbeKWiBtbMG0gIBtbMTszMm3ilogbWzA7MzJt4paIG1sxOzQybeKWhBtbMG0gIBtbMTszMm3iloAbWzA7MzJt4paIG1sxOzQybeKWgOKWgOKWgBtbMDszMm3ilogbWzE7NDJt4paEG1swbSAbWzE7MzJt4paIG1s0Mm3iloAbWzBtICAgG1sxOzMybeKWkRtbMDszMm3ilogbWzE7NDJt4paAG1s0MG3iloQbWzBtICAbWzE7MzJt4paRG1swOzMybeKWiBtbMTs0Mm3iloQbWzBtICAgG1szMm3ilogbWzE7Mzc7NDJt4paAG1szMjs0MG3ilogbWzM3OzQybeKWhBtbMDszMm3ilojilogbWzE7NDJt4paAG1s0MG3ilogbWzBtIBtbMzJt4paI4paIG1sxbeKWiOKWkRtbMG0gG1sxOzMybeKWgBtbMDszMm3ilogbWzE7Mzc7NDJt4paAG1szMjs0MG3iloQbWzBtDQogICAgICAgICAgG1szMm3iloAbWzM3bSAgICAgG1szMm3ilogbWzFt4paI4paE4paEG1swOzMybeKWiBtbMTs0Mm3iloAbWzA7MzJt4paE4paE4paIG1sxOzQybeKWhBtbNDBt4paIG1swbSAbWzE7NDJt4paAG1swbSAbWzMybeKWgOKWiBtbMTs0Mm3iloQbWzQwbeKWgBtbNDJt4paEG1swOzMybeKWgBtbMzdtIBtbMTszMm3ilogbWzA7MzJt4paIG1sxOzQybeKWgOKWgBtbMDszMm3ilogbWzE7Mzc7NDJt4paEG1swOzMybeKWiOKWiBtbMTszNzs0Mm3iloAbWzBtICAbWzE7MzJt4paIG1s0Mm3iloQbWzBtIBtbMTszMm3iloAbWzBtICAgG1szMm3ilojiloDiloDiloQbWzFt4paAG1swOzMybeKWhBtbMTs0Mm3iloQbWzBtICAbWzE7MzJt4paIG1s0Mm3iloQbWzQwbeKWkRtbMG0gIBtbMTszMm3iloDilogbWzA7MzJt4paIG1sxOzM3beKWgBtbMG0NCiAgICAgICAgICAgICAgICAbWzE7MzI7NDJt4paEG1swOzMybeKWiOKWiBtbMTszNzs0Mm3iloAbWzMybeKWgBtbMzdt4paA4paAG1szMm3iloAbWzM3beKWgBtbMDszMm3ilogbWzM3bSAgICAgG1sxOzMyOzQybeKWhBtbMG0gIBtbMW3iloQbWzBtICAbWzE7MzI7NDJt4paAG1swOzMybeKWiOKWiBtbMTszNzs0Mm3iloAbWzMybeKWgOKWgBtbMDszMm3iloAbWzM3bSAbWzE7MzI7NDJt4paAG1swbSAgG1szMm3iloQbWzM3bSAbWzE7NDJt4paAG1swbSAgICAgG1sxOzQybeKWgBtbMG0gICAbWzE7MzJt4paA4paAG1swbSAbWzE7MzJt4paAG1swbSAbWzE7MzJt4paIG1s0Mm3iloQbWzQwbeKWiBtbMG0gIBtbMTszMm3iloAbWzBtDQogICAgICAgICAgICAgICAgIBtbMTszMm3iloDiloAbWzA7MzJt4paA4paAG1sxbeKWgOKWgOKWgBtbMG0gG1sxOzMybeKWhBtbMG0gICAgIBtbMTszMm3iloQbWzBtICAbWzMybeKWgBtbMzdtICAbWzMybeKWiBtbMzdtIBtbMTszMm3iloAbWzA7MzJt4paIG1sxOzQybeKWhBtbMG0gG1szMm3iloQbWzM3bSAbWzE7MzJt4paAG1swbSAgG1sxOzMybeKWgBtbMG0gICAgICAgICAgICAgICAbWzE7MzJt4paAG1s0Mm3iloQbWzQwbeKWgBtbMG0NCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAbWzMybeKWhBtbMzdtICAbWzE7MzJt4paA4paAG1swbSAbWzE7MzJt4paAG1swbSAgICAgICAgICAgICAgICAgICAgICAbWzE7NDJt4paAG1swbQ0KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAbWzE7MzJt4paAG1swbQ0KDQo="
json_output = False


def log(text):
    if not json_output:
        click.echo(text)

def send_webhook(slackwebhook, results):
    webhook = WebhookClient(url=slackwebhook)
    from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler

    rate_limit_handler = RateLimitErrorRetryHandler(max_retry_count=1)
    webhook.retry_handlers.append(rate_limit_handler)

    payload = ""

    # iteratively print all keys of results object
    for key in results:
        if(len(results[key]) == 0):
            print("No {} found!!".format(Result_keys[key]))
        else:
            if(payload == ""):
                payload = "```"
            payload = payload + "{}:".format(Result_keys[key])
            payload = payload + "\n"
            # _ = webhook.send(text=payload)
            for record in results[key]:
                payload = payload + "Name: {}  Record: {} Source: {}".format(record["name"], record["records"], record["source"])
                if("old_record" in record):
                    payload = payload + " Old Record: {}".format(record["old_record"]["records"])
                #Add new line in payload
                payload = payload + "\n"
                # _ = webhook.send(text=payload)
    if(payload != ""):
        payload = payload + "```"
        payload = payload + "\n"
        payload = payload + "<@U04G7FPEC6T>"
        payload = payload + " <@U03E41H1BE1>"
        _ = webhook.send(text=payload)


def get_record_value(record):
    """Return a list of values for a hosted zone record."""
    # test if record's value is Alias or dict of records
    try:
        value = [
            ":".join(
                [
                    "ALIAS",
                    record["AliasTarget"]["HostedZoneId"],
                    record["AliasTarget"]["DNSName"],
                ]
            )
        ]
    except KeyError:
        value = []
        for v in record["ResourceRecords"]:
            value.append(v["Value"])
    return value

def try_record(test, record):
    """Return a value for a record"""
    # test for Key and Type errors
    try:
        value = record[test]
    except KeyError:
        value = ""
    except TypeError:
        value = ""
    return value

def assume_role(role_arn):
    session = boto3.Session()
    sts = session.client("sts")
    assumed_role_object = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName="dnsdefender-session"
    )
    assumed_role_credentials = assumed_role_object["Credentials"]

    return boto3.Session(
        aws_access_key_id=assumed_role_credentials["AccessKeyId"],
        aws_secret_access_key=assumed_role_credentials["SecretAccessKey"],
        aws_session_token=assumed_role_credentials["SessionToken"]
    )

def get_all_account_ids(organisation_lookup_role_arn):
    account_ids = []
    session = assume_role(organisation_lookup_role_arn)
    organizations = session.client("organizations")

    def add_account_ids(list_accounts_response):
        for account in list_accounts_response["Accounts"]:
            account_ids.append(account["Id"])

    response = organizations.list_accounts()
    add_account_ids(response)
    while "NextToken" in response:
        response = organizations.list_accounts(NextToken=response["NextToken"])
        add_account_ids(response)
    return account_ids


@click.option(
    "--regions", default="us-east-1", help="Comma delimited list of regions to run on."
)
@click.option(
    "--exclude", default="", help="Comma delimited list of profile names to exclude."
)
@click.option(
    "--allregions",
    default=False,
    is_flag=True,
    help="Run on all regions.",
)
@click.option(
    "--cloudflaretoken",
    default="",
    help="Pull DNS records from Cloudflare, provide a CF API token.",
)
@click.option(
    "--records",
    required=False,
    type=click.Path(exists=True),
    help="Manually specify DNS records to check against. dnsdefender will check these IPs after checking retrieved DNS "
         "records. See records.csv for an example.",
)
@click.option(
    "--slackwebhook",
    default="",
    help="Specify a Slack webhook URL to send notifications about potential takeovers. Slack workflow variable must be"
         "named 'text'",
)
@click.option(
    "--json",
    default=False,
    is_flag=True,
    help="Only return a JSON object.",
)
@click.option(
    "--skipascii",
    default=False,
    is_flag=True,
    help="Skip printing the ASCII art when starting up dnsdefender.",
)
@click.option(
    "--profile",
    default="",
    help="Specify a specific AWS profile to run dnsdefender on.",
)
@click.option(
    "--roles",
    required=False,
    type=click.Path(exists=True),
    help="Specify CSV filename with AWS account IDs to run dnsdefender on. Each account must have dnsdefender role "
         "assumable by dnsdefender ec2/lambda/whatever is running dnsdefender. Role name: dnsdefenderTargetAccountRole."
         " See roles.csv for example.",
)
@click.option(
    "--autoroles",
    default="",
    required=False,
    help="Like --roles, but finds all organisation accounts automatically. The argument value should be ARN of a role "
         "with organizations:ListAccounts and organizations:DescribeAccount. Ec2/lambda/whatever is running dnsdefender"
         " must have permissions to assume the organisation lookup role."
)
@click.option(
    "--whitelist", default="", help="Specify filepath having list of IPs to whitelist"
)
@click.option(
    "--olddnsentries", default="", help="Specify filepath having list of old DNS entries"
)
@click.option(
    "--zones", default="", help="Comma delimited list of zones to run on.",
    required=False,
)
@cli.command(help="Scan for dangling elastic IPs inside your AWS accounts.")
@pass_info
def aws(
    _: Info,
    regions: str,
    exclude: str,
    allregions: bool,
    cloudflaretoken: str,
    records: str,
    slackwebhook: str,
    skipascii: str,
    profile: str,
    roles: str,
    autoroles: str,
    json: bool,
    whitelist: str,
    zones: str,
    olddnsentries: str,
    ):
    """Scan for dangling elastic IPs inside your AWS accounts."""
    # ascii art
    # if not skipascii and not json:
    #     sys.stdout.write(base64.b64decode(logo_b64).decode('utf-8'))
    
    global json_output
    json_output = json
        
    session = boto3.Session()
    profiles = session.available_profiles
    if zones != "":
        zones = zones.split(",")
    else:
        zones = []
    if exclude != "":
        exclude_list = exclude.split(",")
        for excluded_profile in exclude_list:
            profiles.remove(excluded_profile)
    if profile != "":
        profiles = [profile]

    account_ids = []
    if roles:
        account_ids = [account_id["account_id"] for account_id in csv.DictReader(open(roles, "r"))]
    elif autoroles:
        log("Finding accounts automatically using role: {0}".format(autoroles))
        account_ids = get_all_account_ids(autoroles)
        log("Found {0} accounts in the organisation.".format(len(account_ids)))

    dns_records = []
    # collection of records from cloudflare
    if cloudflaretoken != "":
        log("Obtaining all zone names from Cloudflare.")
        cf_dns_records = get_cloudflare_records(cloudflaretoken, zones)
        dns_records = dns_records + cf_dns_records
        log("Obtained {0} DNS records so far.".format(len(dns_records)))

    # collection of records from r53 using profiles
    for profile in profiles:
        profile_session = boto3.session.Session(profile_name=profile)
        route53 = profile_session.client("route53")
        log("Obtaining Route53 hosted zones for AWS profile: {0}.".format(profile))
        dns_records.extend(get_route53_records(route53, zones))

    ec2_instances = []

    for profile in profiles:
        try:
            session = boto3.Session(profile_name=profile)
            ec2 = session.client("ec2")
            print("Obtaining EC2 instances for AWS profile:", profile)
            
            ec2_instances.extend(get_ec2_instances(ec2))
        except Exception as e:
            print("Error occurred for profile:", profile)
            print(e)

    log("Obtained {0} DNS records so far.".format(len(dns_records)))
    load_balancers = []

    for profile in profiles:
        try:
            session = boto3.Session(profile_name=profile)
            elbv2 = session.client("elbv2")
            elb = boto3.client('elb')
            print("Obtaining Load Balancers for AWS profile:", profile)
                
            load_balancers.extend(get_load_balancers(elbv2, elb))
        except Exception as e:
            print("Error occurred for profile:", profile)
            print(e)


    log("Obtained {0} Load Balancers so far.".format(len(load_balancers)))



    global_accelerators = []

    for profile in profiles:
        session = boto3.session.Session(region_name="us-west-2")
        globalaccelerator = session.client("globalaccelerator")
        print("Obtaining Global Accelerators for AWS profile:", profile)
        global_accelerators.extend(get_all_global_accelerators(globalaccelerator))


    log("Obtained {0} Global Accelerators so far.".format(len(global_accelerators)))

    aws_cnames_map = get_aws_cnames_map(ec2_instances, load_balancers, global_accelerators)



    # collection of IPs
    if allregions:
        ec2 = boto3.client("ec2")
        aws_regions = [
            region["RegionName"] for region in ec2.describe_regions()["Regions"]
        ]
    else:
        aws_regions = regions.split(",")

    whitelist_ips = parseWhitelistFile(whitelist)
    elastic_ips = []
    # collect elastic compute addresses / EIPs for all regions
    for region in aws_regions:
        for profile in profiles:
            log("Obtaining EIPs for region: {}, profile: {}".format(region, profile))
            profile_session = boto3.session.Session(profile_name=profile)
            ec2 = profile_session.client("ec2", region_name=region)
            elastic_ips.extend(get_eips(ec2=ec2, region=region))
        for account_id in account_ids:
            log("Obtaining EIPs for region: {}, account ID: {}".format(region, account_id))
            role_arn = "arn:aws:iam::{0}:role/dnsdefenderTargetAccountRole".format(account_id)
            try:
                role_session = assume_role(role_arn)
            except ClientError as error:
                log("Failed to assume role {0}, skipping it. Error: {1}".format(role_arn, error))
                continue

            ec2 = role_session.client("ec2", region_name=region)
            elastic_ips.extend(get_eips(ec2=ec2, region=region))

    unique_ips = list(set(elastic_ips))
    log("Obtained {0} unique elastic IPs from AWS.".format(len(unique_ips)))
    elastic_ips_map = get_elastic_ips_map(unique_ips)

    # find all DNS records that point to EC2 IP addresses


    old_dns_records = get_old_dns_entries(olddnsentries)
    dns_ec2_ips = filter_ips_by_subnets(dns_records)
    records_to_check = []
    a_records = get_a_records(dns_ec2_ips)
    records_to_check.extend(a_records)

    total_cname_records = get_cnames(dns_ec2_ips)
    filtered_cname_records = filter_cnames(total_cname_records)
    ec2_instances = get_ec2_instances_from_cnames(filtered_cname_records)
    load_balancers = get_load_balancers_from_cnames(filtered_cname_records)
    aws_globalaccelerators = get_aws_globalaccelerators_from_cnames(filtered_cname_records)
    other_entries = get_other_entries_from_cnames(filtered_cname_records, ec2_instances, load_balancers, aws_globalaccelerators)
    records_to_check.extend(ec2_instances)
    records_to_check.extend(load_balancers)
    records_to_check.extend(aws_globalaccelerators)

    results = get_unused_records(records_to_check, other_entries, whitelist_ips, elastic_ips_map, aws_cnames_map, old_dns_records, a_records+total_cname_records)
    update_old_dns_entries(olddnsentries, a_records+total_cname_records)
    print_results(results)

    # check if manually specified A records exist in AWS acc (eips/public ips)
    if records:
        with open(records, "r") as fp:
            csv_reader = csv.DictReader(fp)
            for row in csv_reader:
                aws_metadata = aws_ip_ranges.get(row["record"])
                if aws_metadata:
                    for service in aws_metadata.services:
                        if service == "EC2":
                            if(not check_whitelist(whitelist_ips,row["record"])):
                                if row["record"] not in elastic_ips:
                                    takeover_obj = {
                                        "name": row["name"],
                                        "records": [row["record"]],
                                    }
                                    takeovers.append(takeover_obj)
                                    log("Takeover possible: {}".format(takeover_obj))

    # if len(takeovers) == 0:
    #     log("No takeovers detected! Nice work.")
    if json:
        click.echo(json_lib.dumps(takeovers, indent=2))

    # send slack webhooks, with retries in case of 429s
    if slackwebhook != "":
        send_webhook(slackwebhook, results)

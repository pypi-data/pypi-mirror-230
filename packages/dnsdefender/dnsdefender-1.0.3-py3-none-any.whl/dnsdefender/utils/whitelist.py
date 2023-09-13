def check_whitelist(whitelist_ips,record):
    if record in whitelist_ips:
        return True
    else:
        return False

def parseWhitelistFile(whitelist):
    whitelist_ips = []
    if whitelist != "" :
        with open(whitelist,"r") as f:
            for line in f:
                line.replace(" ","")
                line=line[:-1]
                whitelist_ips.append(line)

    return whitelist_ips
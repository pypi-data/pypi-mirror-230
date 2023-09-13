def get_load_balancers(elbv2_client, elb_client):
    load_balancers = []
    next_marker = None
    
    while True:
        params = {'PageSize': 100}
        if next_marker:
            params['Marker'] = next_marker
        
        response = elb_client.describe_load_balancers(**params)
        # print(response)
        load_balancers.extend(response['LoadBalancerDescriptions'])
        
        if 'NextMarker' in response:
            next_marker = response['NextMarker']
        else:
            break
    
    while True:
        params = {'PageSize': 100}
        if next_marker:
            params['Marker'] = next_marker
        
        response = elbv2_client.describe_load_balancers(**params)
        # print(response)
        load_balancers.extend(response['LoadBalancers'])
        
        if 'NextMarker' in response:
            next_marker = response['NextMarker']
        else:
            break

    return load_balancers
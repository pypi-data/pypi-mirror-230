def get_ec2_instances(ec2_client):
    instances = []
    next_token = None
    while True:
        params = {'MaxResults': 100}
        if next_token:
            params['NextToken'] = next_token
        
        response = ec2_client.describe_instances(**params)
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append(instance)

        if 'NextToken' in response:
            next_token = response['NextToken']
        else:
            break
            
    return instances
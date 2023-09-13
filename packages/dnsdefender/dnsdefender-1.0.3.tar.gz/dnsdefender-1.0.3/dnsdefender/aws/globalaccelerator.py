def get_all_global_accelerators(globalaccelerator_client):
  accelerators = []
  next_token = None
    
  while True:
    params = {'MaxResults': 100}
    if next_token:
      params['NextToken'] = next_token
        
    response = globalaccelerator_client.list_accelerators(**params)
    accelerators.extend(response['Accelerators'])
        
    if 'NextToken' in response:
      next_token = response['NextToken']
    else:
      break
  return accelerators
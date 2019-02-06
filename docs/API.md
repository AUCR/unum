# UNUM API

## Example Upload Python Code
    import json
    import requests
    API_URL = 'http://0.0.0.0:5000'
    API_KEY = 'CRyPP50DBJUlMCxNrcNmGAv8i3cZkQU+799KmojUdtBpKVpml3DBZRy4qlE76YTYg8kkDODoCLQ2dha4L76D8w=='
    file_name = "some_mal_file"
    headers = {'Authorization': 'Bearer ' + API_KEY}
    with open(file_name, 'rb') as fp:
        file_data = fp.read()
    payload = {'filename': str(file_name), 'group_access': 2, 'description': "APIUpload", 'classification': 1}
    response = requests.post('{}/api/unum_file_upload/'.format(
        API_URL), headers=headers, data=file_data, params=payload)
    test = json.loads(response.text)
    print(json.dumps(test, indent=4, sort_keys=True))

It should return data like
    
    {
    "file_id": 22,
    "md5": "12e8f6658618e9169958802fa261ef42"
    }
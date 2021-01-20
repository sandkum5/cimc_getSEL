import requests
from pprint import pprint
import json


def get_token(imc_ip):
    """
    Authenticate and get OAuth token
    """
    user = "admin"
    password = "password" 
    url = f"https://{imc_ip}/redfish/v1/SessionService/Sessions"
    payload = { "UserName": user, "Password": password}
    headers = {'Content-Type': 'application/json'}
    response = requests.request(
        "POST", url, headers=headers, data=json.dumps(post_body), verify=False)
    token = response.headers['X-Auth-Token']
    return token


def get_response(url, token):
    """
    Function to execute get requests using OAuth token
    """
    auth_value = f"OAuth {token}"
    headers = {'Authorization': auth_value}
    response = requests.request("GET", url, headers=headers, verify=False)
    return response


def get_sel_log_count(imc_ip, token):
    """
    Get the SEL log count 
    """
    url = f"https://{imc_ip}/redfish/v1/Chassis/1/LogServices/SEL/Entries/?$top=1"
    response = get_response(url, token)
    json_data = json.loads(response.text)
    count = int(json_data['Members'][0]['EventId'])
    return count


def get_latest_200_logs(imc_ip, token):
    """
    Get latest 200 SEL log entries 
    """
    url = f"https://{imc_ip}/redfish/v1/Chassis/1/LogServices/SEL/Entries/?$top=200"
    response = get_response(url, token)
    return response


def get_sel_logs(imc_ip, token, count):
    """
    Get all the SEL logs
    """
    # url = f"https://{imc_ip}/redfish/v1/Chassis/1/LogServices/SEL/Entries/?$skip=200&$top=200"
    loop_count = (count // 200) + 1
    for x in range(loop_count):
        skip_value = x * 200
        url = f"https://{imc_ip}/redfish/v1/Chassis/1/LogServices/SEL/Entries/?$skip={skip_value}&$top=200"
        response = get_response(url, token)
        pprint(response.text)


def clear_sel_logs(imc_ip, token):
    """
    Clear SEL Log Buffer in CIMC
    """
    url = f"https://{imc_ip}/redfish/v1/Chassis/1/LogServices/SEL/Actions/LogService.ClearLog"
    payload = "{}"
    headers = {'Content-Type': 'text/plain'}
    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False)
    print(response.status_code)


def print_message(response):
    """
    Print function to output SEL logs 
    """
    json_data = json.loads(response.text)
    for i in range(len(json_data['Members'])):
        id = json_data['Members'][i]["Id"]
        message = json_data['Members'][i]["Message"]
        timestamp = json_data['Members'][i]["EventTimestamp"]
        EntryCode = json_data['Members'][i]["EntryCode"]
        Severity = json_data['Members'][i]["Severity"]
        print(f"{id} : {Severity} : {timestamp} : {EntryCode} : {message}")


def main():
    """
    Login to CIMC using Redfish API
    Use OAuth token to get the total SEL log entries
    Pull SEL logs
    Clear SEL logs 
    """
    imc_ip = "x.x.x.x"
    token = get_token(imc_ip)
    count = get_sel_log_count(imc_ip, token)
    get_sel_logs(imc_ip, token, count)
    #clear_sel_logs(imc_ip, token)


if __name__ == '__main__':
    main()


'''
Sample Output:
In [83]: json_data
Out[83]: 
{'Members': [{'EntryCode': 'Device Inserted / Device Present',
   'EventTimestamp': '2020-10-05 15:43:24 UTC',
   'Id': '3629',
   'EntryType': 'SEL',
   'Name': 'Log Entry 3629',
   'EventType': 'ResourceAdded',
   'EventId': '3629',
   'Message': 'BIOS_POST_CMPLT: Presence sensor, Device Inserted / Device Present was asserted',
   'Description': 'Log Entry 3629',
   'Severity': 'Normal',
   '@odata.id': '/redfish/v1/Chassis/1/LogServices/SEL/Entries//3629',
   'Created': '2020-10-05 15:43:24 UTC'},
  {'EntryCode': 'State Asserted',
   'EventTimestamp': '2020-10-05 15:43:23 UTC',
   'Id': '3628',
   'EntryType': 'SEL',
   'Name': 'Log Entry 3628',
   'EventType': 'StatusChange',
   'EventId': '3628',
   'Message': 'System Software event: System Event sensor, OEM System Boot Event was asserted',
   'Description': 'Log Entry 3628',
   'Severity': 'Normal',
   '@odata.id': '/redfish/v1/Chassis/1/LogServices/SEL/Entries//3628',
   'Created': '2020-10-05 15:43:23 UTC'},
'''

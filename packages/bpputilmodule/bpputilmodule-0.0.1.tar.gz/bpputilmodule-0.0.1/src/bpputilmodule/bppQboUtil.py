import json
import requests


def send_to_qbo_pathfix(pathfix_user_id, pathfix_public_key, pathfix_private_key, qbo_url, method):
    pathfix_url = "https://labs.pathfix.com/oauth/method/quickbooks/call?user_id=" + pathfix_user_id + "&public_key=" + pathfix_public_key + "&private_key=" + pathfix_private_key

    payload = json.dumps({
        "url": qbo_url,
        "method": method,
        "headers": {
            "accept": "application/json",
            "x-pinc-response-data-at": "rows.0"
        }
    })
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", pathfix_url, headers=headers, data=payload)
    response_json = response.json()
    # pathfix_status_code = response_json['statusCode']

    # if (pathfix_status_code == '200'):
    #     query_response_object = response_json['data']['QueryResponse']['CompanyInfo'][0]
    # else:
    #     query_response_object = response_json

    return response_json

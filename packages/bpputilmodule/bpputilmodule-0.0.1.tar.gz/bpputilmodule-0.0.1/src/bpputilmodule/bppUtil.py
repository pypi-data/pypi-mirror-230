import json
import requests

def list_of_providers():
    return {"quickbooks", "qbo", "xero", "freshbooks", "fb"}

def list_of_methods():
    return {"FETCH", "CREATE", "REMOVE"}

def decode_response_body(response_json):
    return json.loads((response_json['Payload'].read()).decode('utf-8'))['body']







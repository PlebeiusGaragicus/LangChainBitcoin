import requests

# Replace these variables with your actual values
url = "https://cad9f3dc-360d-49d9-b9e3-5c868510e369-00-1zslnuhag6k0c.riker.replit.dev:8080/v1/getinfo"
macaroon = "your_hex_encoded_macaroon"
cert_path = "/path/to/your/tls.cert"

# Prepare the headers with the macaroon
headers = {
    "Grpc-Metadata-macaroon": macaroon,
}

# It's important to verify with the TLS certificate LND uses, which is usually named tls.cert
response = requests.get(url, headers=headers, verify=cert_path)

# Check the response
if response.status_code == 200:
    print("Connection successful!")
    print("Node info:", response.json())
else:
    print("Failed to connect to the node. Status code:", response.status_code)
    print("Error message:", response.text)

import json

# Read the JSON file
with open("input.json", "r") as file:
    data = json.load(file)

# Extract the required information
address = data["outbounds"][0]["settings"]["servers"][0]["address"]
password = data["outbounds"][0]["settings"]["servers"][0]["password"]
port = data["outbounds"][0]["settings"]["servers"][0]["port"]
security = data["outbounds"][0]["streamSettings"]["security"]
sni = data["outbounds"][0]["streamSettings"]["realitySettings"]["serverName"]
fp = data["outbounds"][0]["streamSettings"]["realitySettings"]["fingerprint"]
pbk = data["outbounds"][0]["streamSettings"]["realitySettings"]["publicKey"]
sid = data["outbounds"][0]["streamSettings"]["realitySettings"]["shortId"]
spx = data["outbounds"][0]["streamSettings"]["realitySettings"]["spiderX"]

# Construct the link
link = f"trojan://{password}@{address}:{port}?security={security}&sni={sni}&fp={fp}&pbk={pbk}&sid={sid}&spx={spx}&type=grpc#reality-trojan-{port}"

# Print the resulting link
print(link)

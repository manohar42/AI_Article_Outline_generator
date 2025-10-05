import http.client
import json

conn = http.client.HTTPSConnection("google.serper.dev")
payload = json.dumps({
  "q": "Reasons for heartattack."
})
headers = {
  'X-API-KEY': 'b5ceb315b7f0dd1589de5fc301d4b7cb7bba3b4f',
  'Content-Type': 'application/json'
}
conn.request("POST", "/search", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))

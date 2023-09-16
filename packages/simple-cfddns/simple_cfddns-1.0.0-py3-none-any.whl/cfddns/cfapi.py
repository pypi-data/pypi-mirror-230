import socket as S
import requests


class CloudflareAPI:
    def __init__(self, ZONE_ID, TOKEN, ttl = 60) -> None:
        self.ZONE_ID = ZONE_ID
        self.TOKEN = TOKEN
        self.ttl = ttl

    def list_records(self, name, type="A"):
        ZONE_ID = self.ZONE_ID
        TOKEN = self.TOKEN

        params = {"type": type}
        if name: params["name"] = name

        res = requests.get(
            f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records",
            params = params,
            headers={
                "Authorization": "Bearer " + TOKEN
            }
        )

        if res.status_code == 200:
            json = res.json()
            if json["success"] == False:
                raise Exception(f"CF_API: list_records API error, errors: {str(json['errors'])}")
            return json["result"]
        else:
            raise Exception(f"CF_API: list_records HTTP error, status_code = {res.status_code}")

    def create_record(self, type, name, content):
        """
        repeat creation leads to HTTP error 400
        """
        ZONE_ID = self.ZONE_ID
        TOKEN = self.TOKEN
        ttl = self.ttl

        res = requests.post(
            f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records",
            headers={"Authorization": "Bearer " + TOKEN},
            json={
                "type": type,
                "name": name,
                "content": content,
                "ttl": ttl
            }
        )

        if res.status_code != 200:
            raise Exception(f"CF_API: create_record HTTP error, status_code = {res.status_code}")

        json = res.json()
        
        if json["success"] == False:
            raise Exception(f"CF_API: create_record API error, errors: {str(json['errors'])}")

        return json["result"]

    def update_record(self, record_id, type, name, content):
        ZONE_ID = self.ZONE_ID
        TOKEN = self.TOKEN
        ttl = self.ttl

        res = requests.put(
            f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{record_id}",
            headers={"Authorization": "Bearer " + TOKEN},
            json={
                "type": type,
                "name": name,
                "content": content,
                "ttl": ttl
            }
        )

        if res.status_code != 200:
            raise Exception(f"CF_API: update_record HTTP error, status_code = {res.status_code}")

        json = res.json()
        
        if json["success"] == False:
            raise Exception(f"CF_API: update_record API error, errors: {str(json['errors'])}")

        return json["result"]

    def delete_record(self, record_id):
        ZONE_ID = self.ZONE_ID
        TOKEN = self.TOKEN
        
        res = requests.delete(
            f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{record_id}",
            headers={ "Authorization": "Bearer " + TOKEN }
        )

        if res.status_code != 200:
            raise Exception(f"CF_API: delete_record HTTP error, status_code = {res.status_code}")
        json = res.json()
        if json.get("success", True) == False:
            raise Exception(f"CF_API: delete_record API error, errors: {str(json['errors'])}")
        return json["result"]

    def smart_update(self, name, ipaddr):
        type = "A" if '.' in ipaddr else "AAAA"
        records = self.list_records(name, type)
        if len(records) == 0:
            self.create_record(type, name, ipaddr)
        else:
            record = records[0]
            rid = record["id"]
            self.update_record(rid, type, name, ipaddr)
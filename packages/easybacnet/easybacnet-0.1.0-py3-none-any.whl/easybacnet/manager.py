import BAC0  # Import the BAC0 library for BACnet communication
import json
import time

class BacnetManager:
    def __init__(self, ip, port):
        self.bacnet = None
        self.configure_bacnet(ip, port)

    def configure_bacnet(self, ip, port):
        if not self.bacnet:
            try:
                self.bacnet = BAC0.connect(ip=ip, port=port)
                print("BACnet configured successfully.")
            except Exception as e:
                print(f"Error configuring BACnet: {str(e)}")
        else:
            print("BACnet is already configured.")

    def read_bacnet_data(self):
        if self.bacnet:
            try:
                data = {}
                mac, device_id = self.bacnet.whois()[0]
                properties_to_retrieve = [
                    "presentValue",
                    "description",
                ]
                objList = self.bacnet.read(f'{mac} device {device_id} objectList')
                objList = objList[1:]

                for obj_type, obj_id in objList:
                    for property_name in properties_to_retrieve:
                        try:
                            property_request = f"{mac} {obj_type} {obj_id} {property_name}"
                            value = self.bacnet.read(property_request)
                            value = str(value)
                            data[f"{obj_type}_{obj_id}_{property_name}"] = value
                        except Exception as prop_error:
                            print(f"Error reading property '{property_name}' of object '{obj_type} {obj_id}': {str(prop_error)}")

                return data
            except Exception as e:
                print(f"Error reading BACnet data: {str(e)}")
                return {"error": str(e)}
        else:
            print("BACnet is not configured. Configure it first.")
            return {"error": "BACnet is not configured. Configure it first."}

    def continuously_monitor_data(self, interval=2):
        while True:
            data = self.read_bacnet_data()
            print(data)
            with open("bacnet_data.json", "w") as json_file:
                json.dump(data, json_file, indent=4)
            time.sleep(interval)

if __name__ == '__main__':
    pass

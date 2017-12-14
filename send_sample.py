import ibmiotf.device

organization = 
deviceType = 
deviceId = 
authMethod = "token"
authToken = 

acc_x = 0.1 # -10 to 10 # Acceleration in x direction
acc_y = 0.2 # -10 to 10 # Acceleration in y direction
acc_z = -0.3 # -10 to 10 # Acceleration in z direction
IR = 1 # 0 or 1 # digital value
US = 20 # Ultra-Sonic distance from obstacle (0-1024)

def myOnPublishCallback():
    print ("Confirmed event received by IoTF\n")

# Initialize the device client.
deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
client = ibmiotf.device.Client(deviceOptions)
print ("init successful")

# Connect and send a datapoint with a value into the cloud as an event
def send(data):
	success = client.publishEvent("data", "json", data, qos=0, on_publish=myOnPublishCallback)
	if not success:
		print ("Not connected to IoTF")
	
client.connect()
send({"IR": IR, "US": US, "acc_x": acc_x, "acc_y": acc_y, "acc_z":acc_z })
client.disconnect()

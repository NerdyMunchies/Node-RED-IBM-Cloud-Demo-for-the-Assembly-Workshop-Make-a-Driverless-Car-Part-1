# Node-RED IBM Cloud Demo for the Assembly Workshop - Make a Driverless Car Part 1
### Node-RED in IBM Cloud
Node-RED is an open source visual flow-based programming tool used for wiring not only Internet of Things (IoT) components, but also integrating an ensemble of services APIs including ones provided by IBM Cloud. <br/>
This repository provides an example of a Node-RED application that is supposed to grab car probe data from a RaspberryPI device that is positioned inside an RC car and visualize both the data and the driver behavior analysis. This data is collected from sensors including IR, Ultra-sonic and accelerometer (MPU-6050) modules. A GPS module is not used to allow the usage of the system in-doors.<br/>
The application explored in this repository can be deployed into IBM Cloud through following the simple steps explained below. <br/>

### How does the system work?
The RaspberryPI Zero communicates with the sensors to collect information that is to be send to IBM Cloud via using the MQTT communication protocol. This process is simplified through the use of the Internet of Thing Platform service available on IBM Cloud. To this data, various pieces of information are added to provided more details about the car probe point collected. This information includes the trip ID, the timestamp, and time of the day. Additionally, the distance and speed were calculated from the sensor data. <br/>
Since the system is to be operable in-doors and collect information that will allow performing a simple driver behavior analysis, the latitude, longitude and heading were calculated to simulate the GPS data as realistically as possible. Driver behavior analysis involves measuring points at which harsh acceleration, harsh braking, over-speeding, frequent harsh acceleration, frequent harsh braking, and frequent stopping took place. Both the car probe data and the driver behavior analysis are both stored in a Cloudant NoSQL database to allow the convenient access to it at any point in time. <br/>
The connecting of the described components is made possible and simple through the deploying a Node-RED the Node-RED Node.js application instance. <br/>

### Architecture overview
![architecture_overview](https://user-images.githubusercontent.com/10744356/33858499-45ab2b3c-dee9-11e7-96e0-2012d01d0f67.png)

### Pre-requisite
An IBM Cloud account - A lite account, which is a free of charge account that doesn’t expire, can be created through going to [IBM Cloud](http://ibm.biz/AssemblyCar1). <br/>

### Creating the Node-RED application and other components
There are three components to configure: <br/>
-	Node-RED application <br/>
-	Internet of Things Platform service <br/>
-	Cloudant NoSQL database <br/>

To simplify connected these three, a boilerplate called Internet of Things Platform Starter is used. It can be found by going to Catalog followed by selecting Boilerplates, which can be seen on the menu available on the left-hand side. The user is then required a unique name for the application being created, which is also used as the hostname. If the user is using a lite account, the region is set to that he chose while applying for the account. After clicking on create, an instance of the Node-RED application is created to which both the Internet of Things Platform service and Cloudant NoSQL database is bound. It will take some time for the application status to change to awake, indicating that it is running. <br/>
Insert video here <br/>

### Steps to configure the Node-RED application and other components
From the hamburger menu at the top left of the page, the user can access the dashboard, which will allow him/her to see all the applications and services that has been created. Click on the name of the application to go to a window that provides more details about the application. If you click on Connection on the menu seen on the left hand-side, you will notice that there are two connections: <app-name>-cloudantNoSQLDB and <app-name>-iotf-service. <br/>


#### Internet of Things Platform service
If we click on <app-name>-iotf-service, it will take us to the page with the details about the IoT Platform service. Go to Manage and then click on Launch. This will take us to the page where we can configure device we can connect to among other things. At the top right of the page, we see an ID, this is the organization ID and it is one of the things needed to configure the connection between a device and the IoT Platform service. <br/>
Here, we are required to configure a device type to which we will be added a device. Go to Devices from the menu on the left, and from the newly opened page, click on Device Types followed by Add Device Type. The name and metadata describing the device type to create the device type. Then, click Register Devices to add a device to that particular device type. Enter a Device ID, metadata describing the device and select an option to define the device’s authentication token. After you are done, you will be directed to a page summarizing the Device Credentials. Copy the credentials into a notepad for later use (It will be used by both the RaspberryPI to send data and the Node-RED application to get the data). <br/>

Insert video here <br/>

On the RaspberryPI, add the following code snippet below, where you will change the organization, deviceType, deviceId, and authToken to that corresponding to the credentials we copied earlier, to the appropriate locations. <br/>
```python
organization = #add organisation from the IoT platform service
deviceType = #add device type from the IoT platform service
deviceId = #add device ID from the IoT platform service
appId = deviceId + "_receiver"
authMethod = "token"
authToken = #add authentication token from the IoT platform service

def myOnPublishCallback():
  print "Confirmed event received by IoTF\n"

# Initialize the device client.
deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
client = ibmiotf.device.Client(deviceOptions)
print "init successful"

# Connect and send a datapoint 
def send(data):
	success = client.publishEvent("data", "json", data, qos=0, on_publish=myOnPublishCallback)
	if not success:
    print "Not connected to IoTF"

client.connect()
send({'IR':INR, "US": USS, "X": X1, "Y": Y1, "Z": Z1 })
client.disconnect()
```
In case Raspberry PI is not available at hand, you use the file called send_sample.py in this repository to simulate the data by typing ```python3 send_sample.py```, given that you have python3 installed on your device. <br/>

Insert Pic here <br/>


#### Cloudant NoSQL database
If we click on <app-name>-cloudantNoSQLDB, it will take us to the page with the details about the Cloudant NoSQL DB service. Click on Service credentials on the menu seen on the left hand-side.  If no service credentials are found, created new credential. Go to the newly created credential and select View credentials. Then, copy both the content into a notepad for later use. The username and password will be used for authentication to allow us to communicate with the database. <br/>

Insert video here <br/>

Next, go to Manage and then click on Launch. This will launch an interface through which we can interact with the Cloudant NoSQL DB. Click on the Databases from the menu available on the left. By default, a database named nodered can be found, which we are not going to touch. Now, click on Create Database at the top of the page to create a new Database and give it a name (here, we called it iotdb) and click create. Here, we will be saving any data we will be receiving/creating. Whenever we want to store something, we store that data in a document in a NoSQL database. <br/>

Insert video here <br/>

One way we ensure that we define what categories of data we might need from the database is by defining functions, which can be considered as a form of a special document called "design documents". We will be creating a design document with a simple view, which is simply how you can define your functions, to grab all documents with the key returned corresponding the timestamp defined for each car probe point and the value corresponding to the entire document object. To do this, after selecting the name of your database, go to design documents, click on the plus sign and click on New View. In the new design field, type the name of the design document (here, we called it carProbe) and in the Index name, type the name of your view, which is should be something representative of what you are trying to do (since we are grabbing all the documents, we called it allDocs). In the Map function field, change doc.id to doc.timestamp and 1 to doc. Finally, click on Create Document. <br/>

Insert video here <br/>


#### Node-RED application
Go back to the dashboard click on the application you created earlier. In order to access the Node-RED editor used to build you application click on Visit App URL. Follow the direction to access the Node-RED editor (you are encouraged to secure your Node-RED editor to ensure that only authorized users can access it). Click on Go to your Node-RED flow editor. <br/>

Insert video here <br/>

A new Node-RED flow opens containing nodes representing a sample application. Select all the nodes and delete them as we will be importing our own flow. In this repository, go to the file called Node-REDflow_Partial.json and copy its content. In the Node-RED editor, go to the hamburger menu at the top right of the page after which select Import Clipboard. Paste the content of the JSON file and click on Import. This will mostly import the calculation part of the application and will be missing some node that we will be adding.
We will notice that we have an error saying that we imported unrecognized types. These are related to the dashboard nodes we will be working with shortly. To work with these nodes, we need to install a module, which we can achieve by going to the hamburger menu again and clicking on Manage palette. In the Install tab, we will search for node-red-dashboard module and install it. If look at the node type menu on the left hand-side, we will node that a number of nodes have been added under dashboard. <br/>

Insert video here <br/>

We will add an ibmiot node, which can be seen under input, to allow us to consume any data received by the IoT Platform service. By clicking on the node, we can change its properties and set the Authentication to Bluemix Service, Device Type and Device id to the device type and device Id that we defined in the IoT Platform service. We will connect it to a debug node, which can be found under output. Before we continue, we will check if our application can receive any data from the Raspberry PI, which should show as a JSON object under the debug tab on the right.
Insert video here <br/>

# Node-RED IBM Cloud Demo for the Assembly Workshop - Make a Driverless Car Part 1
### Node-RED in IBM Cloud
Node-RED is an open source visual flow-based programming tool used for wiring not only Internet of Things (IoT) components, but also integrating an ensemble of service APIs, including ones provided by IBM Cloud.

This repository provides an example of a Node-RED application that is supposed to grab car probe data from a Raspberry PI that is positioned inside an RC car and visualize both the data and the driver behavior analysis. This data is collected from sensors including infrared, ultra-sonic and accelerometer (MPU-6050) modules. A GPS module is not used to allow the usage of the system in-doors.

The application explored in this repository can be deployed into IBM Cloud via the simple steps explained below.

### How does the system work?
The Raspberry PI Zero communicates with the sensors to collect information that is to be sent to IBM Cloud via MQTT. This process is simplified through the usage of the **Internet of Things Platform** service available on IBM Cloud. To this data, various pieces of information are added to provide more details about the car probe point collected. This information includes the trip ID, the timestamp, and time of the day. Additionally, the distance and speed are calculated from the sensor data. 

Since the system is to be operable in-doors and collect information that will allow performing a simple driver behavior analysis, the latitude, longitude and heading are calculated to simulate the GPS data as realistically as possible. Driver behavior analysis involves measuring points at which harsh acceleration, harsh braking, over-speeding, frequent harsh acceleration, frequent harsh braking, and frequent stopping take place. Both the car probe data and the driver behavior analysis are both stored in a **Cloudant NoSQL database** to allow the convenient access to it at any point in time.
The connecting of the described components is made possible and simple through the deploying a Node-RED Node.js application instance.


### Architecture overview
![architecture_overview](https://user-images.githubusercontent.com/10744356/33858499-45ab2b3c-dee9-11e7-96e0-2012d01d0f67.png)

### Pre-requisite
An IBM Cloud account - A lite account, which is a free of charge account that doesn’t expire, can be created through going to [IBM Cloud](bluemix.net). <br/>

### Creating the Node-RED application and other components
There are three components to configure: <br/>
-	Node-RED application <br/>
-	Internet of Things Platform service <br/>
-	Cloudant NoSQL database <br/>

To simplify connecting these three, a boilerplate called Internet of Things Platform Starter is used. It can be found by going to Catalog followed by selecting **Boilerplates**, which can be seen on the menu available on the left-hand side. The user is then required a unique name for the application being created, which is also used as the hostname. If the user is using a lite account, the region is set to that chosen while applying for the account. After clicking on **create**, an instance of the Node-RED application is created to which both the **Internet of Things Platform** service and **Cloudant NoSQL database** are bound. It will take some time for the application status to change to awake, indicating that it is running.

![Alt Text](https://j.gifs.com/59WvjB.gif)

### Steps to configure the Node-RED application and other components
From the hamburger menu at the top left of the page, the user can access the dashboard, which will allow the user to see all the applications and services that have been created. Click on the name of the application to go to a window that provides more details about the application. If you click on **Connection** on the menu seen on the left hand-side, you will notice that there are two connections: <app-name>-cloudantNoSQLDB and <app-name>-iotf-service.

#### Internet of Things Platform service
If we click on <app-name>-iotf-service, it will take us to the page with the details about the IoT Platform service. Go to **Manage** and then click on **Launch**. This will take us to the page where we can configure devices we can connect to among other things. At the top right of the page, we see an ID, this is the organization ID and it is one of the things needed to configure the connection between a device and the **IoT Platform** service.

Here, we are required to configure a device type to which we will be adding a device. Go to **Devices** from the menu on the left, and from the newly opened page, click on **Device Types** followed by **Add Device Type**. Here you will provide the name and metadata describing the device type to create the device type. Then, click **Register Devices** to add a device to that particular device type. Enter a Device ID, metadata describing the device and select an option to define the authentication token. After you are done, you will be directed to a page summarizing the device’s credentials. Copy the credentials into a notepad for later use (It will be used by both the Raspberry PI to send data and the Node-RED application to get the data.

![Alt Text](https://j.gifs.com/kZox95.gif)
![Alt Text](https://j.gifs.com/vojMKm.gif)

On the RaspberryPI, add the following code snippet below to the appropriate locations, where you will change the organization, deviceType, deviceId, and authToken to that corresponding to the credentials we copied earlier.

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
In case the Raspberry PI is not available at hand, you can use the file called **send_sample.py** in this repository to simulate the data by typing ```python3 send_sample.py```, given that you have python3 installed on your device. <br/>

#### Cloudant NoSQL database
If we click on <app-name>-cloudantNoSQLDB, it will take us to the page with the details about the Cloudant NoSQL DB service. Click on Service Credentials on the menu seen on the left hand-side.  If no service credentials are found, create a new credential. Go to the newly created credential and select View credentials. Then, copy both the content into a notepad for later use. The username and password will be used for authentication to allow us to communicate with the database.

![Alt Text](https://j.gifs.com/L8PO8g.gif)

Next, go to Manage and then click on Launch. This will launch an interface through which we can interact with the Cloudant NoSQL DB. Click on the Databases from the menu available on the left. By default, a database named nodered can be found, which we are not going to touch. Now, click on Create Database at the top of the page to create a new Database and give it a name (here, we called it iotdb) and click create. Here, we will be saving any data we will be receiving/creating. Whenever we want to store something, we store that data in a document in a NoSQL database.

![Alt Text](https://j.gifs.com/qY2qY3.gif)

One way we ensure that we define what categories of data we might need from the database is by defining functions, which can be considered as a form of a special document called "design document". We will be creating a design document with a simple view, which is simply how you can define your functions, to grab all documents with the key returned corresponding to the timestamp defined for each car probe point and the value corresponding to the entire document object. To do this, after selecting the name of your database, go to design documents, click on the plus sign and click on **New View**. In the new design field, type the name of the design document (here, we called it carProbe) and in the **Index name**, type the name of your view, which is should be something representative of what you are trying to do (since we are grabbing all the documents, we called it alldocs). In the **Map function field**, change doc.id to doc.timestamp and 1 to doc. Finally, click on **Create Document**.  

Insert video here <br/>
![Alt Text](https://j.gifs.com/MQ9PwB.gif)

#### Node-RED application
Go back to the dashboard and click on the application you created earlier. In order to access the Node-RED editor used to build the application, click on **Visit App URL**. Follow the directions to access the Node-RED editor (you are encouraged to secure your Node-RED editor to ensure that only authorized users can access it). Click on **Go to your Node-RED flow editor**.

Insert video here
![Alt Text](https://j.gifs.com/329gw4.gif)

A new Node-RED flow appears containing nodes representing a sample application. Select all the nodes and delete them as we will be importing our own flow. In this repository, go to the file called **Node-REDflow_Partial.json** and copy its content. In the Node-RED editor, go to the hamburger menu at the top right of the page after which select **Import Clipboard**. Paste the content of the JSON file and click on **Import**. This will mostly import the calculation part of the application and will be missing some nodes that we will be adding.

We will notice that we have an error saying that we imported unrecognized types. These are related to the dashboard nodes that we will be working with shortly. To work with these nodes, we need to install a module, which can be achieved by going to the hamburger menu again and clicking on **Manage palette**. In the **Install** tab, we will search for **node-red-dashboard** module and install it. If look at the node type menu on the left hand-side, we will notice that a number of nodes have been added under the **dashboard** node type.

Insert video here

We will add an **ibmiot** node, which can be seen under **input**, to allow us to consume any data received by the **IoT Platform** service. By double-clicking on the node, we can change its properties and set the **Authentication** to **Bluemix Service**, **Device Type** and **Device id** to the device type and device id that we defined in the IoT Platform service. We will connect it to a **debug node**, which can be found under **output** node type. Before we continue, we will check if our application can receive any data from the Raspberry PI, which should show as a JSON object under the **debug** tab on the right.

Insert video here

After that, connect the **IBM IoT** node to the SetArgs1 node from the imported flow. Double-click on that node and look for global.set(“dburl”, “xxx”) and replace “xxx” with the url for your database, which you can find from the credentials we copied earlier. This is used in various nodes in the flow to communicate with the database.
Next, look for the **cloudant out** node under storage and connect to SetArgs1 in your flow. Edit the node’s properties and change the services to point to your **Cloudant NoSQL database** service and add your database name in the appropriate field. Make sure that the operation is **insert** and that it is set to **Only store msg.payload object**.

Insert PIC here

For all of the HTTP request nodes, make sure to add the username and password previously copied from the database credentials page by editing the node’s properties. An example is provided below:
Insert PIC here

Now that all the operational nodes are done, it is time to create and customize the dashboard, which provides the User Interface (UI) part of the application. On the right hand-side of the page, click on the **dashboard** tab. We will notice that there are 3 tabs, each used to change the look and feel of the UI.

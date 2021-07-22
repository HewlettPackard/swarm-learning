## Troubleshooting ##

Troubleshooting provides solutions to commonly observed issues during Swarm set up and execution.


### 1. Error code : 6002
####    ``Error message: Unable to connect to server. Server might be wrongly configured or down.`` #### 
####    ``Custom message: Error in communicating with server https://HOST_SYSTEM_IP:5814 (default port)`` #### 

#### Problem Description 
Error code: 6002, as shown in below screenshot happens when SL is not able to connect to the APLS server. 

   ![Error_6002](./images/Error_6002_running_SL_node_without_Server_and_License.png)
   
   
#### Resolution
Fix for above issue requires to make sure following two things.

##### 1. Running AutoPass License Server (APLS)
Run ``docker ps | grep apls``  -> If apls container is not running, then license server is not running, and you need to start it using  
``swarm-learning-install-dir/swarm-learning/bin/run-apls`` 

Browse to APLS management console.
If the browser response is, "this site can’t be reached" / "refused to connect" - It means APLS is not running correctly. Restart run-apls script as mentioned above. 

##### 2. Setting up Swarm License
Download the Swarm License.
Install the license using APLS management console. 


For detailed instructions - refer [Installing licenses and starting license server](setup.md#installing-licenses-and-starting-license-server)

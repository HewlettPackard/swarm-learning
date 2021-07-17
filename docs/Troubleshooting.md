## Troubleshooting ##

Troubleshooting provides solutions to commonly observed issues during Swarm set up and execution.


### 1. Error code : 6002
####    Error message: Unable to connect to server. Server might be wrongly configured or down. #### 
####    Custom message: Error in communicating with server https://HOST_SYSTEM_IP:5814 (default port) #### 

#### Problem Description 
Error code: 6002, as shown in below screenshot happens when running SL Node without starting APLS server and License setup. 

   ![Error_6002](./images/Error_6002_running_SL_node_without_Server_and_License.png)
   
   
#### Resolution
Fix for above issue involves two things.
1.	Running AutoPass License Server (APLS) 
2.	Setting up Swarm License

##### 1. Running AutoPass License Server (APLS)
Run docker ps | grep apls  -> If apls container is not running, then license server is not running, and you need to start it 
<your install directory>/ swarm-learning/bin/run-apls 

###### Check APLS status:  
Browse to autopass license server management console: https://192.168.1.102:5814/autopass

> NOTE: For this explanation IP 192.168.1.102 is used – replace this IP address with your license host system IP address (Do NOT use localhost / 127.0.0.1)  
> 5814 is the default port used for APLS. 

If response is, this site can’t be reached: 192.168.1.102 refused to connect. It means Autopass server is not reachable means APLS is not running. Start run-apls script as mentioned above. 

Otherwise, In the login screen login using admin/ password. 
  
> NOTE: SSH command to use port forwarding if web access is not available in licenser server host. 
> $ ssh -L 5814: 192.168.1.102 :5814 username@192.168.1.102 )

   
##### 2. Setting up Swarm License

###### Download the License: 
If you don’t have Swarm License downloaded already, then get the License (.DAT file). Create login credentials to access [My HPE Software Center (MSC)](https://myenterpriselicense.hpe.com/cwp-ui/evaluation/HPE-SWARM/0.3.0/null) if you don’t have yet. The email address used to access MSC is called as HPE passport account.  The evaluation license for running the Swarm Learning components are available at [My HPE Software Center (MSC)](https://myenterpriselicense.hpe.com/cwp-ui/evaluation/HPE-SWARM/0.3.0/null). Use your HPE Passport account to access MSC and download evaluation license.

###### Setup License: 
Go to https://192.168.1.102:5814/autopass

Go to License Management – Install License
Select License Dat file.
Select all feature IDs and install. 

###### Confirm License setup is successful: 
Refer License installed picture here.

   ![License_server_after_installing_license](./images/APLS_after_installing_license.png)
 
   If above screen showing on your License Management means your setup is good to run SL.

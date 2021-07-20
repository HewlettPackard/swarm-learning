## Troubleshooting ##

Troubleshooting provides solutions to commonly observed issues during Swarm set up and execution.


### 1. Error code : 6002
####    Error message: Unable to connect to server. Server might be wrongly configured or down. #### 
####    Custom message: Error in communicating with server https://HOST_SYSTEM_IP:5814 (default port) #### 

#### Problem Description 
Error code: 6002, as shown in below screenshot happens when SL is not able to connect to the APLS server. 

   ![Error_6002](./images/Error_6002_running_SL_node_without_Server_and_License.png)
   
   
#### Resolution
Fix for above issue involves two things.
1.	Running AutoPass License Server (APLS) 
2.	Setting up Swarm License

##### 1. Running AutoPass License Server (APLS)
Run docker ps | grep apls  -> If apls container is not running, then license server is not running, and you need to start it using  
'your install directory/swarm-learning/bin/run-apls' 

###### Check APLS status:  
Follow the steps mentioned below to verify APLS status. 

> NOTE: For this explanation IP 192.168.1.102 is used – replace this IP address with your license host system IP address (Do NOT use localhost / 127.0.0.1)  
> 5814 is the default port used for APLS. 
   
Browse to autopass license server management console: https://192.168.1.102:5814/autopass.
> NOTE: If you can run a browser on the host machine where you ran the "run-apls" script, You can now connect to the License server using https://192.168.1.102:5814/autopass from a browser. 
> 
> Else, if the host machine is accessible from your laptop/desktop, then you can access by using https://192.168.1.102:5814/autopass from your laptop/desktop browser.
> 
> Else you should setup SSH port forwarding first and then access https://localhost:5814/autopass from your laptop/desktop browser. 
> 
> Run this shell command from your laptop/desktop to do SSH port forwarding  
> - $ ssh -L 5814:192.168.1.102:5814 username@192.168.1.102 

If the browser response is, "this site can’t be reached" / "refused to connect" - It means APLS is not running correctly. Restart run-apls script as mentioned above. 

Otherwise, In the APLS login screen, login using "admin/password". 

   
##### 2. Setting up Swarm License

###### Download the License: 
If you don’t have Swarm License downloaded already, then get the License (.DAT file). 

Create login credentials to access [My HPE Software Center (MSC)](https://myenterpriselicense.hpe.com/cwp-ui/evaluation/HPE-SWARM/0.3.0/null) if you don’t have yet. The email address used to access MSC is called as HPE passport account. 

Use your HPE Passport account to access above MSC link and download evaluation license file.

###### Setup License: 
Go to APLS management console. As described in step 1. 

Go to License Management –> Install License

Select License file (.DAT).

Select all feature IDs and install. 

###### Confirm License setup is successful: 
Refer License installed picture here.

   ![License_server_after_installing_license](./images/APLS_after_installing_license.png)
 
   If you are seeing the above screenshot in your APLS Management console, it means your setup is good to run Swarm Learning. 

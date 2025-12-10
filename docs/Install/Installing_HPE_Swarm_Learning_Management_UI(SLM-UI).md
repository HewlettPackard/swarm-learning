# Installing HPE Swarm Learning Management UI \(SLM-UI\)

## Manual installation: 
If you choose to manually install Swarm learning, then 
1. Clone / download this git repo - Select "Code" button on the repo page and select "Download ZIP" to get the files as a compressed folder and extract the zip on **each machine** where you want to install Swarm learning. 

2. Preferable to extract it under /opt/hpe/swarm-learning. 

3. Do a Docker login from your host:
  
       docker login hub.myenterpriselicense.hpe.com –u <YOUR-HPE-PASSPORT-EMAIL> -p hpe
6. Pull the signed Swarm Learning images from HPEs Docker Trust Registry (DTR):
   
       docker pull hub.myenterpriselicense.hpe.com/hpe/swarm-learning/sn:2.3.0 
       docker pull hub.myenterpriselicense.hpe.com/hpe/swarm-learning/sl:2.3.0 
       docker pull hub.myenterpriselicense.hpe.com/hpe/swarm-learning/swci:2.3.0 
       docker pull hub.myenterpriselicense.hpe.com/hpe/swarm-learning/swop:2.3.0 
       docker pull hub.myenterpriselicense.hpe.com/hpe/swarm-learning/slm-ui:2.2.0 
       docker pull hub.myenterpriselicense.hpe.com/hpe/swarm-learning/slm-ui-postgres:2.2.0
       docker pull hello-world
You can skip rest of the installation steps mentioned below.

## Automatic installation: 
Installing Swarm Learning is a two-step process using the GUI.

1.  Using SLM-UI Installer, you can install the SLM-UI on one host.
2.  Using SLM-UI, you can install SL in multiple hosts and run the examples.

1.  Navigate to the [MY HPE SOFTWARE CENTER](https://myenterpriselicense.hpe.com/cwp-ui/auth/login) home page.

2.  Perform the following actions after signing in with your HPE Passport credentials:

    1.  Go to **My Activations** and select your ordered product. If you are using the free community version, then in the MSC page, click Software->Search -> Product Info -> "Swarm Learning" (as search term). In the search results, choose "HPE Swarm Learning Community edition" ver 2.2.0 > Action (drop down) 

    2.  Go to **Action** pull down and then select **Download/Re-download** page.

    3.  Select and download listed software files.

        -   Unselect The tar file containing docs and scripts. This is a older version of the tar. For current version(2.3.0), you need to download this git repo - Select "Code" button on the repo page and select "Download ZIP" to get the files as a compressed folder

        -   The signature file for the above tar file.

        -   The docker digest hash file \(JSON\).

        -   Download the Swarm Learning SLM-UI installer for your platform, Mac, Windows, or Linux.

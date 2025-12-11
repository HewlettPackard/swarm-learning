# Installing HPE Swarm Learning Management UI \(SLM-UI\)

## Manual installation for 2.3.0 version: 
We support **only manual** installation for 2.3.0 version. You need to:
1. Either Clone or download this git repo on **each host machine** where you want to install Swarm learning.

2. If your downloading, then navigate to the main page of the repository. To the right of the list of files, click Releases and select 2.3.0 version. Scroll down to the "Assets" section of the release, click Source code (tar.gz). Copy and extract the tar.gz **on each host machine**

3. Preferable to extract it under /opt/hpe/swarm-learning. 

4. Do a Docker login from your host:
  
       docker login hub.myenterpriselicense.hpe.com –u <YOUR-HPE-PASSPORT-EMAIL> -p hpe
5. Pull the signed Swarm Learning images from HPEs Docker Trust Registry (DTR):
   
       docker pull hub.myenterpriselicense.hpe.com/hpe/swarm-learning/sn:2.3.0 
       docker pull hub.myenterpriselicense.hpe.com/hpe/swarm-learning/sl:2.3.0 
       docker pull hub.myenterpriselicense.hpe.com/hpe/swarm-learning/swci:2.3.0 
       docker pull hub.myenterpriselicense.hpe.com/hpe/swarm-learning/swop:2.3.0 
       docker pull hub.myenterpriselicense.hpe.com/hpe/swarm-learning/slm-ui:2.2.0 
       docker pull hub.myenterpriselicense.hpe.com/hpe/swarm-learning/slm-ui-postgres:2.2.0
       docker pull hello-world
You can skip rest of the installation steps mentioned below.

## Automatic installation for 2.2.0 version: 
Installing Swarm Learning is a two-step process using the GUI.

1.  Using SLM-UI Installer GUI, you can install the SLM-UI on one linux host.
2.  Using SLM-UI, you can install SL in multiple hosts and run the examples.

1.  Navigate to the [MY HPE SOFTWARE CENTER](https://myenterpriselicense.hpe.com/cwp-ui/auth/login) home page.

2.  Perform the following actions after signing in with your HPE Passport credentials:

    1.  Go to **My Activations** and select your ordered product. If you are using the free community version, then in the MSC page, click Software->Search -> Product Info -> "Swarm Learning" (as search term). In the search results, choose "HPE Swarm Learning Community edition" ver 2.2.0 > Action (drop down) 

    2.  Go to **Action** pull down and then select **Download/Re-download** page.

    3.  Select and download listed software files.

        -   The docker digest hash file \(JSON\).

        -   Download the Swarm Learning SLM-UI installer for your platform, Mac, Windows, or Linux.
          
        -   The tar file containing docs and scripts.
          
        -   The signature file for the above tar file.

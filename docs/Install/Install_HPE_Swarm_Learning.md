# <a name="GUID-60017971-B0A9-4119-AEAF-A21594EE5C1E"/> Install HPE Swarm Learning

1.   After installing the license, download the following from the [MY HPE SOFTWARE CENTER](https://myenterpriselicense.hpe.com/cwp-ui/auth/login) page: 

     1.   The tar file containing docs and scripts. 
     2.   The signature file for the above tar file. 
     3.   The docker digest hash file \(JSON\). 
     4.   Download the Swarm Learning installer for your platform, Mac, Windows, or Linux. 

2.   Run the Swarm Learning installer Web App. This is launched in a web browser. 

<blockquote>
    IMPORTANT: For Mac users, HPE recommends you to run the downloaded Swarm Learning installer from the terminal window only.
</blockquote>

The installer has a few configurable options. To change the default options, run the installer from a command prompt. Use the following optional flags to customize the configuration or behavior of the installer:

     -port
     :   Defines the port for the application to run. The default value is 30302.

        Example, `-port 30355`

      -edition
     :   Configure the Swarm Learning edition that must be installed. The following are the available options:

         eval
         :   This option installs the community edition \(free edition\) of the Swarm Learning.

         :   Example, `-edition eval`

         ga
         :   This option installs the enterprise edition \(paid edition\) of the Swarm Learning.

         :   Example, `-edition ga`

       -logs
     :   If enabled, displays the detail message on the CLI during the installation. To enable, use the command, `-logs verbose`.

      -version
     :   This option defines the version of docker images that must be installed. The default value is 1.0.0. Example, `-version 0.3.0`

      -timeoutDuration
     :   Defines installer timeout duration for individual installation tasks. The default value is 300 seconds.

        Example, `-timeoutDuration 600`

     
   ![Overview](GUID-633F271F-2F22-4BB9-91A6-EA50BF8C638A-high.png)

3.   Click **Next** in the **Overview** screen. 
4.   Review the **Requirements** and ensure each of the hosts satisfies the prerequisites, and click **Next.** 
5.   In the **Docker Registry Access**, enter your HPE Passport credentials and click **Next**. 
6.   Add hosts:

     1. Provide a unique **Host Server Name** or **IP Address** for each host. If it is not unique, the message *Duplicated host* is displayed. 
     2. Enter **Port Number**, **Username**, and **Password**. They can be reused for all hosts. If you want to use a different username and password, clear the check box. 
     ![Add hosts](GUID-9E052DAE-2F49-4625-903D-3D458B4320B0=1=en-US=High.png)
     NOTE: If you want to delete any host, click “X” and click **Delete**.
     3. Click **Next.**.
          - It initiates and displays the connection process for all hosts.
          - On a successful connection, the installer copies the required Swarm Learning files to the default Swarm installation location \(`/opt/hpe/swarm-learning`\) on each host.
          - It also pulls the Swarm Docker images from HPE's Docker Trust Registry \(DTR\).
          - If a host fails to connect, an error message is displayed.
          ![Host validation](GUID-60C03DFA-04B4-4884-9CB0-441A3E4351A5=1=en-US=High.png)
     5. If there is an error message, click **Click here for more info**. Close the error message dialog, **Retry** or **Configure** the host, and click **Next**.
     6. A success message is displayed for all installed hosts. Click **Next**.      
 
 <blockquote>
        NOTE: Unless you configure all the hosts successfully, you cannot go to the next screen.
</blockquote>

7.   Review **Next Steps** and click **Next**. 
8.   Review the **Summary** screen, which displays all the installed hosts. Click **Finish**. 
9.   An installation confirmation message is displayed. Click **Close Window**. 



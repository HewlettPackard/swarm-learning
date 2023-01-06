# Swarm Learning log collector

Run this script to collect logs and basic system information and create a tar archive file, that can be sent to HPE for troubleshooting any Swarm Learning related issues.

Please note that the script will collect the logs only from the current host. So if the user is running Swarm Learning on multiple hosts, he needs to run the script on each host machine.

The tar archive includes:

      - OS details
      - nvidia details [if user running examples with GPU]
      - Running and exited docker information
      - docker logs and docker inspect of all artifacts [SN SWOP SL ML]

Syntax:

```
./swarmLogCollector.sh [OPTIONS] > out.log
```

##  Run the below command if you are using SWOP:

```
 ./swarmLogCollector.sh "<DOCKER_HUB>" "workspace=<swarm-learning workspace/exampleFolder>" > out.log
```
Example:

```
 ./swarmLogCollector.sh "hub.myenterpriselicense.hpe.com/hpe_eval/swarm-learning" "workspace=/opt/hpe/swarm-learning/workspace/fraud-detection/" > out.log
```
## Run the below command if you are using run-sl script:

```
./swarmLogCollector.sh "<DOCKER_HUB>" "mlimage=<ml image name>" > out.log
```
Example:

```
./swarmLogCollector.sh "hub.myenterpriselicense.hpe.com/hpe_eval/swarm-learning" "mlimage=user-env-tf2.7.0-swop" > out.log
```

## Additional information to provide:

1. Issue description

      What is the Issue:      
      
      Occurrence - consistent or rare:      
      
      Commands used for starting containers:      
      
      Details of ML platform used:

2. Quick Checklist: Respond [Yes/No]

      APLS server web GUI shows available Licenses?
      
      If Multiple systems are used, can each system access every other system?
      
      Is Password-less SSH configuration setup for all the systems?

3. Additional notes

      Are you running documented example without any modification?  
      
      Add any additional information about use case or any notes which supports for issue investigation:
     
4. If running examples with GPU, use gpu diagnostics messages in application code.
   Like cuda_available, or any python packages which helps to print GPU statistics.

5. Provide firewall related info by running the respective commands based on OS
   For example the below command will provide the firewall details in ubuntu OS.
 
   ```
   sudo ufw status 
   ```

6. Run example with "SWARM_LOOPBACK": "True", to confirm user application has no issues. Follow below link to do the same:
   https://github.com/HewlettPackard/swarm-learning/blob/master/docs/User/Frequently_asked_questions.md#before-enabling-swarm-learning-how-to-confirm-the-standalone-user-application-has-no-issues-and-runs

# Swarm Learning log collector

This script is to collect logs and basic system information and create a tar archive file, that can be sent to HPE for troubleshooting any Swarm Learning related issues.

Please note that the script will collect the logs only from the current host. So if the user is running Swarm Learning on multiple hosts, he needs to run the script on each host machine.

The tar archive includes:

      - OS details
      - nvidia details [if user running examples with GPU]
      - Running and exited docker information
      - docker logs and docker inspect of all artifacts [SN SWOP SL ML]

Syntax:

```
./swarmLogBackup.sh [OPTIONS] > out.log
```

## Running script if using SWOP for running example:

```
 ./swarmLogBackup.sh "<DOCKER_HUB>" "workspace=<swarm-learning workspace/exampleFolder>" > out.log
```
Example:

```
 ./swarmLogBackup.sh "hub.myenterpriselicense.hpe.com/hpe_eval/swarm-learning" "workspace=/opt/hpe/swarm-learning/workspace/fraud-detection/" > out.log
```
## Running script if using run-sl script for running example:

```
./swarmLogBackup.sh "<DOCKER_HUB>" "mlimage=<ml image name>" > out.log
```
Example:

```
./swarmLogBackup.sh "hub.myenterpriselicense.hpe.com/hpe_eval/swarm-learning" "mlimage=user-env-tf2.7.0-swop" > out.log
```

## Please provide the below outputs for better debuggability [Not mandatory]

1. If running examples with GPU, use gpu diagnostics messages in application code.
   Like cuda_available, or any python packages which helps to print GPU statistics.

2. Provide firewall related info by running the respective commands based on OS
   For example the below command will provide the firewall details in ubuntu OS.
 
   ```
   sudo ufw status 
   ```

3. Run example with "SWARM_LOOPBACK": "True", to confirm user application has no issues. Follow below link to do the same:
   https://github.com/HewlettPackard/swarm-learning/blob/master/docs/User/Frequently_asked_questions.md#before-enabling-swarm-learning-how-to-confirm-the-standalone-user-application-has-no-issues-and-runs

Hugging Face 
============
This example demonstrates LLM fine-tuning in a federated scenario. It shows a Hugging Face BERT movie reviews classification application with GPU based local training on the Swarm Learning platform. 

The Machine Learning program, after conversion to Swarm Learning for the Hugging Face transformers platform, is in `examples/huggingface/model`. The Hugging Face transformers-based file is called `model.py`.

This example shows the Swarm training of BERT movie reviews classification model using three ML nodes. ML nodes along with SL nodes are automatically spawned by SWOP nodes - all running on a single host. Swarm training gets initiated by the SWCI node and orchestrated by one SN node running on the same host. This example also shows how private data, private scratch area and shared model can be mounted to ML nodes for Swarm training.

The following image illustrates a cluster setup for the Hugging Face example:

<img width="80%" height="100%" src="../figs/huggingface-cluster-setup.png">


-   This example uses one SN node. The name of the docker containers representing this node is SN1. SN1 is also the Sentinel Node. SN1 runs on the host 172.1.1.1.

-   Three SL and ML nodes are automatically spawned by SWOP node during training and removed after the training. This example uses one SWOP node that connects to the SN node. The name of the docker container representing this SWOP node is SWOP1. SWOP1 runs on the host 172.1.1.1.

-   Training is initiated by SWCI node \(SWCI1\) that runs on the host 172.1.1.1.

-   This example assumes that License Server already runs on host 172.1.1.1. All Swarm nodes connect to the License Server, on its default port 5814.


## <a name="SECTION_G1M_4RZ_LSB"/> Running the Hugging Face BERT example

1.  Navigate to `swarm-learning` folder (that is, parent to examples directory).

    ```
    cd swarm-learning
    ```

2.  Create a temporary workspace directory and copy `huggingface` example.

    ```
    mkdir workspace
    cp -r examples/huggingface/ workspace/huggingface/
    cp -r examples/utils/gen-cert workspace/huggingface/
    ```

3.  Run the gen-cert utility to generate certificates for each Swarm component using the command (`gen-cert -e <EXAMPLE-NAME> -i <HOST-INDEX>`):

    ```
    ./workspace/huggingface/gen-cert -e huggingface -i 1
    ```

4. Create a network called `host-1-net` using docker network create command. This network will be used for SN, SWOP, SWCI, SL and user containers. Please ignore this step if this network is already created.
   
    ```
    docker network create host-1-net
    ```

5. Declare and assign values to the variables like APLS_IP, SN_IP, HOST_IP and SN_API_PORT. The values mentioned here are for illustration purpose only. Use appropriate values as per your swarm network.
   
    ```
    APLS_IP=172.1.1.1
    SN_IP=172.1.1.1
    HOST_IP=172.1.1.1
    SN_API_PORT=30304
    SN_P2P_PORT=30303
    ```

6.  Search and replace all occurrences of placeholders and replace them with appropriate values.

    ```
    sed -i "s+<PROJECT-MODEL>+$(pwd)/workspace/huggingface/model+g" workspace/huggingface/swci/taskdefs/run_hf_task.yaml
    sed -i "s+<PROJECT>+$(pwd)/workspace/huggingface+g" workspace/huggingface/swci/taskdefs/run_hf_task.yaml
    sed -i "s+<SWARM-NETWORK>+host-1-net+g" workspace/huggingface/swop/swop_profile.yaml
    sed -i "s+<LICENSE-SERVER-ADDRESS>+${APLS_IP}+g" workspace/huggingface/swop/swop_profile.yaml
    sed -i "s+<PROJECT>+$(pwd)/workspace/huggingface+g" workspace/huggingface/swop/swop_profile.yaml
    sed -i "s+<PROJECT-CERTS>+$(pwd)/workspace/huggingface/cert+g" workspace/huggingface/swop/swop_profile.yaml
    sed -i "s+<PROJECT-CACERTS>+$(pwd)/workspace/huggingface/cert/ca/capath+g" workspace/huggingface/swop/swop_profile.yaml

    ```

7.  Create a docker volume and copy Swarm Learning wheel file:

    ```
    docker volume rm sl-cli-lib
    docker volume create sl-cli-lib
    docker container create --name helper -v sl-cli-lib:/data hello-world
    docker cp lib/swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl helper:/data
    docker rm helper
    ```

8.  Run SN node (SN1 - sentinel node)

    ```
    ./scripts/bin/run-sn -d --rm --name=sn1 --network=host-1-net --host-ip=${HOST_IP} --sentinel --sn-p2p-port=${SN_P2P_PORT} --sn-api-port=${SN_API_PORT}      \
    --key=workspace/huggingface/cert/sn-1-key.pem --cert=workspace/huggingface/cert/sn-1-cert.pem --capath=workspace/huggingface/cert/ca/capath --apls-ip=${APLS_IP}
    ```

   Use the Docker logs command to monitor the Sentinel SN node and wait for the node to finish initializing. The Sentinel node is ready when these messages appear in the log output:
    ```
    swarm.blCnt : INFO : Starting SWARM-API-SERVER on port: 30304
    ```


9. Run SWOP node \(SWOP1\). 

    ```
    ./scripts/bin/run-swop -d --rm --name=swop1 --network=host-1-net --sn-ip=${SN_IP} --sn-api-port=${SN_API_PORT}              \
    --usr-dir=workspace/huggingface/swop --profile-file-name=swop_profile.yaml --key=workspace/huggingface/cert/swop-1-key.pem      \
    --cert=workspace/huggingface/cert/swop-1-cert.pem --capath=workspace/huggingface/cert/ca/capath -e SWOP_KEEP_CONTAINERS=True    \
    -e http_proxy= -e https_proxy= --apls-ip=${APLS_IP}
    ```
<blockquote>
    NOTE: If required, according to environment, modify IP and proxy either in the above command or in the swop profile file under `workspace/huggingface/swop` folder.
</blockquote>

<blockquote>
   NOTE: `-e SWOP_KEEP_CONTAINERS=True` is an optional argument, by default it would be `False`. 
   SWOP_KEEP_CONTAINERS is set to True so that SWOP doesn't remove stopped SL and ML containers. With out this setting if there is any internal error in SL or ML then SWOP removes them automatically. Refer documentation of SWOP_KEEP_CONTAINERS for more details.
</blockquote>


10. Run SWCI node and observe sequential execution of two tasks – build task (`build_hf_user_image`) and run task (`run_hf_task`).

    ```
    ./scripts/bin/run-swci -ti --rm --name=swci1 --network=host-1-net --usr-dir=workspace/huggingface/swci                        \
    --init-script-name=swci-init --key=workspace/huggingface/cert/swci-1-key.pem --cert=workspace/huggingface/cert/swci-1-cert.pem  \
    --capath=workspace/huggingface/cert/ca/capath -e http_proxy= -e https_proxy= --apls-ip=${APLS_IP}
    ```

-   `build_hf_user_image` - builds Hugging Face transformers based user image with PyTorch backend.

-   `run_hf_task` - runs Swarm training for BERT sentiment classification across three ML nodes.

<blockquote>
   NOTE: If required, according to the environment, modify SN IP in <code>workspace/huggingface/swci/swci-init</code> file.
</blockquote>


11. Three nodes of Swarm trainings are automatically started when the run task (`run_hf_task`) gets assigned and executed. Open a new terminal and monitor the Docker logs of ML nodes for Swarm training. Swarm training ends with the following log message:

    ```
    SwarmCallback : INFO : All peers and Swarm training rounds finished. Final Swarm model was loaded.
    ```


   Final Swarm model is saved inside each user's specific directory in `workspace/huggingface/<userN>`. All the dynamically spawned SL and ML containers exits after Swarm training if `SWOP_KEEP_CONTAINERS` is not set, otherwise SL and ML containers needs to be removed manually. The SN and SWOP nodes continues to run.

12. To clean up, run the `scripts/bin/stop-swarm` script on all the systems to stop and remove the container nodes of the previous run. If required, backup the container logs. Remove Docker networks (`host-1-net`) and Docker volume (`sl-cli-lib`), and delete the workspace directory.

## <a name="SECTION_DATA_REQUIREMENTS"/> Data Requirements

This example requires sentiment analysis data with the following structure:

-   **Training Data**: Three CSV files (`N1.csv`, `N2.csv`, `N3.csv`) containing text samples and their corresponding sentiment labels. Each file represents the private dataset for one ML node.

-   **Test Data**: One CSV file (`test_data.csv`) containing test samples for model evaluation.

-   **Pre-trained Model**: BERT base model downloaded from Hugging Face model hub.

The CSV files should have columns for text data and corresponding sentiment labels (e.g., positive, negative, neutral).

## <a name="SECTION_MODEL_DETAILS"/> Model Details

-   **Model Architecture**: BERT (Bidirectional Encoder Representations from Transformers) for sequence classification
-   **Framework**: Hugging Face Transformers with PyTorch backend
-   **Task**: Sentiment Analysis/Text Classification
-   **Training Strategy**: Fine-tuning pre-trained BERT model
-   **GPU Support**: Enabled with CUDA 11.7 support
-   **Hardware**: Supports both CPU and GPU training

## <a name="SECTION_CUSTOMIZATION"/> Customization

To adapt this example for your own text classification task:

1. **Data Preparation**: Replace the CSV files in the `data/` directory with your own text classification dataset.

2. **Model Configuration**: Modify the model parameters in `model/model.py`:
   - Number of classes (`num_labels`)
   - Training hyperparameters (learning rate, batch size, epochs)
   - Model path and tokenizer configuration

3. **Environment Variables**: Adjust the following in the SWOP profile or task definitions:
   - `MAX_EPOCHS`: Number of training epochs
   - `MIN_PEERS`: Minimum number of peers required for Swarm Learning
   - `NODE_ID`: Identifier for each ML node

4. **Resource Requirements**: Update container resource specifications in the SWOP profile if needed (GPU allocation, memory limits).

     


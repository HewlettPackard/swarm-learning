Hugging Face PEFT
=================

This example demonstrates LLM fine-tuning in a federated scenario. It shows a BERT movie review classification application with GPU-based Parameter Efficient Fine-Tuning (PEFT) using LoRA (Low-Rank Adaptation) on the Swarm Learning platform. 

The Machine Learning program, after conversion to Swarm Learning for the Hugging Face transformers platform with PEFT integration, is in `examples/huggingface-peft/model`. The Hugging Face transformers-based file with PEFT support is called `model.py`.

This example shows the Swarm training of BERT movie reviews classification model using PEFT/LoRA technique with three ML nodes. ML nodes along with SL nodes are automatically spawned by SWOP nodes - all running on a single host. Swarm training gets initiated by the SWCI node and orchestrated by one SN node running on the same host. This example demonstrates memory-efficient fine-tuning using PEFT, which significantly reduces the number of trainable parameters while maintaining model performance.

The following image illustrates a cluster setup for the Hugging Face PEFT example:

<img width="80%" height="100%" src="../figs/huggingface-peft-cluster-setup.png">


-   This example uses one SN node. The name of the docker containers representing this node is SN1. SN1 is also the Sentinel Node. SN1 runs on the host 172.1.1.1.

-   Three SL and ML nodes are automatically spawned by SWOP node during training and removed after the training. This example uses one SWOP node that connects to the SN node. The name of the docker container representing this SWOP node is SWOP1. SWOP1 runs on the host 172.1.1.1.

-   Training is initiated by SWCI node \(SWCI1\) that runs on the host 172.1.1.1.

-   This example assumes that License Server already runs on host 172.1.1.1. All Swarm nodes connect to the License Server, on its default port 5814.


## <a name="SECTION_G1M_4RZ_LSB"/> Running the Hugging Face BERT PEFT example

1.  Navigate to `swarm-learning` folder (that is, parent to examples directory).

    ```
    cd swarm-learning
    ```

2.  Create a temporary workspace directory and copy `huggingface-peft` example.

    ```
    mkdir workspace
    cp -r examples/huggingface-peft/ workspace/huggingface-peft/
    cp -r examples/utils/gen-cert workspace/huggingface-peft/
    ```

3.  Run the gen-cert utility to generate certificates for each Swarm component using the command (`gen-cert -e <EXAMPLE-NAME> -i <HOST-INDEX>`):

    ```
    ./workspace/huggingface-peft/gen-cert -e huggingface-peft -i 1
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
    sed -i "s+<PROJECT-MODEL>+$(pwd)/workspace/huggingface-peft/model+g" workspace/huggingface-peft/swci/taskdefs/run_hf_task.yaml
    sed -i "s+<PROJECT>+$(pwd)/workspace/huggingface-peft+g" workspace/huggingface-peft/swci/taskdefs/run_hf_task.yaml
    sed -i "s+<SWARM-NETWORK>+host-1-net+g" workspace/huggingface-peft/swop/swop_profile.yaml
    sed -i "s+<LICENSE-SERVER-ADDRESS>+${APLS_IP}+g" workspace/huggingface-peft/swop/swop_profile.yaml
    sed -i "s+<PROJECT>+$(pwd)/workspace/huggingface-peft+g" workspace/huggingface-peft/swop/swop_profile.yaml
    sed -i "s+<PROJECT-CERTS>+$(pwd)/workspace/huggingface-peft/cert+g" workspace/huggingface-peft/swop/swop_profile.yaml
    sed -i "s+<PROJECT-CACERTS>+$(pwd)/workspace/huggingface-peft/cert/ca/capath+g" workspace/huggingface-peft/swop/swop_profile.yaml

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
    --key=workspace/huggingface-peft/cert/sn-1-key.pem --cert=workspace/huggingface-peft/cert/sn-1-cert.pem --capath=workspace/huggingface-peft/cert/ca/capath --apls-ip=${APLS_IP}
    ```

   Use the Docker logs command to monitor the Sentinel SN node and wait for the node to finish initializing. The Sentinel node is ready when these messages appear in the log output:
    ```
    swarm.blCnt : INFO : Starting SWARM-API-SERVER on port: 30304
    ```


9. Run SWOP node \(SWOP1\). 

    ```
    ./scripts/bin/run-swop -d --rm --name=swop1 --network=host-1-net --sn-ip=${SN_IP} --sn-api-port=${SN_API_PORT}              \
    --usr-dir=workspace/huggingface-peft/swop --profile-file-name=swop_profile.yaml --key=workspace/huggingface-peft/cert/swop-1-key.pem      \
    --cert=workspace/huggingface-peft/cert/swop-1-cert.pem --capath=workspace/huggingface-peft/cert/ca/capath -e SWOP_KEEP_CONTAINERS=True    \
    -e http_proxy= -e https_proxy= --apls-ip=${APLS_IP}
    ```
<blockquote>
    NOTE: If required, according to environment, modify IP and proxy either in the above command or in the swop profile file under `workspace/huggingface-peft/swop` folder.
</blockquote>

<blockquote>
   NOTE: `-e SWOP_KEEP_CONTAINERS=True` is an optional argument, by default it would be `False`. 
   SWOP_KEEP_CONTAINERS is set to True so that SWOP doesn't remove stopped SL and ML containers. With out this setting if there is any internal error in SL or ML then SWOP removes them automatically. Refer documentation of SWOP_KEEP_CONTAINERS for more details.
</blockquote>


10. Run SWCI node and observe sequential execution of two tasks – build task (`build_hf_user_image`) and run task (`run_hf_task`).

    ```
    ./scripts/bin/run-swci -ti --rm --name=swci1 --network=host-1-net --usr-dir=workspace/huggingface-peft/swci                        \
    --init-script-name=swci-init --key=workspace/huggingface-peft/cert/swci-1-key.pem --cert=workspace/huggingface-peft/cert/swci-1-cert.pem  \
    --capath=workspace/huggingface-peft/cert/ca/capath -e http_proxy= -e https_proxy= --apls-ip=${APLS_IP}
    ```

-   `build_hf_user_image` - builds Hugging Face transformers based user image with PyTorch backend and PEFT library support.

-   `run_hf_task` - runs Swarm training for BERT sentiment classification with PEFT/LoRA across three ML nodes.

<blockquote>
   NOTE: If required, according to the environment, modify SN IP in <code>workspace/huggingface-peft/swci/swci-init</code> file.
</blockquote>


11. Three nodes of Swarm trainings are automatically started when the run task (`run_hf_task`) gets assigned and executed. Open a new terminal and monitor the Docker logs of ML nodes for Swarm training. Swarm training ends with the following log message:

    ```
    SwarmCallback : INFO : All peers and Swarm training rounds finished. Final Swarm model was loaded.
    ```


   Final Swarm model with PEFT adapters is saved inside each user's specific directory in `workspace/huggingface-peft/<userN>`. All the dynamically spawned SL and ML containers exits after Swarm training if `SWOP_KEEP_CONTAINERS` is not set, otherwise SL and ML containers needs to be removed manually. The SN and SWOP nodes continues to run.

12. To clean up, run the `scripts/bin/stop-swarm` script on all the systems to stop and remove the container nodes of the previous run. If required, backup the container logs. Remove Docker networks (`host-1-net`) and Docker volume (`sl-cli-lib`), and delete the workspace directory.

## <a name="SECTION_DATA_REQUIREMENTS"/> Data Requirements

This example requires sentiment analysis data with the following structure:

-   **Training Data**: Three CSV files (`N1.csv`, `N2.csv`, `N3.csv`) containing text samples and their corresponding sentiment labels. Each file represents the private dataset for one ML node.

-   **Test Data**: One CSV file (`test_data.csv`) containing test samples for model evaluation.

-   **Pre-trained Model**: BERT base model downloaded from Hugging Face model hub.

The CSV files should have columns for text data and corresponding sentiment labels (e.g., star ratings from 1-5).

## <a name="SECTION_PEFT_DETAILS"/> PEFT (Parameter Efficient Fine-Tuning) Details

This example demonstrates the use of PEFT with LoRA (Low-Rank Adaptation) technique:

-   **LoRA Configuration**: 
    - Rank (`r`): 8
    - Alpha (`lora_alpha`): 32
    - Dropout (`lora_dropout`): 0.1
    - Target modules: Automatically selected based on BERT architecture
    - Bias: `"none"`

-   **Memory Efficiency**: PEFT significantly reduces the number of trainable parameters compared to full fine-tuning
-   **Performance**: Maintains competitive performance while using much less GPU memory
-   **Adapter Weights**: Only LoRA adapter weights are trained and synchronized across nodes

## <a name="SECTION_MODEL_DETAILS"/> Model Details

-   **Model Architecture**: BERT (Bidirectional Encoder Representations from Transformers) for sequence classification with LoRA adapters
-   **Framework**: Hugging Face Transformers with PyTorch backend and PEFT library
-   **Task**: Sentiment Analysis/Text Classification
-   **Training Strategy**: Parameter-efficient fine-tuning using LoRA
-   **GPU Support**: Enabled with CUDA 11.7 support and FP16 precision
-   **Hardware**: Optimized for GPU training with reduced memory footprint

## <a name="SECTION_ADVANTAGES"/> PEFT Advantages

1. **Reduced Memory Usage**: Only a small fraction of parameters are trainable
2. **Faster Training**: Fewer parameters to update during backpropagation
3. **Storage Efficiency**: Only adapter weights need to be stored/shared
4. **Maintained Performance**: Competitive results compared to full fine-tuning
5. **Swarm Efficiency**: Smaller model updates reduce communication overhead

## <a name="SECTION_CUSTOMIZATION"/> Customization

To adapt this example for your own text classification task:

1. **Data Preparation**: Replace the CSV files in the `data/` directory with your own text classification dataset.

2. **PEFT Configuration**: Modify the LoRA parameters in `model/model.py`:
   - Adjust rank (`r`) for different parameter efficiency vs. performance trade-offs
   - Change target modules based on your model architecture
   - Tune alpha and dropout values for optimal performance

3. **Model Configuration**: Modify the model parameters in `model/model.py`:
   - Number of classes (`num_labels`)
   - Training hyperparameters (learning rate, batch size, epochs)
   - Model path and tokenizer configuration

4. **Environment Variables**: Adjust the following in the SWOP profile or task definitions:
   - `MAX_EPOCHS`: Number of training epochs
   - `MIN_PEERS`: Minimum number of peers required for Swarm Learning
   - `NODE_ID`: Identifier for each ML node

5. **Resource Requirements**: Update container resource specifications in the SWOP profile if needed (GPU allocation, memory limits).

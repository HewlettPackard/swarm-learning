############################################################################
## (C)Copyright 2025 Hewlett Packard Enterprise Development LP
## Licensed under the Apache License, Version 2.0 (the "License"); you may
## not use this file except in compliance with the License. You may obtain
## a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
## WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
## License for the specific language governing permissions and limitations
## under the License.
##
## Dataset: Yelp Open Dataset (https://www.yelp.com/dataset)
## Model: bert-base-cased from Hugging Face (https://huggingface.co/bert-base-cased)
############################################################################

import os
import pandas as pd
from datasets import Dataset, load_dataset
from transformers import Trainer, TrainingArguments, AutoTokenizer, AutoModelForSequenceClassification
from swarmlearning.hf_transformers import SwarmCallback
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
import numpy as np
import torch
import time  # Add for timing
import matplotlib.pyplot as plt
import seaborn as sns


def main():
    # Start timing
    start_time = time.time()
    
    # Check for GPU and set device
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"[INFO] Using GPU: {torch.cuda.get_device_name(0)}")
        print(f"[INFO] GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    else:
        device = torch.device("cpu")
        print("[INFO] Using CPU")

    # Environment variables for Swarm Learning
    node_id = os.getenv('NODE_ID', 'n1')
    max_epochs = int(os.getenv('MAX_EPOCHS', 5))
    min_peers = int(os.getenv('MIN_PEERS', 3))
    swSyncInterval = 16 # Original sync interval for comparison

    # Load and preprocess data
    train_file = f"/tmp/test/N{node_id[-1]}.csv"
    test_file = "/tmp/test/test_data.csv"

    print(f"[INFO] Loading data for node {node_id}")
    data_load_start = time.time()
    
    train_df = pd.read_csv(train_file)
    train_df = train_df[['text', 'stars']].dropna()
    train_df['label'] = train_df['stars'].astype(int) - 1
    train_df = train_df[['text', 'label']].sample(n=4000, random_state=42)  # Same size as PEFT version

    test_df = pd.read_csv(test_file)
    test_df = test_df[['text', 'stars']].dropna()
    test_df['label'] = test_df['stars'].astype(int) - 1
    test_df = test_df[['text', 'label']].sample(n=1200, random_state=42)  # Same size as PEFT version

    train_dataset = Dataset.from_pandas(train_df)
    test_dataset = Dataset.from_pandas(test_df)
    
    data_load_end = time.time()
    print(f"[INFO] Data loading completed in {data_load_end - data_load_start:.2f} seconds")

    # Tokenization - using online model
    model_name = "bert-base-cased"
    print(f"[INFO] Loading tokenizer from {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=256)

    print("[INFO] Tokenizing datasets...")
    tokenization_start = time.time()
    
    tokenized_train = train_dataset.map(tokenize_function, batched=True)
    tokenized_test = test_dataset.map(tokenize_function, batched=True)

    # HuggingFace expects columns: input_ids, attention_mask, label
    tokenized_train.set_format("torch", columns=["input_ids", "attention_mask", "label"])
    tokenized_test.set_format("torch", columns=["input_ids", "attention_mask", "label"])
    
    tokenization_end = time.time()
    print(f"[INFO] Tokenization completed in {tokenization_end - tokenization_start:.2f} seconds")

    # Model setup - using online model
    print(f"[INFO] Loading base model from {model_name}")
    model_load_start = time.time()
    
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=5)
    model.to(device)
    
    model_load_end = time.time()
    print(f"[INFO] Model loading completed in {model_load_end - model_load_start:.2f} seconds")
    
    # Print model size info for comparison with PEFT
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[INFO] Total parameters: {total_params:,}")
    print(f"[INFO] Trainable parameters: {trainable_params:,} (100.00%)")

    # Training arguments
    output_dir = f"/tmp/test/model/saved_models/{node_id}_full"  # Add _full to distinguish from PEFT
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=max_epochs,
        per_device_train_batch_size=32,
        per_device_eval_batch_size=128,
        gradient_accumulation_steps=4,  # Effective batch size = 128
        evaluation_strategy="epoch",
        logging_dir=f"{output_dir}/logs",
        logging_steps=1,
        save_strategy="epoch",
        load_best_model_at_end=True,
        save_total_limit=2,
        fp16=torch.cuda.is_available(),  # Enable FP16 if CUDA available
        dataloader_pin_memory=True,      # Pin memory for faster GPU transfer
        remove_unused_columns=False,     # Keep all columns for better compatibility
    )

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        return {
            "accuracy": accuracy_score(labels, predictions),
            "f1": f1_score(labels, predictions, average='weighted'),
            "precision": precision_score(labels, predictions, average='weighted'),
            "recall": recall_score(labels, predictions, average='weighted'),
        }

    # SwarmCallback
    print(f"[INFO] Creating SwarmCallback with {min_peers} min peers...")
    swarm_callback = SwarmCallback(
        syncFrequency=swSyncInterval,
        minPeers=min_peers,
        model=model
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_test,
        compute_metrics=compute_metrics,
        callbacks=[swarm_callback]
    )

    # Train
    print(f"[INFO] Starting full fine-tuning training on {device}...")
    training_start_time = time.time()
    trainer.train()
    training_end_time = time.time()
    
    training_duration = training_end_time - training_start_time
    print(f"\n[INFO] Full fine-tuning Huggingface Trainer training completed on {device}")
    print(f"[INFO] Training duration: {training_duration:.2f} seconds ({training_duration/60:.2f} minutes)")

    # Evaluate
    print("[INFO] Starting evaluation...")
    eval_start_time = time.time()
    evaluation_results = trainer.evaluate()
    eval_end_time = time.time()

    eval_duration = eval_end_time - eval_start_time
    total_duration = time.time() - start_time
    
    print(f"\n[INFO] Full Fine-tuning Evaluation Results:")
    print("="*50)
    for k, v in evaluation_results.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")
    
    print(f"\n[INFO] Performance Summary:")
    print("="*50)
    print(f"  Data Loading Time: {data_load_end - data_load_start:.2f} seconds")
    print(f"  Tokenization Time: {tokenization_end - tokenization_start:.2f} seconds")
    print(f"  Model Loading Time: {model_load_end - model_load_start:.2f} seconds")
    print(f"  Training Time: {training_duration:.2f} seconds ({training_duration/60:.2f} minutes)")
    print(f"  Evaluation Time: {eval_duration:.2f} seconds")
    print(f"  Total Runtime: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
    print(f"  Final Accuracy: {evaluation_results.get('eval_accuracy', 'N/A'):.4f}")
    print(f"  Final F1 Score: {evaluation_results.get('eval_f1', 'N/A'):.4f}")
    
    # Additional performance metrics
    print(f"\n[INFO] Resource Usage Summary:")
    print("="*50)
    print(f"  Total Parameters: {total_params:,}")
    print(f"  Trainable Parameters: {trainable_params:,}")
    print(f"  Model Size: ~{total_params * 4 / (1024**2):.1f} MB (FP32)")
    print(f"  Sync Frequency: Every {swSyncInterval} batches")
    print(f"  Effective Batch Size: {32 * 4} samples")

    # Save the model
    print(f"[INFO] Saving full fine-tuned model to {output_dir}/final")
    model_save_start = time.time()
    
    os.makedirs(f"{output_dir}/final", exist_ok=True)
    model.save_pretrained(f"{output_dir}/final")
    tokenizer.save_pretrained(f"{output_dir}/final")
    
    model_save_end = time.time()
    print(f"[INFO] Model saving completed in {model_save_end - model_save_start:.2f} seconds")
    print(f"[INFO] Full fine-tuned model saved successfully!")

if __name__ == "__main__":
    main()
import logging
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from processing import DataProcessor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def finetune_model(model, train_dataset, val_dataset, num_epochs, batch_size, learning_rate):
    try:
        # Instantiate the tokenizer with the unk_token set
        tokenizer = AutoTokenizer.from_pretrained(
            "Salesforce/xgen-7b-8k-base",
            unk_token="<unk>",  # Set the unk_token
            trust_remote_code=True
        )

        # Enable token tracing
        tokenizer._tokenizer.enable_tracing()

        # Set up the optimizer and loss function, data loaders, and fine-tuning loop
        optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
        loss_fn = torch.nn.CrossEntropyLoss()
        train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=batch_size)

        # Fine-tuning loop
        for epoch in range(num_epochs):
            model.train()
            for inputs, labels in train_loader:
                optimizer.zero_grad()
                # Tokenize the text using the tokenizer
                tokenized_inputs = tokenizer(inputs, return_tensors="pt", padding=True, truncation=True)
                outputs = model(**tokenized_inputs)
                logits = outputs.logits
                loss = loss_fn(logits, labels)
                loss.backward()
                optimizer.step()

            model.eval()
            with torch.no_grad():
                total_loss = 0.0
                total_correct = 0
                total_samples = 0
                for inputs, labels in val_loader:
                    # Tokenize the text using the tokenizer
                    tokenized_inputs = tokenizer(inputs, return_tensors="pt", padding=True, truncation=True)
                    outputs = model(**tokenized_inputs)
                    logits = outputs.logits
                    loss = loss_fn(logits, labels)
                    total_loss += loss.item()
                    _, predicted = torch.max(logits, 1)
                    total_correct += (predicted == labels).sum().item()
                    total_samples += labels.size(0)

                # Calculate val_loss and val_accuracy
                val_loss = total_loss / len(val_loader)
                val_accuracy = total_correct / total_samples

                logging.info(f"Epoch {epoch+1}: Val Loss = {val_loss:.4f}, Val Accuracy = {val_accuracy:.4f}")

        # Disable token tracing
        tokenizer._tokenizer.disable_tracing()

    except Exception as e:
        logging.error(f"An error occurred during fine-tuning: {e}")
        raise

if __name__ == "__main__":
    # Get the directory of the currently executing script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the project directory path using the script's directory
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, "training_data")  # Construct the data directory path

    # Instantiate the DataProcessor class
    data_processor = DataProcessor(data_dir)

    # Load and process the datasets
    trained_dataset = data_processor.process_data()

    if trained_dataset is not None:
        # Calculate batch size and learning rate
        batch_size = 32
        num_samples = len(trained_dataset)
        num_epochs = 5
        learning_rate = 1e-4

        # Calculate validation dataset (val_dataset) for fine-tuning
        val_dataset = trained_dataset.sample(frac=0.2, random_state=42)

        # Instantiate the model for fine-tuning
        model = AutoModelForCausalLM.from_pretrained("Salesforce/xgen-7b-8k-base")

        # Fine-tune the model using the train_dataset and val_dataset
        finetune_model(model, trained_dataset, val_dataset, num_epochs, batch_size, learning_rate)

        logging.info("Fine-tuning completed successfully.")
    else:
        logging.error("Data processing failed.")
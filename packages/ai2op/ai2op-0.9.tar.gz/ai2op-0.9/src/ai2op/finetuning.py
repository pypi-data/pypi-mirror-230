import logging
import os
import pandas as pd
import nbformat
from nbconvert import PythonExporter
import chardet
import pdb
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class DataProcessor:
    def __init__(self, data_dir):
        # Initialize the data directory and logger
        self.data_dir = data_dir
        self.logger = self.setup_logging()

    def setup_logging(self):
        # Set up logging with both console and file handlers
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        
        log_file_path = os.path.join(self.data_dir, "data_processing.log")
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger

    def export_notebook_to_script(self, notebook_path, script_path):
        # Export Jupyter Notebook to a Python script
        nb = nbformat.read(notebook_path, as_version=nbformat.NO_CONVERT)
        exporter = PythonExporter()
        python_code, _ = exporter.from_notebook_node(nb)
        with open(script_path, "w") as f:
            f.write(python_code)

    def load_csv(self, file_path, encoding='utf-8', dtype=None):
        # Load CSV file with error handling for different encodings
        try:
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())
            file_encoding = result['encoding']
            return pd.read_csv(file_path, encoding=file_encoding, dtype=dtype, low_memory=False)
        except UnicodeDecodeError:
            self.logger.warning(f"UnicodeDecodeError encountered while loading CSV '{file_path}' with encoding '{encoding}'. Trying 'latin-1' encoding.")
            try:
                return pd.read_csv(file_path, encoding='latin-1', dtype=dtype, low_memory=False)
            except Exception as e:
                self.logger.error(f"Error loading CSV '{file_path}' with 'latin-1' encoding: {e}")
                return None
        except Exception as e:
            self.logger.error(f"Error loading CSV '{file_path}': {e}")
            return None

    def load_excel(self, file_path, encoding='utf-8'):
        # Load Excel file with error handling for different encodings
        try:
            return pd.read_excel(file_path, engine='openpyxl')
        except UnicodeDecodeError:
            self.logger.warning(f"UnicodeDecodeError encountered while loading Excel '{file_path}' with encoding '{encoding}'. Trying 'latin-1' encoding.")
            try:
                return pd.read_excel(file_path, engine='openpyxl', encoding='latin-1')
            except Exception as e:
                self.logger.error(f"Error loading Excel '{file_path}' with 'latin-1' encoding: {e}")
                return None
        except Exception as e:
            self.logger.error(f"Error loading Excel '{file_path}': {e}")
            return None

    def process_sroie_files(self, directory):
        # Process SROIE files from the given directory
        sroie_data = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'rb') as txt_file:
                            raw_data = txt_file.read()
                            detected_encoding = chardet.detect(raw_data)['encoding']
                            text_data = raw_data.decode(detected_encoding)
                            sroie_data.append(text_data)
                    except Exception as e:
                        self.logger.error(f"Error reading '{file_path}': {e}")
        
        sroie_df = pd.DataFrame({'data': sroie_data})
        return sroie_df

    def process_data(self):
        # Process various data files and concatenate them into a single dataset
        try:
            breakpoint() 
            root_dir = os.path.join(self.data_dir)

            # Load files
            currency_data = self.load_csv(os.path.join(root_dir, 'currency.csv'))
            fortune500_data = self.load_csv(os.path.join(root_dir, 'fortune500.csv'))
            msft_data = self.load_csv(os.path.join(root_dir, 'msft.csv'))
            snp_data = self.load_csv(os.path.join(root_dir, 's&p.csv'))

            balancesheets_data = self.load_csv(os.path.join(root_dir, 'bank_fail', 'balancesheets.csv'))
            banklist_data = self.load_csv(os.path.join(root_dir, 'bank_fail', 'banklist.csv'))

            final_datasets_dir = os.path.join(root_dir, 'income', 'final_datasets')
            final_datasets_files = [
                'Final_32_region_deciles_1958-2015.csv',
                'Final_Global_Income_Distribution.csv',
                'Final_Historical_data_ISO.csv'
            ]
            final_datasets_data = pd.concat(
                [pd.read_csv(os.path.join(final_datasets_dir, file)) for file in final_datasets_files]
            )

            input_data_dir = os.path.join(root_dir, 'income', 'input_data')
            input_data_files = [
                'WDI_GINI_data.csv'
            ]
            input_data = pd.concat(
                [pd.read_csv(os.path.join(input_data_dir, file)) for file in input_data_files]
            )

            mapping_files_dir = os.path.join(root_dir, 'income', 'mapping_files')
            mapping_files_files = [
                'GCAM_region_names.csv',
                'WIDER_mapping_file.csv'
            ]
            mapping_files = pd.concat(
                [pd.read_csv(os.path.join(mapping_files_dir, file)) for file in mapping_files_files]
            )

            train_dataset = pd.concat([currency_data, fortune500_data, msft_data, snp_data,
                                       balancesheets_data, banklist_data, final_datasets_data,
                                       input_data, mapping_files])

            etfs_dir = os.path.join(root_dir, 'nasdaq', 'etfs')
            etfs_files = [file for file in os.listdir(etfs_dir) if file.endswith('.csv')]
            etfs_data = pd.concat([pd.read_csv(os.path.join(etfs_dir, file)) for file in etfs_files])

            stocks_dir = os.path.join(root_dir, 'nasdaq', 'stocks')
            stocks_files = [file for file in os.listdir(stocks_dir) if file.endswith('.csv')]
            stocks_data = pd.concat([pd.read_csv(os.path.join(stocks_dir, file)) for file in stocks_files])

            symbols_valid_meta_data = self.load_csv(os.path.join(root_dir, 'nasdaq', 'symbols_valid_meta.csv'))

            train_dataset = pd.concat([train_dataset, etfs_data, stocks_data, symbols_valid_meta_data])

            news_dir = os.path.join(root_dir, 'news')
            news_files = [file for file in os.listdir(news_dir) if file.endswith('.csv')]
            news_data = pd.concat([pd.read_csv(os.path.join(news_dir, file)) for file in news_files])

            train_dataset = pd.concat([train_dataset, news_data])

            prediction_dir = os.path.join(root_dir, 'prediction')
            prediction_files = [file for file in os.listdir(prediction_dir) if file.endswith('.csv')]
            prediction_data = pd.concat([pd.read_csv(os.path.join(prediction_dir, file)) for file in prediction_files])

            train_dataset = pd.concat([train_dataset, prediction_data])

            sroie_dir = os.path.join(root_dir, 'sroie')
            sroie_df = self.process_sroie_files(sroie_dir)
            breakpoint() 
            train_dataset = pd.concat([train_dataset, sroie_df])  # Concatenate sroie_df with the train_dataset

            self.logger.info("Data processing completed successfully.")
            return train_dataset

        except Exception as e:
            self.logger.error(f"An error occurred during data processing: {e}")
            return None
        
def finetune_model(model, train_dataset, val_dataset, num_epochs, batch_size, learning_rate, output_dir):
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
            train_loss = 0.0
            for inputs, labels in train_loader:
                optimizer.zero_grad()
                # Tokenize the text using the tokenizer
                tokenized_inputs = tokenizer(inputs, return_tensors="pt", padding=True, truncation=True)
                outputs = model(**tokenized_inputs)
                logits = outputs.logits
                loss = loss_fn(logits, labels)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()

            # Logging the training loss
            train_loss /= len(train_loader)
            logging.info(f"Epoch {epoch+1}: Train Loss = {train_loss:.4f}")

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

        # Save the fine-tuned model and tokenizer
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)

        logging.info(f"Fine-tuned model and tokenizer saved to {output_dir}")

    except Exception as e:
        logging.error(f"An error occurred during fine-tuning: {e}")
        raise

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, "training_data")
    
    data_processor = DataProcessor(data_dir)
    
    # Load your datasets (replace with your actual data loading process)
    trained_dataset = data_processor.process_data()  # Replace with the correct method to get your training dataset

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
        
        # Define output directory to save the fine-tuned model and tokenizer
        output_dir = os.path.join(project_dir, "fine_tuned_model")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Fine-tune the model using the train_dataset and val_dataset
        finetune_model(model, trained_dataset, val_dataset, num_epochs, batch_size, learning_rate, output_dir)

        logging.info("Fine-tuning completed successfully.")
    else:
        logging.error("Data processing failed.")


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def finetune_model(model, train_dataset, val_dataset, num_epochs, batch_size, learning_rate, output_dir):
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
            train_loss = 0.0
            for inputs, labels in train_loader:
                optimizer.zero_grad()
                # Tokenize the text using the tokenizer
                tokenized_inputs = tokenizer(inputs, return_tensors="pt", padding=True, truncation=True)
                outputs = model(**tokenized_inputs)
                logits = outputs.logits
                loss = loss_fn(logits, labels)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()

            # Logging the training loss
            train_loss /= len(train_loader)
            logging.info(f"Epoch {epoch+1}: Train Loss = {train_loss:.4f}")

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

        # Save the fine-tuned model and tokenizer
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)

        logging.info(f"Fine-tuned model and tokenizer saved to {output_dir}")

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
if __name__ == "__main__":

    # ---- Main block from processing.py ----

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, "training_data")
    
    data_processor = DataProcessor(data_dir)
    
    # Load your datasets (replace with your actual data loading process)
    trained_dataset = data_processor.process_data()  # Replace with the correct method to get your training dataset

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
        
        # Define output directory to save the fine-tuned model and tokenizer
        output_dir = os.path.join(project_dir, "fine_tuned_model")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Fine-tune the model using the train_dataset and val_dataset
        finetune_model(model, trained_dataset, val_dataset, num_epochs, batch_size, learning_rate, output_dir)

        logging.info("Fine-tuning completed successfully.")
    else:
        logging.error("Data processing failed.")


    # ---- Main block from finetuning.py ----

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
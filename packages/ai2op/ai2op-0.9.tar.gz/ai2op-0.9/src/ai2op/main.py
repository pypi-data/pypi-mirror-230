import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Importing the functions from their respective files
from summarize import summarize
from interpret import interpret
from headline import headline

# Configuration and logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Instantiate the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("Salesforce/xgen-7b-8k-inst", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("Salesforce/xgen-7b-8k-inst")
print(tokenizer.special_tokens_map)

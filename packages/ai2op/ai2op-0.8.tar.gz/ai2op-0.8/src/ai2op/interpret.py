import torch

def interpret(text, tokenizer, model):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    predicted_class = torch.argmax(outputs.logits, dim=-1).item()
    return predicted_class

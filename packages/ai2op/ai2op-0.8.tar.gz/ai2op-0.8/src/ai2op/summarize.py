from transformers import TextGenerationPipeline

def summarize(model, tokenizer):
    return TextGenerationPipeline(model=model, tokenizer=tokenizer)

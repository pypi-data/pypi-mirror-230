from transformers import Text2TextGenerationPipeline  # Replace with the actual pipeline or model you're using

def headline(model, tokenizer, summary, interpret):
    
    # Combine the summary and interpretation into a single string, with a more targeted prompt
    input_text = f"Create a headline that is short, catchy, and accurately reflects the summary and interpretation below:\nSummary: {summary}\nInterpretation: {interpret}"
    
    # Initialize the Text2Text generation pipeline
    pipeline = Text2TextGenerationPipeline(model=model, tokenizer=tokenizer)
    
    # Generate the headline
    generated_output = pipeline(input_text)
    generated_headline = generated_output[0]['generated_text']
    
    return generated_headline

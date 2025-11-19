from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

print("Loading tokenizer...")
tok = AutoTokenizer.from_pretrained("google/flan-t5-small")

print("Loading model...")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")

print("Model download OK!")

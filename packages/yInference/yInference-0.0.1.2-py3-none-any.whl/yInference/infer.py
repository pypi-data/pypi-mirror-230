from transformers import AutoTokenizer,AutoModelForCausalLM

def inference(text="",model_name="",max_input_tokens = 1000,max_output_tokens = 100):
  model = AutoModelForCausalLM.from_pretrained(model_name)
  
  tokenizer = AutoTokenizer.from_pretrained(model_name)
  input_ids = tokenizer.encode(
      text,
      return_tensors = "pt",
      truncation = True,
      max_length = max_input_tokens
  )
  device = model.device
  generated_token_with_prompt = model.generate(
      input_ids = input_ids.to(device),
      max_length = max_output_tokens
  )
  generated_text_with_prompt = tokenizer.batch_decode(generated_token_with_prompt,
                                                      skip_special_tokens=True)
  generated_text_answer = generated_text_with_prompt[0][len(text):]

  return generated_text_answer
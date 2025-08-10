from email import charset
import google.generativeai as genai
import os
import datetime

#configuration
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
generation_config = {'temperature':0.9, 'top_p':0.95, 'max_output_tokens':10000}
 
final_prompt = []

prompt_file_path = r"C:\Users\meetd\Desktop\Pro1\sys_prompt.txt"
output_directory = r"C:\Users\meetd\Desktop\Pro1\generated_texts"
user_prompt_file_path = r"C:\Users\meetd\Desktop\Pro1\user_prompt.txt"

try:
    # Read the system prompt first
    if os.path.exists(prompt_file_path):
        with open(prompt_file_path, "r", encoding='utf-8') as f:
            final_prompt.append(f.read())
            print("Using system prompt from 'sys_prompt.txt'.")
    
    # Check for and add the user prompt if it exists and is not empty
    if os.path.exists(user_prompt_file_path) and os.path.getsize(user_prompt_file_path) > 0:
        with open(user_prompt_file_path, "r", encoding='utf-8') as f:
            final_prompt.append(f.read())
            print("Adding user prompt from 'user_prompt.txt'.")

    if final_prompt:
        model = genai.GenerativeModel("gemini-2.5-flash", generation_config=generation_config)
        response = model.generate_content(final_prompt) # Pass the list of prompts
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = f"model_response_{timestamp}.txt"
        output_file_path = os.path.join(output_directory, output_filename)
        
        response_content = response.text
        
        os.makedirs(output_directory, exist_ok=True)
        
        with open(output_file_path, "w", encoding='utf-8') as f:
            f.write(response_content) 
    
        print(f"Model response successfully saved to: {output_file_path}")
    else:
        print("Error: No valid prompt file found.")

except FileNotFoundError:
    print(f"Error: A required file was not found.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

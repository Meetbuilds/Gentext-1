from email import charset
import google.generativeai as genai
import os
import datetime

#configuration
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
generation_config = {'temperature':0.9, 'top_p':0.95, 'max_output_tokens':2000}
 

prompt_file_path = r"C:\Users\meetd\Desktop\Pro1\system_prompt.txt"
output_directory = r"C:\Users\meetd\Desktop\Pro1\generated_texts"

try:
    with open(prompt_file_path, "r", encoding='utf-8') as f:
        system_prompt = f.read()

    model = genai.GenerativeModel("gemini-2.5-flash", generation_config=generation_config)

    response= model.generate_content(system_prompt)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"token_count_response_{timestamp}.txt"
    output_file_path = os.path.join(output_directory, output_filename)
    
    response_content = response.text
    
    os.makedirs(output_directory, exist_ok=True)
    
    with open(output_file_path, "w", encoding='utf-8') as f:
        f.write(response_content) 

    print(f"Model response successfully saved to: {output_file_path}")

except FileNotFoundError:
    print(f"Error: The file '{prompt_file_path}' was not found.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")


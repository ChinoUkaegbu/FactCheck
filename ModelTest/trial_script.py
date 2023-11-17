from openai import OpenAI
import pandas as pd

# Initialize OpenAI client
client = OpenAI(api_key='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')

def get_chat_completion(prompt, speaker, claim_date, subject, model="gpt-3.5-turbo"):
    # Add relevant prompt and context to the input statement
    prompt = f"Fact check the following statement with a response of 'true', 'false' or 'unclear' - {input_statement}.\nContext:\nSpeaker: {speaker}\nClaim Date: {claim_date}\n Subject matter: {subject}."
    # Making an API request using the OpenAI Python library
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a professional factchecker with an experience of 10+ years"},
            {"role": "user", "content": prompt}
        ]
    )
    
    # Returning the content of the API response
    return completion.choices[0].message.content

# Load CSV file
input_csv_path = 'trial_fact_input.csv'
output_csv_path = 'output_data_w_both_labels.csv'


df = pd.read_csv(input_csv_path)

# Create an empty list to store results
output_data = []

# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    input_statement = row['Statement']
    speaker = row['Speaker']
    subject = row['Subject']
    claim_date = row['Date (when statement was made)']
    label_source_text = row['Label']

    label_source_num = 0 # Default label (unclear)
    if "true" in label_source_text.lower():
        label_source_num = 1  # Set label to 1 if "true" is present
    elif "false" in label_source_text.lower():
        label_source_num = 2  # Set label to 2 if "false" is present

    
    # Get the response from the OpenAI API
    api_response = get_chat_completion(input_statement, speaker, claim_date, subject)

    # Determine the label based on the presence of "true", "false", or "unclear" in the responses
    label_model = 0  # Default label (unclear)
    if "true" in api_response.lower():
        label_model = 1  # Set label to 1 if "true" is present
    elif "false" in api_response.lower():
        label_model = 2  # Set label to 2 if "false" is present


    # Append the input statement and API response to the output list
    output_data.append({
        'input_statement': input_statement,
        'api_response': api_response,
        'label_model': label_model,
        'label_source_num': label_source_num
    })

# Convert the list of dictionaries to a DataFrame
output_df = pd.DataFrame(output_data)

# Save the DataFrame to a new CSV file
output_df.to_csv(output_csv_path, index=False)

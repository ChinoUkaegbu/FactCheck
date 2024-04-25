import os
from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_community.utilities import GoogleSearchAPIWrapper

from langchain.agents import AgentType, Tool, initialize_agent
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent

# Load environment variables for API keys
os.environ["OPENAI_API_KEY"] = "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"
os.environ["GOOGLE_CSE_ID"] = "51b6c946e572b4eb1"
os.environ["GOOGLE_API_KEY"] = "AIzaSyDyqYsccbQPF0NNjBSt-BOIYT5eZsYIFCY"

import pandas as pd

# Initialize the LLM
llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo") #note llm used and ChatOpenAI vs OpenAI


# Initialize Google Search API for Web Search
search = GoogleSearchAPIWrapper()

tools = [
    Tool(
        name="Search",
        func=search.run,
        description="useful for when you need to ask with search",
    )
]

# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/react")
print(prompt)

#early_stopping_method set to generate so we can get final output
agent_executor = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, handle_parsing_errors=True, max_iterations=3, early_stopping_method="generate", return_intermediate_steps=True)



# Load CSV file
input_csv_path = 'trial_fact_input_full.csv'
output_csv_path = 'curr_results.csv'


df = pd.read_csv(input_csv_path)

# Create an empty list to store results
output_data = []

# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    statement_id = row['ID']
    input_statement = row['Statement']
    speaker = row['Speaker']
    position = row["Speaker's Position"]
    location = row['Context (Location)']
    claim_date = row['Date (when statement was made)']
    subject = row['Subject']
    label_source_text = row['Label']

    label_source_num = 0 # Default label (unclear)
    if "true" in label_source_text.lower():
        label_source_num = 1  # Set label to 1 if "true" is present
    elif "false" in label_source_text.lower():
        label_source_num = 2  # Set label to 2 if "false" is present

    
    # Get the response from the OpenAI API
    #api_response = get_chat_completion(input_statement, speaker, position, location, claim_date, subject)
    response = agent_executor.invoke({"input": f"You are a professional factchecker with an experience of 10+ years and you MUST provide a response of 'true', 'false', or 'unclear'. Fact check the following statement- {input_statement}"})
    api_response = response["output"]
    api_metadata = response["intermediate_steps"]


    # Determine the label based on the presence of "true", "false", or "unclear" in the responses
    label_model = 0  # Default label (unclear)
    if "true" in api_response.lower()[:7]: #checks first seven characters (seven characters in 'unclear') as the model leads with the verdict before an explanation and sometimes the explanation may contain the charcaters but may not be the verdict.
        label_model = 1  # Set label to 1 if "true" is present
    elif "false" in api_response.lower()[:7]:
        label_model = 2  # Set label to 2 if "false" is present


    # Append the input statement, API response, etc to the output list
    output_data.append({
        'statement_id': statement_id,
        'input_statement': input_statement,
        'api_response': api_response,
        'api_metadata': api_metadata,
        'label_model': label_model,
        'label_source_num': label_source_num,
        'label_source_text': label_source_text
    })

# Convert the list of dictionaries to a DataFrame
output_df = pd.DataFrame(output_data)

# Save the DataFrame to a new CSV file
output_df.to_csv(output_csv_path, index=False)

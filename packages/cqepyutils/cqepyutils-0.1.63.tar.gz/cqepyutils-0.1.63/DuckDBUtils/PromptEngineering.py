from lifelines.datasets import load_dd
from lifelines import KaplanMeierFitter
import os
from langchain.llms import OpenAI
from langchain import PromptTemplate


# Load the dataset
data = load_dd()

# Create an instance of KaplanMeierFitter
kmf = KaplanMeierFitter()

# Fit the data into the model
kmf.fit(durations = data['duration'], event_observed = data['observed'])

# Create an estimate of the survival function
kmf.plot_survival_function()

# Create an instance of KaplanMeierFitter
kmf = KaplanMeierFitter()

# Fit the data into the model
kmf.fit(durations = data['duration'], event_observed = data['observed'])

# Calculate the median survival time
median_survival_time = kmf.median_survival_time_

print("The median survival time is:", median_survival_time)


#
# # set up the environment with respected API key
# os.environ["OPENAI_API_KEY"] = ""
#
# #os.environ["COHERE_API_KEY"] = ""
#
# #os.environ["HUGGINGFACEHUB_API_TOKEN"] = ""
#
#
# # you can choose between different llm models
# llm = OpenAI(model_name="text-davinci-003")
#
# #llm = HuggingFaceHub(repo_id="google/flan-t5-xl")
#
# #llm = Cohere(model='command-xlarge')
#
# text = "How read book effectively?"
#
# print(llm(text))
#
#
#
#
# # Define the template
# template = """
# Give me step by step instruction in table format:
#
# {text}
# """
#
# # Create the prompt template object
# summary_prompt = PromptTemplate(
#     input_variables=["text"], # The name of the input variable
#     template=template # The template string
# )
#
# # Format the prompt with some text
# text = "I want to backflip"
# formatted_prompt = summary_prompt.format(text=text)
#
# # Print the formatted prompt
# print(llm(formatted_prompt))
import os
api_key = os.environ['GENAI_API_KEY']

os.environ["GOOGLE_API_KEY"] = api_key

from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize the Gemini Pro model
llm = ChatGoogleGenerativeAI(model="gemini-pro")

response = llm.invoke("Explain quantum computing in simple terms.")
print(response.content)

# chat_model.py
import os
import pandas as pd
from datetime import date
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import LLMChain
from langchain.schema.runnable import RunnableMap

class AllRetriever:
    def get_relevant_documents(self, query):
        # Get raw text documents
        raw_docs = vectordb.get()["documents"]
        # Wrap each string in a Document object
        return [Document(page_content=doc) for doc in raw_docs]

retriever = AllRetriever()


# Set Gemini API key
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Load and process CSV
df = pd.read_csv("flat_data.csv")

# Convert date to datetime
df["date"] = pd.to_datetime(df["date"])

# Combine into natural language
df["combined"] = df.apply(lambda row: (
    f"Flight ID {row['id']} - {row['name']} ({row['model']}) with capacity {row['capacity']} "
    f"is scheduled on {row['date'].strftime('%Y-%m-%d')} from {row['from']} to {row['to']}."
), axis=1)

# Create LangChain Documents
docs = [Document(page_content=row) for row in df["combined"].tolist()]
splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0)
split_docs = splitter.split_documents(docs)

# Embed using Gemini
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectordb = Chroma.from_documents(split_docs, embedding, persist_directory="./chroma_db")
vectordb.persist()



retriever = AllRetriever()
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)

# Prompt template
today = date.today().isoformat()

prompt_template = PromptTemplate.from_template("""
You are a flight assistant. Today is {today}.

Use the following flight information to answer the user's question accurately.

Context:
{context}

Question:
{question}
""")

# Combine retrieved documents into a single prompt
llm_chain = LLMChain(llm=llm, prompt=prompt_template)
stuff_chain = create_stuff_documents_chain(llm=llm, prompt=prompt_template)


# Create full RAG chain
rag_chain = RunnableMap({
    "context": lambda x: retriever.get_relevant_documents(x["question"]),
    "question": lambda x: x["question"],
    "today": lambda x: today
}) | stuff_chain

# ✅ Final interface
def process_chat(query: str):
    return rag_chain.invoke({"question": query})

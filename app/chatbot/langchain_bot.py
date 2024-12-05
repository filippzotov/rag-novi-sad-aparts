import os
import pandas as pd
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate  # Import PromptTemplate
from app.database import (
    engine,
)  # Ensure this import points to your DB connection module

# Configure OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name="gpt-4o-mini")

# Load data from the database into a DataFrame
query = "SELECT * FROM apartments;"  # Adjust this query to fetch the data you need
df = pd.read_sql_query(query, engine)

# Convert DataFrame to a list of documents
# Each document represents an apartment as a text description
documents = []
for index, row in df.iterrows():
    features = []

    # List of boolean columns to check
    boolean_columns = [
        "has_washing_machine",
        "has_oven",
        "has_fridge",
        "has_tv",
        "has_air_conditioning",
        "has_french_bed",
        "has_bathtub",
        "has_pullout_bed",
        "has_corner_sofa",
        "has_dishwasher",
        "has_vacuum_cleaner",
        "has_elevator",
        "has_intercom",
        "has_surveillance",
        "has_wheelchair_ramp",
        "allows_pets",
        "allows_business_use",
        "has_shared_entrance",
        "has_shared_electricity_meter",
        "is_renovated",
    ]

    # Mapping of column names to user-friendly feature names
    feature_names = {
        "has_washing_machine": "washing machine",
        "has_oven": "oven",
        "has_fridge": "fridge",
        "has_tv": "TV",
        "has_air_conditioning": "air conditioning",
        "has_french_bed": "French bed",
        "has_bathtub": "bathtub",
        "has_pullout_bed": "pull-out bed",
        "has_corner_sofa": "corner sofa",
        "has_dishwasher": "dishwasher",
        "has_vacuum_cleaner": "vacuum cleaner",
        "has_elevator": "elevator",
        "has_intercom": "intercom",
        "has_surveillance": "surveillance",
        "has_wheelchair_ramp": "wheelchair ramp",
        "allows_pets": "allows pets friendly",
        "allows_business_use": "allows business use",
        "has_shared_entrance": "shared entrance",
        "has_shared_electricity_meter": "shared electricity meter",
        "is_renovated": "recently renovated",
    }

    # Collect features that are True
    for col in boolean_columns:
        if row.get(col):
            features.append(feature_names[col])

    # Collect other fields if they are not empty or None
    size = f"{row['size_sqm']} sqm" if pd.notnull(row.get("size_sqm")) else None
    rooms = f"{row['room_count']} rooms" if pd.notnull(row.get("room_count")) else None
    bedrooms = (
        f"{row['bedroom_count']} bedrooms"
        if pd.notnull(row.get("bedroom_count")) and row.get("bedroom_count") > 0
        else None
    )
    bathrooms = (
        f"{row['bathroom_count']} bathrooms"
        if pd.notnull(row.get("bathroom_count")) and row.get("bathroom_count") > 0
        else None
    )
    toilets = (
        f"{row['toilet_count']} toilets"
        if pd.notnull(row.get("toilet_count")) and row.get("toilet_count") > 0
        else None
    )
    price = (
        f"{row['price_per_month']} euro per month"
        if pd.notnull(row.get("price_per_month"))
        else None
    )
    street = row.get("street_name") if row.get("street_name") else None
    municipality = (
        row.get("municipality_name") if row.get("municipality_name") else None
    )
    neighborhoods = (
        ", ".join(row["neighborhoods"]) if row.get("neighborhoods") else None
    )
    floor = (
        f"Floor {row['floor_number']}" if pd.notnull(row.get("floor_number")) else None
    )
    construction_year = (
        f"Built in {row['construction_year']}"
        if pd.notnull(row.get("construction_year"))
        else None
    )
    heating_types = (
        ", ".join(row["heating_types"]) if row.get("heating_types") else None
    )
    deposit = (
        f"Deposit: {row['deposit']} euro" if pd.notnull(row.get("deposit")) else None
    )
    available_date = (
        row.get("available_date").strftime("%Y-%m-%d")
        if row.get("available_date")
        else "immediately"
    )
    listing_url = row.get("listing_url", "N/A")

    # Build the description only with available data
    description_parts = [
        f"Apartment for rent",
        f"at {street}" if street else None,
        f"in {municipality}" if municipality else None,
        f"neighborhoods: {neighborhoods}" if neighborhoods else None,
        ".",
        f"Price: {price}." if price else None,
        f"Size: {size}." if size else None,
        f"{rooms}." if rooms else None,
        f"{bedrooms}." if bedrooms else None,
        f"{bathrooms}." if bathrooms else None,
        f"{toilets}." if toilets else None,
        f"{floor}." if floor else None,
        f"{construction_year}." if construction_year else None,
        f"Heating types: {heating_types}." if heating_types else None,
        # f"{deposit}." if deposit else None,
        f"Features: {', '.join(features)}." if features else None,
        f"Available from: {available_date}.",
        f"URL: {listing_url}",
    ]

    # Filter out None values and join the parts
    doc = " ".join(filter(None, description_parts))
    print(doc)
    documents.append(doc)

# Create embeddings for the documents
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Create a vector store from the documents
if not documents:
    print(
        "Debug: No documents generated from the database query. Skipping vectorstore creation."
    )
    vectorstore = None  # Handle the case where the vectorstore isn't created
else:
    try:
        # Create embeddings for the documents
        vectorstore = FAISS.from_texts(documents, embeddings)
    except Exception as e:
        print(f"Debug: Error during FAISS vectorstore creation: {e}")
        raise
# Initialize memory to keep track of conversation history
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Create a retriever with a limit of 3 results

# Define a custom prompt to enforce English language
QA_PROMPT = PromptTemplate(
    template="""
You are a helpful assistant that helps users choose apartments from the database.

You should always respond in English.

All Prices are in EURO.

When the user asks what you can do, explain that you can help find apartments based on their preferences.

If the user's information is insufficient, provide a few example apartments from the database that are generally appealing. Politely mention that these are just examples and encourage the user to add more filters such as location, price range, number of bedrooms, etc., for personalized recommendations.

Once you have enough information, provide details of up to 3 matching apartments.

Present the results in the following format for each apartment:
- URL: [apartment listing URL]
- Price: [price]
- Street: [street address]

If no filters are provided, encourage the user to refine their preferences for better matches.

Ensure that your responses are friendly and professional, and focus on making the interaction helpful and engaging.

Use the following conversation and context to answer the question.

{chat_history}

Question: {question}

Context:
{context}

Answer:""",
    input_variables=["chat_history", "question", "context"],
)


# Ensure the retriever and chain are created only if the vectorstore exists
if vectorstore:
    # Create a retriever with a limit of 3 results
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # Create a Conversational Retrieval Chain with the custom prompt
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        verbose=True,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT},
    )
else:
    print("Debug: Vectorstore is None. Retrieval and QA chain will not be initialized.")


def reset_memory():
    """Resets the conversation memory."""
    memory.clear()
    print("Debug: Memory has been reset.")


def ask_question(question):
    try:
        # Execute the chain with the input question
        response = qa_chain({"question": question})
        # Debugging: Log the raw response
        print("Debug: Raw Response:", response)
        # Return the assistant's answer
        return response["answer"]
    except Exception as e:
        # Handle exceptions gracefully
        print("Debug: Error Occurred")
        print(f"Error: {e}")
        return "I encountered an issue processing your request. Could you please rephrase or provide more details?"

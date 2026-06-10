from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from transformers import pipeline
import streamlit as st
import torch


EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@st.cache_resource
def load_vectorstore():

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL
    )

    vectorstore = FAISS.load_local(
        "finance_faiss",
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore


@st.cache_resource
def load_generator():

    generator = pipeline(
        "text-generation",
        model="google/gemma-2-2b-it",
        device_map="auto",
        torch_dtype=torch.float16
    )

    return generator


vectorstore = load_vectorstore()
generator = load_generator()


def ask_question(query):

    docs_with_scores = vectorstore.similarity_search_with_score(
        query,
        k=3
    )

    retrieved_docs = [
        doc
        for doc, score in docs_with_scores
    ]

    context = "\n\n".join(
        doc.page_content[:500]
        for doc in retrieved_docs
    )

    prompt = f"""
You are a financial analyst.

Use ONLY the provided context.

Instructions:
- Answer using only the provided context.
- Use bullet points when appropriate.
- Mention financial figures exactly.
- Summarize instead of copying text.
- If information is unavailable, say:
"The information is not available in the provided documents."

Context:
{context}

Question:
{query}

Answer:
"""

    response = generator(
        prompt,
        max_new_tokens=150,
        do_sample=False
    )

    answer = response[0]["generated_text"]

    if "Answer:" in answer:
        answer = answer.split(
            "Answer:"
        )[-1].strip()

    sources = []

    for doc in retrieved_docs:

        sources.append(
            {
                "file": doc.metadata.get(
                    "source",
                    "Unknown"
                ).split("\\")[-1],

                "page": doc.metadata.get(
                    "page_label",
                    "N/A"
                )
            }
        )

    return answer, sources
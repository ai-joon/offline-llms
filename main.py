from loader import load_index
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

# 1) Load prebuilt FAISS index (built separately via loader.py CLI)
INDEX_DIR = r"C:\Source\research\faiss_index"  # change to your saved index folder
db = load_index(INDEX_DIR, emb_model="nomic-embed-text", base_url="http://localhost:11434")

# 4) Retriever
retriever = db.as_retriever(search_kwargs={"k": 4})

# 5) LLM (local via Ollama)
llm = Ollama(model="qwen2.5:0.5b-instruct", base_url="http://localhost:11434", temperature=0.2)

# 6) Prompt + RAG call
template = """You are a concise assistant. Use the context to answer.
If the answer isn't in the context, say you don't know.

Question: {question}
Context:
{context}
Answer:"""
prompt = PromptTemplate.from_template(template)

def rag_answer(query: str):
    ctx_docs = retriever.invoke(query)
    context = "\n\n".join(d.page_content for d in ctx_docs)
    return llm.invoke(prompt.format(question=query, context=context))

print(rag_answer("이 문서에 대한 요약을 제공하시오."))
import os
import json
import time
import ssl
import httpx
import urllib3
import gradio as gr
from typing import List
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pinecone import Pinecone

# LlamaIndex Imports
from llama_index.core import (
    Settings, 
    StorageContext, 
    VectorStoreIndex, 
    SimpleDirectoryReader,
    get_response_synthesizer,
    PromptTemplate
)
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.cohere import Cohere
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.llms import ChatMessage
from llama_index.core.schema import TextNode, NodeWithScore

# --- 1. Settings & Security (NetFree/SSL Bypass) ---
load_dotenv()
os.environ['CURL_CA_BUNDLE'] = ""
os.environ['HTTPX_VERIFY'] = "False" 
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

unsafe_client = httpx.Client(verify=False)

# --- 2. Model & DB Configuration ---
Settings.embed_model = CohereEmbedding(
    api_key=os.getenv("COHERE_API_KEY"), 
    model_name="embed-multilingual-v3.0", 
    http_client=unsafe_client
)
Settings.llm = Cohere(
    api_key=os.getenv("COHERE_API_KEY"), 
    model="command-r-plus-08-2024",
)
Settings.node_parser = MarkdownNodeParser()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), ssl_verify=False)
pinecone_index = pc.Index("rag-project")
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Load Index
index = VectorStoreIndex.from_vector_store(vector_store)
retriever = index.as_retriever(similarity_top_k=5)
response_synthesizer = get_response_synthesizer(
    llm=Settings.llm, 
    response_mode="tree_summarize",
    summary_template=PromptTemplate(
        "You are a professional AI assistant for developers.\n"
        "Always respond in the same language as the user's question.\n"
        "Context info:\n{context_str}\n"
        "Query: {query_str}\nAnswer:"
    )
)

# --- 3. Workflow Definition ---
class RetrievalEvent(Event):
    query: str

class StructuredSearchEvent(Event):
    query: str
    category: str

class SynthesizeEvent(Event):
    query: str
    context: str

class SmartAgentWorkflow(Workflow):
    @step
    async def route_query(self, ev: StartEvent) -> RetrievalEvent | StructuredSearchEvent:
        query = ev.query
        routing_prompt = f"""
        Analyze the user query: "{query}"
        Categories: 'rules', 'decisions', 'warnings', or 'none'.
        Respond ONLY with JSON: {{"route": "structured", "category": "rules"}} or {{"route": "semantic", "category": "none"}}
        """
        response = Settings.llm.chat([ChatMessage(role="user", content=routing_prompt)])
        clean_res = str(response.message.content).strip().replace("```json", "").replace("```", "")
        result = json.loads(clean_res)

        if result["route"] == "structured":
            return StructuredSearchEvent(query=query, category=result["category"])
        return RetrievalEvent(query=query)

    @step
    async def handle_structured_search(self, ev: StructuredSearchEvent) -> SynthesizeEvent:
        try:
            with open("structured_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data["items"].get(ev.category, [])
            return SynthesizeEvent(query=ev.query, context=str(items))
        except:
            return SynthesizeEvent(query=ev.query, context="No structured data found.")

    @step
    async def handle_retrieval(self, ev: RetrievalEvent) -> SynthesizeEvent:
        nodes = retriever.retrieve(ev.query)
        context = "\n\n".join([n.node.get_content() for n in nodes])
        return SynthesizeEvent(query=ev.query, context=context)

    @step
    async def synthesize_response(self, ev: SynthesizeEvent) -> StopEvent:
        wrapped_node = NodeWithScore(node=TextNode(text=ev.context), score=1.0)
        response = response_synthesizer.synthesize(query=ev.query, nodes=[wrapped_node])
        return StopEvent(result=str(response))

# --- 4. Gradio UI ---
agent_workflow = SmartAgentWorkflow(timeout=120)

async def predict_workflow(message, history):
    try:
        result = await agent_workflow.run(query=message)
        return str(result)
    except Exception as e:
        return f"❌ Error: {str(e)}"

custom_css = """
.gradio-container { direction: rtl; }
#chatbot { height: 600px !important; }
"""

with gr.Blocks(theme=gr.themes.Soft(), css=custom_css) as demo:
    gr.Markdown("# 🤖 Smart AI Agentic Assistant")
    gr.ChatInterface(fn=predict_workflow, chatbot=gr.Chatbot(elem_id="chatbot"))

if __name__ == "__main__":
    demo.launch()
from fastapi import FastAPI
from pydantic import BaseModel
from src.llm_client import LLMClient
from src.conversation import Conversation
from src.agent import Agent
from dotenv import load_dotenv
import os
from src.rag import retrieve_context, build_vectorstore

load_dotenv()
app = FastAPI()

conversation = Conversation()
client = LLMClient(api_key=os.getenv("OPENROUTER_API_KEY"))
agent = Agent(llm_client=client)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


class AgentResponse(BaseModel):
    response: str
    steps: list


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    conversation.add_user_message(request.message)
    response = client.stream_response(conversation.get_history())
    conversation.add_assistant_message(response)
    return ChatResponse(response=response)


@app.get("/history")
async def get_history():
    return {"history": conversation.get_history()}


@app.delete("/history")
async def clear_history():
    conversation.messages = []
    return {"message": "conversation cleared"}


@app.post("/rag-chat", response_model=ChatResponse)
async def rag_chat(request: ChatRequest):
    try:
        context = retrieve_context(request.message)

        augmented_message = f"""Use the following context to answer the question.

Context:
{context}

Question: {request.message}"""

        # Store original question, not augmented one
        conversation.add_user_message(request.message)
        
        temp_messages = conversation.get_history()[:-1] + [
            {"role": "user", "content": augmented_message}
        ]
        response = client.stream_response(temp_messages)
        conversation.add_assistant_message(response)

        return ChatResponse(response=response)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return ChatResponse(response=f"Error: {str(e)}")


@app.post("/agent-chat", response_model=AgentResponse)
async def agent_chat(request: ChatRequest):
    """
    Agent endpoint: researches the web, synthesizes findings,
    saves a report to documents/, and returns a summary.
    The saved file is automatically available to the RAG pipeline.
    """
    try:
        result = agent.run(request.message)
        return AgentResponse(
            response=result["answer"],
            steps=result["steps"]
        )
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return AgentResponse(
            response=f"Agent error: {str(e)}",
            steps=[]
        )
from fastapi import FastAPI
from pydantic import BaseModel
import openai
from openai import OpenAI
import time

client = OpenAI()
import os

# 🛠 One-time Assistant creation (stores knowledge of JSLT functions)
JSLT_INSTRUCTIONS = """
You are an expert in JSLT transformations.
The input json is {"name":"some-data","dateOfBirth":"28-12-1990"}
Our JSLT has **custom functions** like:

1. **LookUp("collectionName", "inputKey", "outputKey")**
   - Queries MongoDB and returns the `outputKey` from `collectionName` based on `inputKey`.
   - Example: `LookUp("StateLookup", "city", "state")`
     - If `StateLookup = [{"city": "NYC", "state": "New York"}]`
     - Then `LookUp("StateLookup", "NYC", "state")` returns `"New York"`.

2. **SplitName("fullName")**
   - Splits a full name into `firstName` and `lastName`.
   - Example: `SplitName("John Doe")` → `{ "firstName": "John", "lastName": "Doe" }`.
3. ifEmptyMakeNull(value)   

Only return the **JSLT code** and nothing else.
"""
app = FastAPI()
assistant_id=os.environ.get("JSLT_ASSISTANT", "")
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

def generate_jslt_token_heavy(input_json):
    prompt = f"{input_json["message"]}\n\n"

    response = client.chat.completions.create(model="gpt-4-turbo",
    messages=[{"role": "system", "content": f"{JSLT_INSTRUCTIONS}"},
              {"role": "user", "content": prompt}])

    return response.choices[0].message.content

@app.post("/generate-jslt-token-heavy")
async def generate_jslt_api(input_json: dict):
    jslt_output = generate_jslt_token_heavy(input_json)
    return {"jslt": jslt_output}
class MessageModel(BaseModel):
    message: str

@app.post("/generate-jslt")
async def generate_jslt(messageModel: MessageModel):
    """Use OpenAI Assistants API to generate JSLT with memory."""
    thread_id=os.environ.get("JSLT_OPENAI_THREAD_ID","")
    if thread_id == "":    
        print("I am creating a new thread with id below")
        thread = openai.beta.threads.create()
        thread_id= thread.id
        print("Creating new Thread ID:", thread_id)

    # Send user message to the assistant
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=messageModel.message
    )
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    # ✅ Polling until the run is completed
    while True:
        run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        print(run_status)
        if run_status.status == "completed":
            print("✅ Assistant finished processing!")
            break
        
        time.sleep(1)  # Wait 1 second before checking again
    # Retrieve the assistant’s latest response
    response = openai.beta.threads.messages.list(thread_id=thread_id)
    print("=====",response)
    # Extract assistant's response (latest message with role 'assistant')
    assistant_message = next(
        (msg for msg in reversed(response.data) if msg.role == "assistant"), None
    )

    if assistant_message and assistant_message.content:
        jslt_response = assistant_message.content[0].text.value  # Extract JSLT output
        return {"response": jslt_response}
    
    return {"error": "No valid response from assistant"}

def start_assistant():
    global assistant_id
    assistant = openai.beta.assistants.create(
    name="JSLT Transformer",
    instructions=JSLT_INSTRUCTIONS,
    model="gpt-4-turbo"
    )
    print("Assistant ID:", assistant.id)
    assistant_id=assistant.id

if __name__ == "__main__":
    import uvicorn
    if assistant_id == "":
        start_assistant()
    else:
        print("Skipping Assistant Creation as you are using the default one",assistant_id)
    uvicorn.run(app, host="0.0.0.0", port=8000)





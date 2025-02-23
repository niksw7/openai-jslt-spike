from fastapi import FastAPI
from pydantic import BaseModel

import openai
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

Only return **valid JSLT transformation code** and nothing else.
"""
app = FastAPI()
assistant_id=os.environ.get("JSLT_ASSISTANT", "")
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# def generate_jslt(input_json):
#     prompt = f"Generate a JSLT transformation that extracts the first and last name from the following JSON:\n\n{input_json}\n\nOnly return the JSLT code."
    
#     response = openai.ChatCompletion.create(
#         model="gpt-4-turbo",
#         messages=[{"role": "system", "content": "You are an expert in JSLT transformations."},
#                   {"role": "user", "content": prompt}]
#     )
    
#     return response["choices"][0]["message"]["content"]

# @app.post("/generate-jslt/")
# async def generate_jslt_api(input_json: dict):
#     jslt_output = generate_jslt(input_json)
#     return {"jslt": jslt_output}
class MessageModel(BaseModel):
    message: str

@app.post("/generate-jslt")
async def generate_jslt(messageModel: MessageModel):
    """Use OpenAI Assistants API to generate JSLT with memory."""
    thread = openai.beta.threads.create()
    thread_id= thread.id
    print("Thread ID:", thread_id)

    
    # Send user message to the assistant
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=messageModel.message
    )
    print("assistant_id",assistant_id)
    # Run the assistant. Create a new thread every time
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # Retrieve the response (only assistant's answer)
    response = openai.beta.threads.messages.list(thread_id=thread_id)
    print(response)
    
    return {"response": response.data[-1].content}

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
    uvicorn.run(app, host="0.0.0.0", port=8000)





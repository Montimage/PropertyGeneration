from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path
from models import PromptRequest, PropertyMessage, ErrorMessage, QuestionMessage, SavePropertyRequest, SendToMonitoringRequest, ReceivedEventRequest, ReceivedEventResponse
from typing import Union
from fastapi.responses import JSONResponse
import requests
from fastapi import BackgroundTasks

# Add the 'src' directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from generator import generate_property_from_text
from save_property import save_property_to_db

RECEIVER_URL = "http://192.168.64.37:8000"

generated_messages = []

app = FastAPI()

# Allow frontend to access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate-property", response_model=Union[QuestionMessage, PropertyMessage, ErrorMessage])
async def generate_property(request: PromptRequest):
    scenario = request.input_text
    protocols = request.protocol_list

    result = generate_property_from_text(scenario, protocols)

    if result["success"]:
        if result["is_valid"]:
            print("Valid property sent")
            return PropertyMessage(
                type="property",
                status="valid",
                role="ai",
                content=result["xml"],
                editable=True,
                ask_to_save=True,
                origin="chat"
            )
        else:
            print("Invalid property sent")
            return PropertyMessage(
                type="property",
                status="invalid",
                role="ai",
                content=result["xml"],
                editable=True,
                ask_to_save=True,
                validation_feedback=result["validation_feedback"],
                origin="chat"
            )
    else:
        print("Error message sent")
        return ErrorMessage(
            type="error",
            role="ai",
            content=result["error"]
        )

@app.post("/save-property")
async def save_property(request: SavePropertyRequest):
    data = request.dict()
    print(f"Received data: {data}")
    success = save_property_to_db(
        description=data["description"],
        protocols=data["protocol"],
        name=data["name"],
        xml_content=data["content"]
    )
    if success:
        return JSONResponse(content={"message": "Property saved successfully."}, status_code=200)
    else:
        return JSONResponse(content={"error": "Failed to save property."}, status_code=500)

@app.post("/send-to-monitoring")
async def send_to_monitoring(request: SendToMonitoringRequest):
    data = request.dict()

    xml_content = data["content"]
    property_name = data.get("name", "rule.xml")
    if not property_name.endswith(".xml"):
        property_name += ".xml"

    receiver_url = f"{RECEIVER_URL}/rules"

    try:
        response = requests.post(
            receiver_url,
            data=xml_content.encode("utf-8"),
            headers={
                "Content-Type": "application/xml",
                "X-Rule-Filename": property_name
            },
            timeout=60
        )

        try:
            receiver_response = response.json()
        except Exception:
            receiver_response = response.text

        if response.ok:
            return JSONResponse(
                content={
                    "message": "Property sent to monitoring receiver.",
                    "receiver_status": response.status_code,
                    "receiver_response": receiver_response
                },
                status_code=response.status_code
            )
        else:
            return JSONResponse(
                content={
                    "error": "Failed to send property to monitoring receiver.",
                    "receiver_status": response.status_code,
                    "receiver_response": receiver_response
                },
                status_code=response.status_code
            )

    except requests.exceptions.RequestException as e:
        return JSONResponse(
            content={"error": f"Failed to send property to monitoring receiver: {str(e)}"},
            status_code=500
        )

def process_received_event(source: str, event: dict):
    global generated_messages

    try:
        info = event.get("info", "")
        attributes = event.get("Attribute", [])

        scenario = (
            f"Received event from {source} with the following details:\n"
            f"{info}\n"
            f"Attributes:\n{attributes}"
        )
        protocols = []

        result = generate_property_from_text(scenario, protocols)

        if result["success"]:
            if result["is_valid"]:
                message = {
                    "type": "property",
                    "status": "valid",
                    "role": "ai",
                    "content": result["xml"],
                    "editable": True,
                    "ask_to_save": True,
                    "origin": "remote_incident",
                    "incident_source": source
                }
            else:
                message = {
                    "type": "property",
                    "status": "invalid",
                    "role": "ai",
                    "content": result["xml"],
                    "editable": True,
                    "ask_to_save": True,
                    "validation_feedback": result.get("validation_feedback"),
                    "origin": "remote_incident",
                    "incident_source": source
                }
        else:
            message = {
                "type": "error",
                "role": "ai",
                "content": result["error"]
            }

        generated_messages.append(message)

        print("=== Generated message queued for frontend ===")
        print(message)
        print("===========================================")

    except Exception as e:
        print("=== Error while processing received event in background ===")
        print(str(e))
        print("==========================================================")

        generated_messages.append({
            "type": "error",
            "role": "ai",
            "content": f"Error while processing received event: {str(e)}"
        })

@app.post("/receive-event", response_model=ReceivedEventResponse)
async def receive_event(request: ReceivedEventRequest, background_tasks: BackgroundTasks):
    try:
        data = request.dict()

        if not isinstance(data, dict):
            return JSONResponse(
                content={"error": "Invalid request payload."},
                status_code=400
            )

        source = data.get("source")

        event_wrapper = data.get("event")
        if not isinstance(event_wrapper, dict):
            return JSONResponse(
                content={"error": "Missing or invalid 'event' field."},
                status_code=400
            )

        event = event_wrapper.get("Event")
        if not isinstance(event, dict):
            return JSONResponse(
                content={"error": "Missing or invalid 'event.Event' field."},
                status_code=400
            )

        background_tasks.add_task(process_received_event, source, event)

        return JSONResponse(
            content={
                "message": "Event received successfully.",
                "source": source,
                "received_keys": list(data.keys())
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to receive event: {str(e)}"},
            status_code=500
        )

@app.get("/pending-messages")
async def get_pending_messages():
    global generated_messages

    messages_to_return = generated_messages[:]
    generated_messages.clear()

    return {"messages": messages_to_return}
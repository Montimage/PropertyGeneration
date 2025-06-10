from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path
from models import PromptRequest, PropertyMessage, ErrorMessage, QuestionMessage, SavePropertyRequest
from typing import Union
from fastapi.responses import JSONResponse

# Add the 'src' directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from generator import generate_property_from_text
from save_property import save_property_to_db

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
                ask_to_save=True
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
                validation_feedback=result["validation_feedback"]
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
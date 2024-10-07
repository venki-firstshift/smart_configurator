#!/usr/bin/env python
from starlette.datastructures import UploadFile

from copilot.chat_bot import create_qa_chain
from fastapi import FastAPI
from langserve import CustomUserType, add_routes
from pydantic import Field
from langchain_core.runnables import RunnableLambda

class FileProcessingRequest(CustomUserType):
    """Request including a base64 encoded file."""

    # The extra field is used to specify a widget for the playground UI.
    file: str = Field(..., json_schema_extra={"widget": {"type": "base64file"}})


def _process_file(request: FileProcessingRequest) -> str:
    """Extract the text from the first page of the PDF."""
    content = request.file
    return content

chain = create_qa_chain()


# 4. App definition
app = FastAPI(
  title="LangChain Server",
  version="1.0",
  description="A simple API server using LangChain's Runnable interfaces",
)


# 5. Adding chain route
add_routes(
    app,
    chain,
    path="/config/entities",
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
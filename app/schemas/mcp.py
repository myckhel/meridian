from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MCPServerInfo(BaseModel):
    name: str
    version: str


class MCPInitializeResult(BaseModel):
    protocol_version: str = Field(alias="protocolVersion")
    capabilities: dict[str, Any] = Field(default_factory=dict)
    server_info: MCPServerInfo = Field(alias="serverInfo")

    model_config = ConfigDict(populate_by_name=True)


class MCPTool(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any] = Field(alias="inputSchema")
    output_schema: dict[str, Any] | None = Field(default=None, alias="outputSchema")

    model_config = ConfigDict(populate_by_name=True)


class MCPTextContent(BaseModel):
    type: str
    text: str | None = None


class MCPToolCallResult(BaseModel):
    content: list[MCPTextContent] = Field(default_factory=list)
    is_error: bool = Field(default=False, alias="isError")

    model_config = ConfigDict(populate_by_name=True)

    @property
    def primary_text(self) -> str:
        text_parts = [item.text for item in self.content if item.type == "text" and item.text]
        return "\n".join(text_parts).strip()
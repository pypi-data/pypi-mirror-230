# imports
from pydantic import BaseModel, Field
from netsky.models import ai_model


@ai_model
class Summary(BaseModel):
    """A summary of input text"""

    description: str = Field(description="The description of the text")
    summary: str = Field(description="The one to two paragraph summary of the text")
    key_points: list[str] = Field(description="The key points of the text, if any")
    sentiment: str = Field(description="The sentiment of the text")
    sentiment_score: float = Field(description="The sentiment score of the text")
    biases: list[str] = Field(
        description="The obvious biases of the text's author, if any"
    )

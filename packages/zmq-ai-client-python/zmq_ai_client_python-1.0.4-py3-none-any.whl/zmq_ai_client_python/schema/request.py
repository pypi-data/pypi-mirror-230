from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class Message:
    """
    Dataclass representing a message in the request.
    """
    role: str  # Role of the message sender (e.g., "user" or "system")
    content: str  # Content of the message
    name: Optional[str] = None  # Optional name of the sender
    function_call: Optional[dict] = None  # Optional function call associated with the message


@dataclass
class Function:
    """
    Dataclass representing a function that can be called in the request.
    """
    name: str  # Name of the function
    description: Optional[str] = None  # Optional description of the function
    parameters: Optional[dict] = None  # Optional parameters for the function
    function_call: Optional[str] = None  # Optional function call string


@dataclass
class ChatCompletionRequest:
    """
    Dataclass representing a request to the model.
    """
    model: str  # Name of the model to be used
    messages: List[Message]  # List of messages in the request
    functions: Optional[List[Function]] = None  # Optional list of functions in the request
    temperature: Optional[float] = 1.0  # Sampling temperature for the model's output
    top_p: Optional[float] = 1.0  # Nucleus sampling parameter
    n: Optional[int] = 1  # Number of completions to generate
    stream: Optional[bool] = False  # Whether to stream the output
    stop: Optional[List[str]] = None  # List of tokens to stop the generation
    max_tokens: Optional[int] = 256  # Maximum number of tokens in the output
    presence_penalty: Optional[float] = 0.0  # Penalty for new tokens in the output
    frequency_penalty: Optional[float] = 0.0  # Penalty for frequent tokens in the output
    logit_bias: Optional[dict] = None  # Bias for certain tokens in the output
    user: Optional[str] = None  # Optional user identifier for the request
    key_values: Optional[Dict[str, str]] = None # Optional key_values for advanced options

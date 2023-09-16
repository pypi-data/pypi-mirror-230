from dataclasses import dataclass, field
from typing import List, Optional, Dict, Literal
from zmq_ai_client_python.schema.request import Message


@dataclass
class ChatCompletionLogprobs:
    """
    Dataclass representing the log probabilities associated with a chat completion.
    """
    text_offset: List[int]  # Offsets for the text
    token_logprobs: List[Optional[float]]  # Log probabilities for each token
    tokens: List[str]  # Tokens in the completion
    top_logprobs: List[Optional[Dict[str, float]]]  # Top log probabilities for each token


@dataclass
class ChatCompletionChoice:
    """
    Dataclass representing a choice in a chat completion.
    """
    index: int  # Index of the choice
    message: Message  # Message associated with the choice
    logprobs: Optional[ChatCompletionLogprobs]  # Log probabilities for the choice
    finish_reason: Optional[str]  # Reason for finishing the choice (if any)


@dataclass
class ChatCompletionUsage:
    """
    Dataclass representing the usage statistics of a chat completion.
    """
    prompt_tokens: int  # Number of tokens in the prompt
    completion_tokens: int  # Number of tokens in the completion
    total_tokens: int  # Total number of tokens (prompt + completion)


@dataclass
class ChatCompletion:
    """
    Dataclass representing a chat completion.
    """
    id: str  # Unique identifier for the completion
    object: Literal["chat_completion"]  # Type of the object (always "chat_completion" for this class)
    created: int  # Timestamp of when the completion was created
    choices: List[ChatCompletionChoice]  # List of choices in the completion
    usage: ChatCompletionUsage  # Usage statistics for the completion
    key_values: dict[any:any] = field(default_factory=dict)  # Additional key-value pairs associated with the completion

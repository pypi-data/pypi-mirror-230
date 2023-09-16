import msgpack
import zmq

from dataclasses import asdict
from zmq_ai_client_python.schema.completion import ChatCompletion, ChatCompletionChoice, ChatCompletionUsage, ChatCompletionLogprobs
from zmq_ai_client_python.schema.request import ChatCompletionRequest, Message


class LlamaClient:
    """
    LlamaClient is a client class to communicate with a server using ZeroMQ and MessagePack.
    """

    def __init__(self, host: str):
        """
        Initializes the LlamaClient with the given host.

        :param host: The server host to connect to.
        """
        self.context = zmq.Context()  # Creating a new ZeroMQ context
        self.socket = self.context.socket(zmq.REQ)  # Creating a new request socket
        self.socket.connect(host)  # Connecting to the provided host

    def send_request(self, request: ChatCompletionRequest) -> ChatCompletion:
        """
        Sends a request to the server and receives a response.

        :param request: The request object to be sent.
        :return: The unpacked ChatCompletion response.
        """
        request_dict = asdict(request)  # Convert the request dataclass to a dictionary
        packed_request = msgpack.packb(request_dict)  # Pack the request dictionary using MessagePack
        self.socket.send(packed_request)  # Send the packed request to the server
        response = self.socket.recv()  # Receive the response from the server
        return self._unpack_response(response)  # Unpack and return the response

    @staticmethod
    def _unpack_logprobs(data: bytes):
        """
        Unpacks logprobs data from bytes.

        :param data: The packed logprobs data.
        :return: The unpacked ChatCompletionLogprobs object.
        """
        text_offset, token_logprobs, tokens, top_logprobs = data
        return ChatCompletionLogprobs(text_offset, token_logprobs, tokens, top_logprobs)

    @staticmethod
    def _unpack_message(data: bytes):
        """
        Unpacks message data from bytes.

        :param data: The packed message data.
        :return: The unpacked Message object.
        """
        role, content, name, function_call = data
        return Message(role, content, name, function_call)

    @staticmethod
    def _unpack_choice(data: bytes):
        """
        Unpacks choice data from bytes.

        :param data: The packed choice data.
        :return: The unpacked ChatCompletionChoice object.
        """
        index, message, logprobs, finish_reason = data
        message = LlamaClient._unpack_message(message)
        if logprobs is not None:
            logprobs = LlamaClient._unpack_logprobs(logprobs)
        return ChatCompletionChoice(index, message, logprobs, finish_reason)

    @staticmethod
    def _unpack_usage(data: bytes):
        """
        Unpacks usage data from bytes.

        :param data: The packed usage data.
        :return: The unpacked ChatCompletionUsage object.
        """
        prompt_tokens, completion_tokens, total_tokens = data
        return ChatCompletionUsage(prompt_tokens, completion_tokens, total_tokens)

    @staticmethod
    def _unpack_completion(data: bytes):
        """
        Unpacks completion data from bytes.

        :param data: The packed completion data.
        :return: The unpacked ChatCompletion object.
        """
        id, object, created, choices, usage, key_values = data
        choices = [LlamaClient._unpack_choice(choice) for choice in choices]
        usage = LlamaClient._unpack_usage(usage)
        return ChatCompletion(id, object, created, choices, usage)

    @staticmethod
    def _unpack_response(data: bytes):
        """
        Unpacks the response data from bytes.

        :param data: The packed response data.
        :return: The unpacked ChatCompletion object.
        """
        unpacked_data = msgpack.unpackb(data, raw=False)  # Unpack the data using MessagePack
        return LlamaClient._unpack_completion(unpacked_data)  # Return the unpacked ChatCompletion object

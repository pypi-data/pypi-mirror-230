"""Client to use for integration tests"""
import logging
from google.protobuf import service
import zmq
from edgepirpc.protos import rpc_pb2 as rpc_pb

_logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG
)

# pylint: disable=too-few-public-methods
class ClientRpcChannel(service.RpcChannel):
    """
    Client class that utilizes google's abstract RpcChannel interfce. 
    - The RpcChannel represents a comunication line to a service and can 
    be used to call that service's methods. 
    - This class handles connecting to the RPC server, as well as serializing/deserializing
    messages to and from the server when service methods are called from the client side.
    """

    def __init__(self, transport):
        self.transport = transport
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.transport)

    # pylint: disable=no-member
    def _get_rpc_request(self, method, client_request):
        # Wrap client's request msg in an RPC message
        rpc_request = rpc_pb.RpcRequest()
        # Set rpc request to client's request as byte string
        rpc_request.request_proto = client_request.SerializeToString()
        # Set rpc service and method name
        rpc_request.service_name = method.containing_service.name
        rpc_request.method_name = method.name
        _logger.debug("RPC request object: {%s}", rpc_request)
        return rpc_request

    def _send_rpc_request(self, rpc_request):
        try:
            # Serialize RPC protocol message
            # Send over socket
            rpc_request_data = rpc_request.SerializeToString()
            self.socket.send(rpc_request_data)
        # pylint: disable=broad-except, broad-exception-caught
        except Exception as exc:
            _logger.exception("Error serialzing/sending RPC request to server: %s", exc)

    #pylint: disable=no-member
    def _get_rpc_response(self):
        # Receive rpc response data from socket
        try:
            rpc_response_data = self.socket.recv()
            # Return the rpc response message
            rpc_response = rpc_pb.RpcResponse()
            rpc_response = rpc_response.FromString(rpc_response_data)
            _logger.debug("RPC response object: {%s}", rpc_response)
            return rpc_response
        # pylint: disable=broad-exception-caught
        except Exception as exc:
            _logger.exception("Error recieving/deserializing RPC response: {%s}", exc)
        return None

    # pylint: disable=too-many-arguments, unused-argument
    # TODO: Determine whether unused arguments 'response_class' and 'done' are needed
    def CallMethod(self, method_descriptor, _rpc_controller, request, response_class, done):
        _logger.debug('%s', request)
        # Create rpc request
        rpc_request = self._get_rpc_request(method_descriptor,request)
        # Send rpc service request over socket
        self._send_rpc_request(rpc_request)
        # Get the rpc response from socket
        rpc_response = self._get_rpc_response()
        # Return rpc response message
        return rpc_response

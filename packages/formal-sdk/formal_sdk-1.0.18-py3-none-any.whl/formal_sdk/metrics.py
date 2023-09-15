import grpc


from .gen.admin.v1.metrics_pb2 import (
	GetMetricsRequest,
	Metric,
	Node,
	Link,
	GetMetricsResponse,
)

from .gen.admin.v1.metrics_pb2_grpc import MetricsServiceStub
class MetricsService:
	def __init__(self, base_url, token):
		self.base_url = base_url
		self.channel = grpc.secure_channel(self.base_url, grpc.ssl_channel_credentials())
		self.stub = MetricsServiceStub(self.channel)
		self.headers = [('x-api-key', token)]

	def GetMetrics(self, request: GetMetricsRequest) -> GetMetricsResponse:
		return self.stub.GetMetrics(request, metadata=self.headers)


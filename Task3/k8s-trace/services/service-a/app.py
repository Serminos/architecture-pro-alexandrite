from flask import Flask, request, jsonify
import requests
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

app = Flask(__name__)

resource = Resource(attributes={SERVICE_NAME: "service-a"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(
    JaegerExporter(
        agent_host_name="simplest-agent",
        agent_port=6831,
    )
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route('/')
def hello():
    # Вызываем service-b
    try:
        resp = requests.get('http://service-b:8080/')
        return f"Hello from service-a! Response from service-b: {resp.text}"
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
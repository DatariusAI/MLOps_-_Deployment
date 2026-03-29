"""Simple model serving API - demonstrates MLOps deployment pattern."""
import pickle
import json
import numpy as np
from http.server import HTTPServer, BaseHTTPRequestHandler


class ModelHandler(BaseHTTPRequestHandler):
    model = None
    metadata = None

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "healthy",
                "model_loaded": self.model is not None
            }).encode())
        elif self.path == '/info':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(self.metadata or {}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/predict':
            content_length = int(self.headers['Content-Length'])
            body = json.loads(self.rfile.read(content_length))
            features = np.array(body['features']).reshape(1, -1)
            prediction = self.model.predict(features).tolist()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"prediction": prediction}).encode())


if __name__ == '__main__':
    with open('model.pkl', 'rb') as f:
        ModelHandler.model = pickle.load(f)
    print("Model server running on port 8080")
    HTTPServer(('', 8080), ModelHandler).serve_forever()

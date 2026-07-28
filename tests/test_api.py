import unittest
import subprocess
import time
import urllib.request
import urllib.parse
import json

class TestAPIServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.process = subprocess.Popen(
            ["uvicorn", "pyc64c.api_server:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.wait()

    def test_health_endpoint(self):
        req = urllib.request.Request("http://127.0.0.1:8000/health")
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode('utf-8'))
            self.assertEqual(data["status"], "ok")

    def test_metrics_endpoint(self):
        req = urllib.request.Request("http://127.0.0.1:8000/metrics")
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode('utf-8'))
            self.assertEqual(data["status"], "healthy")

    def test_compile_endpoint(self):
        payload = {
            "version": "1.0",
            "source_code": "def main():\n    print(\"api ok\")",
            "options": {"target": "c64"}
        }
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            "http://127.0.0.1:8000/compile",
            data=req_data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode('utf-8'))
            self.assertEqual(data["status"], "success")
            self.assertIn("prg_base64", data["artifacts"])

if __name__ == '__main__':
    unittest.main()

import threading

class TasmotaAdapter:
    def cmd(self, command):
        print(f"Executing Tasmota command: {command}")
        # Simulate different command responses
        if command == "status5":
            return {"Status": {"Topic": "dummy_topic"}}
        # Add more command simulations as needed
        return {}

    def set_timer(self, delay, callback, timer_name=None):
        def timer_callback():
            threading.Timer(delay / 1000, callback).start()

        timer_callback()

tasmota = TasmotaAdapter()

import subprocess


class BotControl:
    def __init__(self):
        self.process = None

    def start(self):
        if not self.process:
            self.process = subprocess.Popen(
                ["python", "run_commander.py"]
            )

            print("Bot started.")

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None

            print("Bot stopped.")

    def status(self):
        if self.process:
            print("Running")
        else:
            print("Stopped")
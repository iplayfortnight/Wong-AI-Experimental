import os
import sys
import time
import mmap
from pynput import keyboard

SHARED_MEM_SIZE = 128
MEM_NAME = "Local_AI_Sensors"
DAEMON_HEARTBEAT_FILE = "daemon_pulse.tmp"

class SensorDaemon:
    def __init__(self):
        self.keystroke_count = 0
        
        if os.name == 'nt':
            self.shmem = mmap.mmap(-1, SHARED_MEM_SIZE, tagname=MEM_NAME, access=mmap.ACCESS_WRITE)
        else:
            fd = os.open(f"/dev/shm/{MEM_NAME}", os.O_RDWR | os.O_CREAT)
            os.ftruncate(fd, SHARED_MEM_SIZE)
            self.shmem = mmap.mmap(fd, SHARED_MEM_SIZE, access=mmap.ACCESS_WRITE)

        self.listener = keyboard.Listener(on_press=self._on_press)
        self.listener.start()

    def _on_press(self, key):
        self.keystroke_count += 1

    def execution_loop(self):
        try:
            while True:
                time.sleep(1.0)
                
                with open(DAEMON_HEARTBEAT_FILE, "w") as f:
                    f.write(str(time.time()))

                telemetry = f"WPS:{float(self.keystroke_count):.1f}"
                telemetry_padded = telemetry.ljust(SHARED_MEM_SIZE, " ")
                
                self.shmem.seek(0)
                self.shmem.write(telemetry_padded.encode('utf-8'))
                self.keystroke_count = 0
        except KeyboardInterrupt:
            self.listener.stop()
            self.shmem.close()
            if os.path.exists(DAEMON_HEARTBEAT_FILE):
                os.remove(DAEMON_HEARTBEAT_FILE)
            sys.exit(0)

if __name__ == "__main__":
    daemon = SensorDaemon()
    daemon.execution_loop()

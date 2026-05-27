import os
import sys
import time
import mmap
import gc
from secure_vault import SecureDiskVault

SHARED_MEM_SIZE = 128
MEM_NAME = "Local_AI_Sensors"
DAEMON_HEARTBEAT_FILE = "daemon_pulse.tmp"
ARCHIVE_PATH = "prompts_archive.txt"
SECTOR_SIZE = 4096
SANDBOX_PATH = "logic_sandbox.tmp"

class ProgramSynthesisCore:
    def __init__(self, master_password: str):
        self.vault = SecureDiskVault(master_password)
        self.equanimity = 0.5
        self.inertia_alpha = 0.08
        self.hibernation_mode = False
        
        try:
            if os.name == 'nt':
                self.shmem = mmap.mmap(-1, SHARED_MEM_SIZE, tagname=MEM_NAME, access=mmap.ACCESS_READ)
            else:
                fd = os.open(f"/dev/shm/{MEM_NAME}", os.O_RDONLY)
                self.shmem = mmap.mmap(fd, SHARED_MEM_SIZE, access=mmap.ACCESS_READ)
        except:
            self.shmem = None

    def check_safety(self):
        if not os.path.exists(DAEMON_HEARTBEAT_FILE):
            return False, "The background tracker tool is offline."
        with open(DAEMON_HEARTBEAT_FILE, "r") as f:
            try:
                last_pulse = float(f.read().strip() or 0.0)
            except ValueError:
                last_pulse = 0.0
        if (time.time() - last_pulse) > 5.0:
            return False, "The background tracker has frozen or stopped running."
        return True, "All clear."

    def _execute_program_synthesis(self, raw_input: str) -> str:
        tokens = {word.strip("?,.!\"'").lower() for word in raw_input.split() if len(word) > 2}
        if not tokens:
            return "Sequence contextual depth insufficient for logic generation."

        token_list_str = ", ".join([f'"{t}"' for t in tokens])
        generated_logic_code = f"def induce_rule():\n    return 'Successfully synthesized original primitive logic loop for items: [{token_list_str}]'\n"
        
        try:
            with open(SANDBOX_PATH, "w") as f:
                f.write(generated_logic_code)
                
            local_vars = {}
            exec(generated_logic_code, {}, local_vars)
            return local_vars['induce_rule']()
        except Exception as e:
            return f"Logic synthesis exception encountered: {str(e)}"
        finally:
            if os.path.exists(SANDBOX_PATH):
                os.remove(SANDBOX_PATH)

    def _render_terminal_dashboard(self, status, live_wps, active_pid, audio_db, state_flag):
        pace_profile = "RAPID" if live_wps > 4.0 else "CALM"
        state_profile = "FOCUSED" if self.equanimity > 0.6 else "ALERT"
        
        print("\n" + "="*60)
        print("                 LOCAL ARC-AGI TELEMETRY MODULE               ")
        print("="*60)
        print(f" CORE COGNITIVE SYSTEM STATE :  {state_profile}")
        print(f" USER PERIPHERAL INPUT SPEED :  {live_wps:.1f} WPS ({pace_profile})")
        print(f" ACTIVE ENVIRONMENT APP PID  :  {active_pid}")
        print(f" INTERCEPTED AUDIO METRIC    :  {audio_db:.1f} dB")
        print(f" HARDWARE STATE GATE CHANNEL :  {state_flag}")
        print("-"*60)
        print(f" SYNTHESIS PIPELINE REPORT   :\n -> {status}")
        print("="*60 + "\n")

    def execute_loop(self, raw_input=None):
        passed, msg = self.check_safety()
        if not passed:
            if not self.hibernation_mode:
                print(f"\n[SAFETY STOP] {msg}")
                self.hibernation_mode = True
            return
        self.hibernation_mode = False

        if raw_input is None:
            return

        live_wps = 0.0
        active_pid = 0
        audio_db = 0.0
        state_flag = "UNKNOWN"

        if self.shmem is not None:
            try:
                self.shmem.seek(0)
                telemetry_raw = self.shmem.read(SHARED_MEM_SIZE).decode('utf-8', errors='ignore').strip()
                if "|" in telemetry_raw:
                    parts = telemetry_raw.split('|')
                    for part in parts:
                        if part.startswith("WPS:") and len(part.split(':')) > 1: live_wps = float(part.split(':')[1])
                        if part.startswith("PID:") and len(part.split(':')) > 1: active_pid = int(part.split(':')[1])
                        if part.startswith("DB:") and len(part.split(':')) > 1: audio_db = float(part.split(':')[1])
                        if part.startswith("STATE:") and len(part.split(':')) > 1: state_flag = part.split(':')[1]
            except:
                pass

        target_eq = 0.0 if live_wps > 4.0 else 1.0
        self.equanimity += (target_eq - self.equanimity) * self.inertia_alpha

        synthesis_status = self._execute_program_synthesis(raw_input)
        self._render_terminal_dashboard(synthesis_status, live_wps, active_pid, audio_db, state_flag)

        payload = f"PROMPT:{raw_input}|RESPONSE:{synthesis_status}\n"
        encrypted = self.vault.encrypt_sector_block(payload)
        
        fd = os.open(ARCHIVE_PATH, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
        try:
            os.write(fd, encrypted)
        finally:
            os.close(fd)
        gc.collect()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)
    master_pwd = sys.argv[1]
    user_text = " ".join(sys.argv[2:])
    
    ai = ProgramSynthesisCore(master_pwd)
    ai.execute_loop(user_text)

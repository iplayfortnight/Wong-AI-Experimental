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
SECTOR_SIZE = 4048

class CognitiveAICore:
    def __init__(self, master_password: str):
        self.vault = SecureDiskVault(master_password)
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

    def _synthesize_fluid_thought(self, current_prompt):
        if not os.path.exists(ARCHIVE_PATH):
            return "Hello there. I am your new local system node. My memory file is currently blank, but I am online, encrypted, and ready to learn from your daily workflows."
            
        file_size = os.path.getsize(ARCHIVE_PATH)
        total_sectors = file_size // SECTOR_SIZE
        
        prompt_keywords = {word.strip("?,.!\"'") for word in current_prompt.lower().split() if len(word) > 3}
        
        if not prompt_keywords:
            return "I am listening, but that input is too brief to draw any deep context. Tell me a bit more about what we are focusing on right now."

        discovered_fragments = []
        with open(ARCHIVE_PATH, "rb") as f:
            for i in range(total_sectors):
                f.seek(i * SECTOR_SIZE)
                decrypted = self.vault.decrypt_sector_block(f.read(SECTOR_SIZE))
                
                if not decrypted or "PROMPT:" not in decrypted:
                    continue
                    
                try:
                    first_split = decrypted.split("PROMPT:")
                    if len(first_split) > 1:
                        second_split = first_split[1].split("|")
                        clean_raw = second_split[0].strip()
                        block_words = {word.strip("?,.!\"'") for word in clean_raw.lower().split()}
                        
                        if prompt_keywords.intersection(block_words):
                            discovered_fragments.append(clean_raw)
                except:
                    pass
                        
                del decrypted

        if len(discovered_fragments) > 0:
            latest_match = discovered_fragments[-1]
            return f"I see a direct link here. Based on our history with '{latest_match}', we should continue expanding this exact logical framework. What is our next specific objective for this task?"
                
        return f"I understand you want to focus on '{current_prompt}'. This specific concept profile is new to my memory drive, so I have opened a secure, encrypted memory block to start tracking its parameters alongside you."

    def execute_loop(self, raw_input=None):
        passed, msg = self.check_safety()
        if not passed:
            print(f"\n[SAFETY STOP] {msg}\nGoing to sleep until the tracker restarts...")
            return

        if raw_input is None:
            return

        comprehensible_output = self._synthesize_fluid_thought(raw_input)
        print(f"\n[AGI ANSWER] -> {comprehensible_output}")

        payload = f"PROMPT:{raw_input}|ANSWER:{comprehensible_output}\n"
        encrypted = self.vault.encrypt_sector_block(payload)
        
        fd = os.open(ARCHIVE_PATH, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
        try:
            os.write(fd, encrypted)
        finally:
            os.close(fd)
        gc.collect()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    master_pwd = sys.argv[1]
    ai = CognitiveAICore(master_pwd)
    if len(sys.argv) > 2:
        ai.execute_loop(" ".join(sys.argv[2:]))

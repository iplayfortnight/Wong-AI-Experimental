import os
import sys
import time
import mmap
import gc
import math
import random
from secure_vault import SecureDiskVault

SHARED_MEM_SIZE = 128
MEM_NAME = "Local_AI_Sensors"
DAEMON_HEARTBEAT_FILE = "daemon_pulse.tmp"
ARCHIVE_PATH = "prompts_archive.txt"
SECTOR_SIZE = 4096

class LocalRecurrentBrain:
    def __init__(self, vocab_size, hidden_dim=64):
        self.vocab_size = vocab_size
        self.hidden_dim = hidden_dim
        
        random.seed(42)
        self.Wxh = [[random.uniform(-0.1, 0.1) for _ in range(hidden_dim)] for _ in range(vocab_size)]
        self.Whh = [[random.uniform(-0.1, 0.1) for _ in range(hidden_dim)] for _ in range(hidden_dim)]
        self.Why = [[random.uniform(-0.1, 0.1) for _ in range(vocab_size)] for _ in range(hidden_dim)]
        
        self.bh = [0.0] * hidden_dim
        self.by = [0.0] * vocab_size

    def forward(self, input_indices):
        h = [0.0] * self.hidden_dim
        
        for idx in input_indices:
            next_h = [0.0] * self.hidden_dim
            for j in range(self.hidden_dim):
                next_h[j] = self.Wxh[idx][j] + sum(h[k] * self.Whh[k][j] for k in range(self.hidden_dim)) + self.bh[j]
                next_h[j] = math.tanh(next_h[j])
            h = next_h
            
        y = [0.0] * self.vocab_size
        for j in range(self.vocab_size):
            y[j] = sum(h[k] * self.Why[k][j] for k in range(self.hidden_dim)) + self.by[j]
            
        max_y = max(y)
        exp_y = [math.exp(yi - max_y) for yi in y]
        sum_exp_y = sum(exp_y)
        probs = [ey / sum_exp_y for ey in exp_y]
        
        return probs

class CognitiveAICore:
    def __init__(self, master_password: str):
        self.vault = SecureDiskVault(master_password)
        self.equanimity = 0.5
        self.inertia_alpha = 0.08
        self.hibernation_mode = False
        self.current_wps = 0.0
        
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
            try: last_pulse = float(f.read().strip() or 0.0)
            except ValueError: last_pulse = 0.0
        if (time.time() - last_pulse) > 5.0:
            return False, "The background tracker has frozen or stopped running."
        return True, "All clear."

    def absorb_surroundings(self, sample_duration=5.0):
        steps = int(sample_duration / 0.5)
        accumulated_wps = 0.0
        for _ in range(steps):
            time.sleep(0.5)
            passed, _ = self.check_safety()
            if not passed or self.shmem is None: continue
            try:
                self.shmem.seek(0)
                raw = self.shmem.read(SHARED_MEM_SIZE).decode('utf-8', errors='ignore').strip()
                parts = raw.split('|')
                for part in parts:
                    if part.startswith("WPS:"): accumulated_wps += float(part.split(':')[1])
            except: pass
        self.current_wps = accumulated_wps / steps

    def _generate_neural_text(self, current_prompt):
        vocab = ["the", "project", "terminal", "runs", "a", "silent", "local", "digestive", "system", "my", "independent", "architecture", "needs", "secure", "storage", "layout", "hello", "user", "welcome", "to", "program", "software", "workspace"]
        word_to_idx = {word: i for i, word in enumerate(vocab)}
        
        prompt_words = [w.lower().strip("?,.!\"'") for w in current_prompt.split() if w.lower().strip("?,.!\"'") in word_to_idx]
        
        if not prompt_words:
            pace_desc = "rapid" if self.current_wps > 4.0 else "calm"
            return f"observing fresh inputs with {pace_desc} cadence"

        brain = LocalRecurrentBrain(vocab_size=len(vocab), hidden_dim=32)
        input_indices = [word_to_idx[w] for w in prompt_words]
        
        generated_sentence = list(prompt_words)
        
        for _ in range(8):
            probs = brain.forward(input_indices)
            
            next_idx = probs.index(max(probs))
            if next_idx == input_indices[-1] and len(probs) > 1:
                sorted_probs = sorted(range(len(probs)), key=lambda k: probs[k])
                next_idx = sorted_probs[-2]
                
            next_word = vocab[next_idx]
            generated_sentence.append(next_word)
            input_indices.append(next_idx)
            
        return " ".join(generated_sentence)

    def execute_loop(self, raw_input=None):
        passed, msg = self.check_safety()
        if not passed: return

        if raw_input is None: return

        neural_output = self._generate_neural_text(raw_input)
        print(f"[AGI BRAIN OUTPUT] -> {neural_output}")

        payload = f"PROMPT:{raw_input}|ANSWER:{neural_output}\n"
        encrypted = self.vault.encrypt_sector_block(payload)
        
        fd = os.open(ARCHIVE_PATH, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
        try: os.write(fd, encrypted)
        finally: os.close(fd)
        gc.collect()

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    master_pwd = sys.argv[1]
    ai = CognitiveAICore(master_pwd)
    ai.absorb_surroundings(sample_duration=5.0)
    if len(sys.argv) > 2:
        ai.execute_loop(" ".join(sys.argv[2:]))

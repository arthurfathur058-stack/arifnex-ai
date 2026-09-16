import time
COOLDOWN_TIME = 60

class KeyManager:
    def __init__(self, keys):
        self.keys = keys
    def get_best_key(self):
        now = time.time()
        available = []
        for i, k in enumerate(self.keys):
            if k["cooldown"] > now: continue
            score = k["priority"] * 1000 + (k["uses"] % 100)
            available.append((score, i))
        if not available:
            soonest = min(self.keys, key=lambda x: x["cooldown"])
            wait = max(0, soonest["cooldown"] - now)
            time.sleep(min(wait, 5))
            return self.get_best_key()
        available.sort(key=lambda x: x[0])
        return available[0][1]
    def mark_success(self, i): self.keys[i]["uses"] += 1
    def mark_rate_limited(self, i):
        self.keys[i]["cooldown"] = time.time() + COOLDOWN_TIME
        self.keys[i]["errors"] += 1
    def mark_error(self, i):
        self.keys[i]["errors"] += 1
        if self.keys[i]["errors"] > 5:
            self.keys[i]["cooldown"] = time.time() + 300
    def stats(self):
        return [{"provider": k["provider"], "uses": k["uses"],
                 "errors": k["errors"],
                 "cooldown": max(0, int(k["cooldown"] - time.time()))} for k in self.keys]

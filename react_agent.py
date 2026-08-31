class ReActAgent:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    def run_loop(self, task_func):
        retries = 0
        last_error = None

        while retries < self.max_retries:
            try:
                result = task_func()
                return {"status": "success", "result": result, "retries": retries}
            except Exception as e:
                retries += 1
                last_error = str(e)
                print(f"[ReAct Warning] Attempt {retries} failed: {last_error}. Retrying...")

        return {
            "status": "failed",
            "retries": retries,
            "error": f"Max retries ({self.max_retries}) exceeded. Loop forcefully terminated to protect tokens.",
            "last_error": last_error
        }

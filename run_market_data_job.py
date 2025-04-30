import time
import requests

API_BASE = "https://automation-api.clevercertificates.com"

def get_next_template_id():
    try:
        response = requests.get(f"{API_BASE}/get-next-template-to-process")
        response.raise_for_status()
        data = response.json()
        return data.get("template_id")
    except Exception as e:
        print(f"[ERROR] Failed to fetch next template ID: {e}")
        return None

def process_template(template_id):
    try:
        response = requests.post(f"{API_BASE}/generate-market-data/{template_id}")
        response.raise_for_status()
        print(f"[SUCCESS] Processed template ID {template_id}")
    except Exception as e:
        print(f"[ERROR] Failed to process template ID {template_id}: {e}")

def main():
    max_templates = 10  # Set a limit if you want
    count = 0

    while count < max_templates:
        template_id = get_next_template_id()
        if not template_id:
            print("No templates left to process.")
            break

        process_template(template_id)
        count += 1

        if count < max_templates:
            print("Waiting 60 seconds before next run...")
            time.sleep(60)

if __name__ == "__main__":
    main()

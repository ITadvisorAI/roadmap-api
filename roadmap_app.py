import os
import json
import logging
import threading
from flask import Flask, request, jsonify
from process_roadmap import process_roadmap  # You will create this script next

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = "temp_sessions"
os.makedirs(BASE_DIR, exist_ok=True)

@app.route("/", methods=["GET"])
def health():
    return "✅ Roadmap GPT is live", 200

@app.route("/start_roadmap", methods=["POST"])
def start_roadmap():
    try:
        data = request.get_json(force=True)
        session_id = data.get("session_id")
        email = data.get("email")
        files = data.get("files", [])
        gpt_module = data.get("gpt_module", "")
        status = data.get("status", "")

        logging.info("📥 Incoming Roadmap GPT request:\n%s", json.dumps(data, indent=2))

        if not all([session_id, email, files]):
            logging.error("❌ Missing required fields in payload")
            return jsonify({"error": "Missing required fields"}), 400

        # Ensure session folder exists
        folder_name = session_id if session_id.startswith("Temp_") else f"Temp_{session_id}"
        folder_path = os.path.join(BASE_DIR, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Start background processing
        def runner():
            try:
                process_roadmap(session_id, email, files, folder_path)
            except Exception as e:
                logging.exception("🔥 Error in Roadmap processing thread")

        threading.Thread(target=runner, daemon=True).start()
        logging.info(f"🚀 Roadmap GPT started for session: {session_id}")

        return jsonify({"message": "Roadmap generation started"}), 200

    except Exception as e:
        logging.exception("🔥 Failed to process roadmap request")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 14000))
    logging.info(f"🌐 Roadmap API launching on port {port}")
    app.run(host="0.0.0.0", port=port)

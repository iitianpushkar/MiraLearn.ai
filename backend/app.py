from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import os
import json

from dotenv import load_dotenv
from mira_sdk import MiraClient, Flow

load_dotenv()
client = MiraClient(config={"API_KEY": os.getenv("MIRA_API_KEY")})

app = Flask(__name__)
CORS(app)

@app.route('/transcript', methods=['POST'])
def get_transcript():
    data = request.json
    video_url = data.get('url')
    
    # Extract the video ID
    try:
        video_id = video_url.split('v=')[1].split('&')[0]
    except IndexError:
        return jsonify({"error": "Invalid YouTube URL"}), 400
    
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Format the transcript with timeline and text
        formatted_transcript = [
            f"[{item['start']:.2f}s] {item['text']}" for item in transcript
        ]
        transcript_text = "\n".join(formatted_transcript)
        
        # Return the transcript text directly without saving to a file
        return jsonify({"transcript": transcript_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/query', methods=['POST'])
def get_query():
    data = request.json
    query = data.get('query')
    transcript_text = data.get('context')  # Receive transcript from the previous endpoint

    if not transcript_text:
        return jsonify({"error": "No transcript provided"}), 400

    print(f"Received query: {query}")
    
    # Prepare input for the flow system
    input_dict = {
        "context": transcript_text, # Pass the transcript as context for query
        "question": query
    }

    flow = Flow(source="flow.yaml")
    
    # Run the flow with the provided query and transcript context
    result = client.flow.test(flow, input_dict)
    print(result)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)

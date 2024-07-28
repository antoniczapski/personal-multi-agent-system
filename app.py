from flask import Flask, request, jsonify
import requests
import os
import agent
import logging

app = Flask(__name__)
SLACK_TOKEN = os.getenv("SLACK_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO)

# A set to keep track of processed event_ids to ensure idempotency
processed_events = set()

@app.route('/slack/events', methods=['POST'])
def slack_events():
    json_data = request.json
    logging.info(f"Received event: {json_data}")
    
    if 'challenge' in json_data:
        return jsonify({'challenge': json_data['challenge']})
    
    if 'event' in json_data:
        event = json_data['event']
        event_id = json_data.get('event_id')
        
        # Check if this event_id has been processed
        if event_id in processed_events:
            logging.info(f"Duplicate event_id {event_id} detected, ignoring.")
            return jsonify({'status': 'duplicate event'}), 200
        
        # Add the event_id to the set of processed events
        processed_events.add(event_id)
        
        if event.get('type') == 'message' and not event.get('bot_id'):
            user_message = event['text']
            channel_id = event['channel']

            # Respond with a new message
            response_message = agent.qa(user_message)  # Get the response from the QA function
            response_url = 'https://slack.com/api/chat.postMessage'
            headers = {'Authorization': 'Bearer ' + SLACK_TOKEN}
            data = {
                'channel': channel_id,
                'text': response_message
            }
            response = requests.post(url=response_url, headers=headers, data=data)
            logging.info(f"Sent response: {response_message}")
    
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)

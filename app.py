from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

SLACK_TOKEN = 'xoxb-7148644545494-7433135074481-HpLXAnRnOAOu3SnGHOYv2hZH'

@app.route('/slack/events', methods=['POST'])
def slack_events():
    json_data = request.json
    if 'challenge' in json_data:
        return jsonify({'challenge': json_data['challenge']})
    
    if 'event' in json_data:
        event = json_data['event']
        if event.get('type') == 'message' and not event.get('bot_id'):
            user_message = event['text']
            channel_id = event['channel']
            thread_ts = event.get('thread_ts') or event['ts']

            # Respond in a thread
            response_message = user_message  # Echo the user's message
            response_url = 'https://slack.com/api/chat.postMessage'
            headers = {'Authorization': 'Bearer ' + SLACK_TOKEN}
            data = {
                'channel': channel_id,
                'text': response_message,
                'thread_ts': thread_ts  # this will make it a threaded message
            }
            response = requests.post(url=response_url, headers=headers, data=data)
            
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=3000, debug=True)

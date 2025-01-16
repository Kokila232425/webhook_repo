from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import uuid

app = Flask(__name__)

MONGO_URI = "mongodb+srv://koki887021:kokila23242526@webhook.op2jv.mongodb.net/?retryWrites=true&w=majority&appName=webhook"  
client = MongoClient(MONGO_URI)
db = client['webhook_database'] 
collection = db['webhooks_details'] 


@app.route('/webhook', methods=['POST'])
def webhook():
  
    if request.method == 'POST':
        data = request.json 

        action = data.get('action')
        sender = data.get('sender', {}).get('login', 'unknown')  
        timestamp = datetime.utcnow()
        request_id = str(uuid.uuid4()) 

     
        payload = {
            "request_id": request_id,
            "author": sender,
            "action": action,
            "timestamp": timestamp,
            "from_branch": None,
            "to_branch": None
        }

      
        if action == 'push':
          
            payload['from_branch'] = None
            payload['to_branch'] = data['ref'].split('/')[-1]
        elif action == 'pull_request':
           
            pr = data.get('pull_request', {})
            payload['from_branch'] = pr.get('head', {}).get('ref', None)
            payload['to_branch'] = pr.get('base', {}).get('ref', None)
        elif action == 'merge':
            payload['from_branch'] = data.get('merge_branch', {}).get('from', None)
            payload['to_branch'] = data.get('merge_branch', {}).get('to', None)
        else:
            return jsonify({"message": f"Action {action} not supported"}), 400

    
        result = collection.insert_one(payload)

    
        response_data = payload
        response_data['id'] = str(result.inserted_id) 

        return jsonify({"message": "Webhook received and data stored successfully", "data": response_data}), 200
    else:
        return jsonify({"message": "Invalid request method"}), 405

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

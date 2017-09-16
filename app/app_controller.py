from flask import jsonify, request
from flask_socketio import emit


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_post():
    page_url = request.json['pageUrl']

    return jsonify({
        'pageUrl': page_url,
        'results': {
            'positive': {'text': "positive comments", 'count': 12},
            'neutral': {'text': "neutral comments", 'count': 4},
            'negative': {'text': "negative comments", 'count': 20}
        }
    }), 202


#@socketio.on('processing_status')
def route_message(message):
    emit(message['page'], message['data'], broadcast=True)

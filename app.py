from flask import Flask

import sys
sys.path.append('./recommendation')

from recommendation import Recommendation

app = Flask(__name__)
recommendation = Recommendation('./recommendation/data')

@app.route('/r/<int:client_id>')
def client_recommendation(client_id):
	return {"hashtags": recommendation.predict(client_id)}

if __name__ == '__main__':
	app.run(debug=True)

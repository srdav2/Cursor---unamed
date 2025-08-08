from flask import Flask

app = Flask(__name__)

@app.route('/api/status')
def status():
    return {"status": "Backend is running!"}

if __name__ == '__main__':
    # Runs the server on port 5000
    app.run(debug=True, port=5000)

from flask import Flask, request, render_template
import Engine as eg

generator = eg.Engine()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', 'XUSLD')
    if query:
        generator.create_page(query)
        return render_template('output/output.html')

if __name__ == '__main__':
    app.run(debug=True)
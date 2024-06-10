from flask import Flask, render_template, request
import bibtexmagic as btm
app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/BibTexConverter', methods=['POST'])
def modify():
    if request.method == 'POST':
        input_string = request.form['input_string']
        # modified_string = input_string.upper()  # Hier wird der eingegebene String in Großbuchstaben umgewandelt
        modified_string = btm.create_bibtex(input_string)
        return render_template('result.html', input_string=input_string, modified_string=modified_string)


if __name__ == '__main__':
    app.run(debug=True)

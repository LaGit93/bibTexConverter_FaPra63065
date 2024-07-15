from flask import Flask, render_template, request
import BibTexMagic as BTM
import ocr_clipboard as occ


app = Flask(__name__)

# Initialisieren der Startseite
@app.route('/')
def index():
    language_list = occ.language_names()
    return render_template("result.html", language_list=language_list)


# Ausführen des BibTex-Parsers
@app.route('/BibTexConverter', methods=['POST'])
def modify():
    if request.method == 'POST':
        input_string = request.form['input_string']
        #modified_string = BTM.create_bibtex(input_string)
        modified_string = BTM.create_bibtex_loop(input_string)
        language_list = occ.language_names()

        return render_template('result.html', input_string=input_string, modified_string=modified_string, language_list=language_list)

# Ausführen der OCR-Erkennung
@app.route('/ocr', methods=['POST'])
def testocr():
    if request.method == 'POST':
        fieldselect_language = request.form.get('language_list_select')
        input_string = occ.newocr(fieldselect_language)
        modified_string = ""
        language_list = occ.language_names()
        selected_language = fieldselect_language  # Speichere den ausgewählten Wert
        return render_template('result.html', input_string=input_string, modified_string=modified_string, language_list=language_list, selected_language=selected_language)


if __name__ == '__main__':
    app.run(debug=True)

from utils import UPLOAD_FOLDER,MAX_CONTENT_LENGTH,INDEX_NAME, index_file, filename_by_datetime, create_whoosh_index,search_document
import os, whoosh.index as index
from datetime import datetime
from werkzeug.utils import secure_filename
import aspose.words as aw
from flask import Flask, request, render_template, send_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

@app.route('/', methods=['GET','POST'])
def show_upload_page():
    '''
        Apresenta a pagina inicial de upload de uma ata
    '''

    if request.method == 'GET':    
        return render_template('file_upload.html.j2')
    
    if request.method == 'POST':
        files = request.files.getlist("file")
        ret_msg = [""]
        upload_date = datetime.utcnow()
        file_count = 0

        for file in files:
            file_count += 1
            filename = filename_by_datetime(upload_date,file_count)
            if ".docx" in file.filename.lower() or ".doc" in file.filename.lower() or ".odt" in file.filename.lower():
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # Carregando o documento .docx
                doc = aw.Document(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # Salvando como PDF
                doc.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # Indexação
                index_file(os.path.join(app.config['UPLOAD_FOLDER'], filename),upload_date)
            elif ".pdf" in file.filename.lower():
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # Indexação
                index_file(os.path.join(app.config['UPLOAD_FOLDER'], filename),upload_date)
            else:
                ret_msg.append("<h1>Formato n&atilde;o suportado! Arquivo %s n&atilde;o armazenado.</h1>"%(file.filename))
    
    ix = index.open_dir(INDEX_NAME)            
    all_docs = ix.searcher().documents()
    for doc in all_docs:
        print(doc["file_path"])
    ix.close()
    return render_template('file_upload.html.j2')

@app.route('/start_project', methods=['GET'])
def create_bd():
    response = create_whoosh_index()
    return response

@app.route('/search/', methods=['GET', 'POST'])
def search():
    ix = index.open_dir("whoosh_index")
    with ix.searcher() as s:
        if request.method == 'POST':
            filter = request.form.get('filter')
            query = request.form.get('query')
            results = search_document(query,filter,s,ix.schema)
            return render_template('file_search.html.j2', results =results, resultsLength=len(results))
        if request.method == 'GET':
            return render_template('file_search.html.j2', results =[], resultsLength=0)


@app.route('/download/', methods=['GET'])
def download():
    file_name = request.args.get('file_name')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    return send_file(file_path)

if __name__ == '__main__':
    app.run(debug = True)
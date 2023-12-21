import os, PyPDF2, whoosh.index as index
from whoosh.fields  import Schema, TEXT, ID
from whoosh.analysis.analyzers import StandardAnalyzer
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from whoosh import fields

'''
   Variaveis Globais
'''
UPLOAD_FOLDER = os.path.join(os.getcwd(),"uploadFile")
MAX_CONTENT_LENGTH = 16 * 1000 * 1000
INDEX_NAME = "whoosh_index"
STOPWORDS = ["de", "a", "o", "que", "e", "do", "da", "em", "um", "para", "é", "com", "não", "uma", "os", "no", "se", "na", "por", "mais", "as", "dos", "como", "mas", "foi", "ao", "ele", "das", "tem", "à", "seu", "sua", "ou", "ser", "quando", "muito", "há", "nos", "já", "está", "eu", "também", "só", "pelo", "pela", "até", "isso", "ela", "entre", "era", "depois", "sem", "mesmo", "aos", "ter", "seus", "quem", "nas", "me", "esse", "eles", "estão", "você", "tinha", "foram", "essa", "num", "nem", "suas", "meu", "às", "minha", "têm", "numa", "pelos", "elas", "havia", "seja", "qual", "será", "nós", "tenho", "lhe", "deles", "essas", "esses", "pelas", "este", "fosse", "dele", "tu", "e", "vocês", "vos", "lhes", "meus", "minhas", "eu", "tua", "teus", "tuas", "nosso", "nossa", "nossos", "nossas", "dela", "delas", "esta", "estes", "estas", "aquele", "aquela", "aqueles", "aquelas", "isto", "aquilo", "estou", "está", "estamos", "estão", "estive", "esteve", "estivemos", "estiveram", "estava", "estávamos", "estavam", "estivera", "estivéramos", "esteja", "estejamos", "estejam", "estivesse", "estivéssemos", "estivessem", "estiver", "estivermos", "estiverem", "hei", "há", "havemos", "hão", "houve", "houvemos", "houveram", "houvera", "houvéramos", "haja", "hajamos", "hajam", "houvesse", "houvéssemos", "houvessem", "houver", "houvermos", "houverem", "houverei", "houverá", "houveremos", "houverão", "houveria", "houveríamos", "houveriam", "sou", "somos", "são", "era", "éramos", "eram", "fui", "foi", "fomos", "foram", "fora", "fôramos", "seja", "sejamos", "sejam", "fosse", "fôssemos", "fossem", "for", "formos", "forem", "serei",  "será", "seremos", "serão", "seria", "seríamos", "seriam", "tenho", "tem", "temos", "tém", "tinha", "tínhamos", "tinham", "tive", "teve", "tivemos", "tiveram", "tivera", "tivéramos", "tenha", "tenhamos", "tenham", "tivesse", "tivéssemos", "tivessem", "tiver", "tivermos", "tiverem", "terei", "terá", "teremos", "terão", "teria", "teríamos", "teriam"]
WHOOSH_SCHEMA = Schema(title=TEXT(stored=True), content=TEXT(analyzer=StandardAnalyzer(stoplist=STOPWORDS), stored=True), file_path=ID(stored=True), upload_date=fields.DATETIME(stored=True,sortable=True))

'''
   Funcoes Utilitarias
'''
def filename_by_datetime(upload_date,file_id):
    return "[" + str(file_id) + "]" + str(upload_date.strftime("%Y-%m-%d-%H-%M-%S")) + ".pdf"

def readpdf(file_path):
    pdfObj = open(file_path,'rb')
    read_pdf = PyPDF2.PdfFileReader(pdfObj, strict = False)
    page_content = ""
    documentTitle = read_pdf.getDocumentInfo().title
    for i in range(read_pdf.getNumPages()):    
        page = read_pdf.getPage(i)
        page_content += page.extractText()
    return {"title": documentTitle, "content":page_content}

'''
    FUNCOES QUE MANIPULAM O WHOOSH
'''             

def create_whoosh_index():
    try:
        if os.path.exists(INDEX_NAME):
            return "Não é possível criar o índice, pois o banco já existe."
        else:
            os.mkdir(INDEX_NAME)
        ix = create_in(INDEX_NAME, WHOOSH_SCHEMA)
        ix.close()
        return "Banco criado com sucesso"
    except:
        return "Erro interno."

def index_file(uploaded_file_path,file_upload_date):
    pdf_content = readpdf(uploaded_file_path)
    ix = index.open_dir(INDEX_NAME)
    writer = ix.writer()
    writer.add_document(title = pdf_content['title'], content=pdf_content['content'], file_path= uploaded_file_path, upload_date=file_upload_date)
    writer.commit()
    ix.close()

def search_document(content,filter,s,s_schema):
    qp = QueryParser(filter, schema= s_schema)       
    query = qp.parse(u"%s" %(content))
    results = s.search(query)
    return results
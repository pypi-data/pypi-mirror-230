from PyPDF2 import PdfFileReader
from IPython.display import Image

pdf_document = "/Users/dashka-z/Downloads/econstats/econknow/tasks.pdf"
with open(pdf_document, "rb") as filehandle:  
    pdf = PdfFileReader(filehandle)
   
    info = pdf.getDocumentInfo()
    pages = pdf.getNumPages()
    # print("Количество страниц в документе: %i\n\n" % pages)
    # print("Мета-описание: ", info)
    page = pdf.getPage(0)

    fig = Image(filename=(page))
    fig
import requests

from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd='C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
import sys
from pdf2image import convert_from_path
import os
import shutil
import re
from flask import Flask,render_template,request


app = Flask(__name__)

APP_ROOT = os.path.dirname(sys.argv[0])

@app.route('/')
def hello_world():
    return  render_template('index.html')


@app.route('/scrape',methods=['POST'])
def scrape():
    target = os.path.join(APP_ROOT, "images\\")
    IMG_ID=request.form.get("ImageId")
    
    token={'BP':['BP','Blood Pressure'],'Sugar':['Sugar','Random Sugar'],'TSH':['TSH','thyroid stimulating hormone','thyroid'],
           'T4':['T4','Thyroxine'],'D-Dimer':['D-Dimer'],'CRP':['CRP','c reactive protein'],'HB':['HB','Hemoglobin'],
           'HbA1c':['HbA1c'],'TLC':['TLC','Total leucocyte count','leucocyte count Total','leucocyte','Total Leukocyte Count','Leukocyte','Leukocyte Count Total'],
           'Cholesterol':['Total Cholesterol','Cholesterol','Cholesterol Total'],'HDL':['HDL','high density lipoprotein'],
           'LDL':['LDL','low density lipoprotein'],'SPO2':['SPO2','Oxygen'],'Heart Rate':['Heart Rate','Heart Beat','Pulse Rate'],
           'Respiratory Rate':['Respiratory Rate','RR'],'Fasting Sugar':['Fasting Sugar','FBS'],'PP Sugar':['PP Sugar','PPBS'],
           'Temperature':['Temperature']}
    
    
    
    if IMG_ID:
        #path = os.path.join('{}'.format(IMG_ID))
        os.mkdir(target)
        url = 'https://doctorconsole.healthok.in/viewImage/{}'.format(IMG_ID)

        response = requests.get(url)

        with open(target+'IMG_ID_{}.pdf'.format(IMG_ID), 'wb') as f:
            f.write(response.content)

        f.close() 

        PDF_file = target+'IMG_ID_{}.pdf'.format(IMG_ID)

        pages = convert_from_path(PDF_file, 500,poppler_path='C:\\Program Files\\poppler-0.68.0\\bin')

        image_counter = 1


        for page in pages:

            filename = target+'IMG_ID_{}page_'.format(IMG_ID)+str(image_counter)+".jpg"
            page.save(filename, 'JPEG')
            image_counter = image_counter + 1


        filelimit = image_counter-1

        outfile = target+"out_text.txt"

        f = open(outfile, "a")

        for i in range(1, filelimit + 1):
            filename = target+"IMG_ID_{}page_".format(IMG_ID)+str(i)+".jpg"
            text = str(((pytesseract.image_to_string(Image.open(filename))))).lower()
            f.write(text)

        f.close()
       
    else :
        
        uploaded_file=request.files.getlist("image/PDF")

        if not os.path.isdir(target):
            os.mkdir(target)
        
        if uploaded_file[0].filename.endswith('.pdf'):
            
            for file in uploaded_file:
                filename_img = file.filename
                destination = "/".join([target, filename_img])
                file.save(destination)
                ext = os.path.splitext(filename_img)[1]
                os.rename(target + filename_img, target+'pdf{}'.format(ext))
            
            PDF_file =target+'pdf.pdf'

            pages = convert_from_path(PDF_file, 500,poppler_path='C:\\Program Files\\poppler-0.68.0\\bin')

            image_counter = 1


            for page in pages:

                filename = target+'image_'+str(image_counter)+".jpg"
                page.save(filename, 'JPEG')
                image_counter = image_counter + 1


            filelimit = image_counter-1

            outfile = target+'out_text.txt'

            f = open(outfile, "a")

            for i in range(1, filelimit + 1):
                filename = target+'image_'+str(i)+".jpg"
                text = str(((pytesseract.image_to_string(Image.open(filename))))).lower()
                f.write(text)

            f.close()
        
        else:
            i=1
            filenames=[]
            for file in uploaded_file:

                filename_img = file.filename
                destination = "/".join([target, filename_img])
                file.save(destination)
                ext = os.path.splitext(filename_img)[1]
                os.rename(target + filename_img, target+'image_{}{}'.format(i,ext))
                filenames.append(str('image_{}{}'.format(i,ext)))
                i+=1

            outfile = target+"out_text.txt"

            f = open(outfile, "a")

            for filename in filenames:
                filename = target+filename
                text = str(((pytesseract.image_to_string(Image.open(filename))))).lower()
                f.write(text)


            f.close()
    
    

    result={}
    p = re.compile('\d+(\.\d+)?')
    with open(target+"out_text.txt",'r') as f:

        lines =f.readlines()
        
        for line in lines:
            line=line.replace(',','')
            line=line.replace('-','')
            line=line.replace(';','')
            line=line.replace('(','')
            line=line.replace(')','')
            line=line.replace('%','')
            line=line.replace('[','')
            line=line.replace(']','')
            
            for tkns in token.keys():
                for tkn in token[tkns]:
                        
                    if tkn.lower() in  line:
                        
                        words=[]
                        for word in line.split():
                            words.append(word)


                        
                        for word in words:
                            if p.match(word) :
                                
                                if tkns not in result.keys() and line.find(tkn.lower()) < line.find(word):
                                    
                                    result[tkns]=word
                            
                  

                            
    f.close()
    shutil.rmtree(target)
   
      
    return render_template("index.html", output=result)


if __name__=="__main__":
    app.run(debug=True,use_reloader=False)  

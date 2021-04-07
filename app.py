import requests

from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd='Tesseract-OCR\\tesseract.exe'
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
           'HbA1c':['HbA1c'],'TLC':['TLC','Total leucocyte count','leucocyte count Total','Total Leukocyte Count','Leukocyte Count Total'],
           'Cholesterol':['Total Cholesterol','Cholesterol','Cholesterol Total'],'HDL':['HDL','high density lipoprotein'],
           'LDL':['LDL','low density lipoprotein'],'SPO2':['SPO2','Oxygen'],'Heart Rate':['Heart Rate','Heart Beat','Pulse Rate'],
           'Respiratory Rate':['Respiratory Rate'],'Fasting Sugar':['Fasting Sugar','FBS'],'PP Sugar':['PP Sugar','PPBS'],
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

        pages = convert_from_path(PDF_file, 500)

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

       
        text=[]
        for filename in uploaded_file:
            
            text.append(str(((pytesseract.image_to_string(Image.open(filename))))).lower())
           
   

    result={}
    p = re.compile('\d+(\.\d+)?')
    #with open(target+"out_text.txt",'r') as f:
    for lines in text:
        #lines =f.readlines()
        
        #for line in lines:
        lines=lines.replace(',','')
        lines=lines.replace('-','')
        lines=lines.replace(';','')
        lines=lines.replace('(','')
        lines=lines.replace(')','')
        lines=lines.replace('%','')
        lines=lines.replace('[','')
        lines=lines.replace(']','')
        print(lines)
        for tkns in token.keys():
            for tkn in token[tkns]:

                if tkn.lower() in  lines:

                    words=[]
                    for word in lines.split():
                        words.append(word)



                    for word in words:
                        if p.match(word) :

                            if tkns not in result.keys() and lines.find(tkn.lower()) < lines.find(word):
                               
                                result[tkns]=word

                  

                            
  
      
    return render_template("index.html", output=result)


if __name__=="__main__":
    app.run(debug=True)  

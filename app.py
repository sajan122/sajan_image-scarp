from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import logging
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
import os

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
                try:

                    # query to search for images
                    query = request.form['content'].replace(" ","")

                            # directory to store downloaded images
                    save_directory = "static/images/" #Agar tum Flask ke static folder me floder rakhna chahte ho (taaki browser se directly show karwana cahate ho to tume  photo ko tume static ande rakhan hoga ) "static/images/" folder ke ander folder


                            # create the directory if it doesn't exist
                    if not os.path.exists(save_directory):
                        os.makedirs(save_directory) #folder makir  matlab uya ki ager ho hai do thik nahi to bana  degega 



                            # fake user agent to avoid getting blocked by Google
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

                            # fetch the search results page
                    response = requests.get (f"https://www.google.com/search?q={query}&sca_esv=825d6cf8198b9510&udm=2&biw=2133&bih=1058&sxsrf=AE3TifNzh3VunnRkjWCO2Rbb1un8nzOyHw%3A1760955290480&ei=mgv2aIuJHce74-EPo_W1iAI&ved=0ahUKEwiLvrfUxbKQAxXH3TgGHaN6DSEQ4dUDCBE&oq=sudhanshu+kumar&gs_lp=Egtnd3Mtd2l6LWltZyIPc3VkaGFuc2h1IGt1bWFyMgcQIxgnGMkCMgYQABgHGB4yBhAAGAcYHjIFEAAYgAQyBhAAGAcYHjIGEAAYBxgeMgUQABiABDIGEAAYBxgeMgYQABgHGB4yBhAAGAcYHkjHDVAAWABwAXgAkAEAmAEAoAEAqgEAuAEMyAEAmAIBoAIYmAMAiAYBkgcBMaAHALIHALgHAMIHAzQtMcgHEw&sclient=gws-wiz-img") #Yeh sirf(only) first page ka HTML lata hai. requests.get” se poore Google Images nahi milenge.

                            # parse the HTML using BeautifulSoup
                    soup = BeautifulSoup(response.content, "html.parser")

                            # find all img tags
                    image_tags = soup.find_all("img")

                            # download each image and save it to the specified directory
                    del image_tags[0]
                    img_data=[]  # sirf store mongodb me karne ke liye ye use hota hai 
                    image_files = [] 
                    for index,image_tag in enumerate(image_tags):
                                # get the image source URL
                                image_url = image_tag['src']
                                #print(image_url)
                                
                                # send a request to the image URL and save the image
                                image_data = requests.get(image_url).content
                                mydict={"Index":index,"Image":image_data}
                                img_data.append(mydict)
                                filename = f"{query}_{image_tags.index(image_tag)}.jpg"   #"cat_0.jpg" jo src return(store ho rah hai)  kon index par hai o dedo
                        
                                with open(os.path.join(save_directory, filename), "wb") as f: 
                                     f.write(image_data)
       
                                                       
                                image_files.append(filename)                       
                    client = pymongo.MongoClient("mongodb+srv://sajan:Sajan%40123@cluster0.5u8yykc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0") # sirf store mongodb me karne ke liye ye use hota hai 
                    db = client['image_scrap']
                    review_col = db['image_scrap_data']
                    review_col.insert_many(img_data)          

                    return render_template("result.html",image_files=image_files,query=query)
                except Exception as e:
                    logging.info(e)
                    return'something is wrong'
            # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000) #8000 to http://127.0.0.1:8000 nahi port nahi dekha to http://127.0.0.1:5000 lekh do matlab port number dena hoga last me

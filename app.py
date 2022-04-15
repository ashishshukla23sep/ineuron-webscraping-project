
import pymongo
from flask import Flask,render_template,url_for,redirect
from flask_cors import CORS,cross_origin
app=Flask(__name__)

client = pymongo.MongoClient("mongodb+srv://ashishshukla23sep:mm1332647@cluster0.o1yzz.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db1=client["inureon"]
col1=db1['inureon_webscrapping']

final_content=[]
for i in col1.find():
    final_content.append(i)
for i in final_content:
    i.pop('_id')

categories=[]
for i in range(0,len(final_content)):
    for j in range(0,len(list(final_content[i].keys()))):
        categories.append(list(final_content[i].keys())[j])


sub_categories=[]
for i in range(0,len(final_content)):
    sub_categories.append(list(list(final_content[i].values())[0].keys()))
length=len(final_content)

courses_detais=[]
for i in range(0,10):
    courses_detais.append(list(final_content[i].values()))


@app.route("/")
@cross_origin()
def main():
    return render_template("reqest.html",categories_length=zip(categories,list(range(0,length))),sub_categories=sub_categories,courses_detais=courses_detais )

if __name__=="__main__":
    app.run(port=8080,debug=True)
import redis
import json
import logging
import flask
from flask import request, jsonify

#r = redis.Redis(host='localhost',port=7000)
r = redis.StrictRedis('localhost', 7000, charset="utf-8", decode_responses=True)

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def productCount():
    return r.incr("productID")
def categoryCount():
    return r.incr("categoryID")    
def imageCount():
    return r.incr("imageID")   

@app.route('/', methods=['GET'])
def home():
    r.set("User:12","Nareshbhai")
    op= r.get("User:12")
    return op

# Add and update product (Pass "productID" : 1 if you want to update)
# { "name":"KichanStuff", "description" : "This is description", "vender":"Vendor", "Price" : 12, "currency" :"USD", "MainCategory": 1 }
@app.route('/addprodust', methods=['POST'])
def addprodust():
    record = json.loads(request.data)
    cat_id = record['MainCategory']   
    categoryArray =r.zrangebyscore("category",cat_id,'('+str(int(cat_id)+1),withscores=True)
    print(categoryArray)
    if not categoryArray:
        return "{'message': 'No category found please add category first and then add product!'}"
    else:
        if "productID" not in record:
            productID = productCount()
        else:
            productID = record["productID"]
        print(productID)
        r.hmset("product:"+ str(productID),{"name":record['name'],"description":record['description'],"vender":record['vender'],"Price":record['Price'],"currency":record['currency'],"MainCategory":record['MainCategory']})
        r.zadd("category:"+ str(record['MainCategory'])+":product", {productID:productID}) # cat:1:prod 1 2 3 3 
        r.zadd("productName",{record['name']:productID}) # Normalisse product name 
        return jsonify(record)

#ADD product image
#{ "name":"KichanStuff", "image": "01010101001010101", "productID": 1, "url":"https://miro.medium.com/max/1200/1*mk1-6aYaf_Bes1E3Imhc0A.jpeg" }
@app.route('/addimage', methods=['POST'])
def addimage():
    record = json.loads(request.data)
    imageID = imageCount()
    print(imageID)
    r.hmset("image:"+ str(imageID),{"name":record['name'],"image":record['image'],"productID":record['productID'],"url":record['url']})
    r.zadd("product:"+str(record['productID'])+":image",{imageID:imageID}) # pro:1:image comple xcheck
    return jsonify(record)
    
@app.route('/addpcategory', methods=['POST'])
def addpcategory():
    record = json.loads(request.data)
    if r.zscore("category",record['name']) is None:
        CategoryID = categoryCount()
        r.zadd("category",{record['name']: CategoryID})
    else:
        record["CategoryID"] = r.zscore("category",record['name']) 
        record["message"] = "Category already exist" 
    return jsonify(record)

##################################################################################################################################################################
# Delete product by ID 

#use multi exec for and pipeline
@app.route('/deleteProductID/<pro_id>', methods=['DELETE'])
def deleteProductID(pro_id):
    product_value = r.hgetall("product:"+str(pro_id))
    a = product_value['MainCategory']
    product_image_list = r.zrangebyscore("product:"+str(pro_id)+":image",'-inf','+inf')
    print(f'fount all productimage {product_image_list}')
    for i in product_image_list:
        r.delete("image:"+str(i))
    r.delete("product:"+str(pro_id)+":image")
    r.zrem("category:"+a+":product",pro_id)
    r.delete("product:"+str(pro_id))
    return "deletd sussfully"



##################################################################################################################################################################
#https://github.com/kenkyl/product-catalog/blob/master/src/db.py

#use the pipeline opt
@app.route('/getproductbyid/<pro_id>', methods=['GET'])
def getproductbyid(pro_id):
    product_value = r.hgetall("product:"+str(pro_id))
    print('found product: {product_value}')
    product_image_list = r.zrangebyscore("product:"+str(pro_id)+":image",'-inf','+inf')
    print(f'fount all productimage {product_image_list}')
    images = []
    for i in product_image_list:
        print(r.hgetall("image:"+str(i)))
        images.append(r.hgetall("image:"+str(i)))
    print(type(product_value)) 
    product_value["p_images"] = images  
    return product_value

# Search All product by CateID
@app.route('/serachProducCatID/<cat_id>', methods=['GET'])
def serachProducCatID(cat_id):
    productArray =r.zrangebyscore("category:"+cat_id+":product",'-inf','+inf',withscores=True)
    print(productArray)
    if not productArray:
        return "{'message': 'no category found'}"
    else:
        allproducts=[]
        op = list(productArray)
        for i in op:
            allproducts.append(getproductbyid(int(i[1])))
        return jsonify(allproducts)

#Full text search this is not called FTS
@app.route('/serachProductName/<product_name>', methods=['GET'])
def serachProductName(product_name):
    products =r.zscan("productName",cursor=0,match="*"+product_name+"*")
    print(products)
    if not products[1]:
        return "{'message': 'no product found'}"
    else:
        allproducts=[]
        op = list(products[1])
        for i in op:
            allproducts.append(getproductbyid(int(i[1])))
        return jsonify(allproducts)

# Search category by id
@app.route('/getcategorybyid/<cat_id>', methods=['GET'])
def getcategorybyid(cat_id):
    categoryArray =r.zrangebyscore("category",cat_id,'('+str(int(cat_id)+1),withscores=True)
    print(categoryArray)
    if not categoryArray:
        return "{'message': 'no category found'}"
    else:
        return jsonify(categoryArray)

def index():
    print("This is sssssss")

index()
app.run()

from fileinput import filename
import io
import os
import random
from random import seed
from re import A
import string
import warnings
from PIL import Image
import hashlib
import boto3

from dotenv import load_dotenv
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from flask import Flask, request, send_file, make_response
from flask_cors import CORS
from waitress import serve 

import argostranslate.package, argostranslate.translate

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

load_dotenv()
stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'],
    verbose=True,
)

app = Flask(__name__)
CORS(app)

from_code = "ja"
to_code = "en"

#install Argos Translate package
download_path = "translate-ja_en.argosmodel"
argostranslate.package.install_from_path(download_path)

# Translate Settings
installed_languages = argostranslate.translate.get_installed_languages()
from_lang = list(filter(
	lambda x: x.code == from_code,
	installed_languages))[0]
to_lang = list(filter(
	lambda x: x.code == to_code,
	installed_languages))[0]
translation = from_lang.get_translation(to_lang)
s3client = boto3.client('s3')
bucket = "kemushiboy.com-portrait-generator-img"

#Firestore Settings
# Use a service account.
fscred = credentials.Certificate('stable-diffusion-api-kemushi-firebase-adminsdk-urwnm-c45f669ba6.json')
fsapp = firebase_admin.initialize_app(fscred)
fsdb = firestore.client()

@app.route("/<language>", methods=["POST"])
def generate(language):
    
    req = request.form
    #Japanese
    if language == "ja":
        name = req.get("name")
        gender = req.get("gender")
        age = req.get("age")
        country_name = req.get("country")
        if country_name == "":
            country_name = "日本"
        country = translation.translate(country_name+"人")
        address = translation.translate(req.get("address"))
        born = translation.translate(req.get("born"))
        marriage = req.get("marriage")
        occupation = translation.translate(req.get("occupation"))
        favorite = translation.translate(req.get("favorite"))
        personality_text = translation.translate(req.get("personality"))
        personality = ""
        if personality_text != "":
            personality = personality_text + " personality, "# difficult to translate personality text.
        creed = req.get("creed")
    #english
    elif language == "en":
        name = req.get("name")
        gender = req.get("gender")
        age = req.get("age")
        country_name = req.get("country")
        country = translation.translate(country_name+"人")
        address = req.get("address")
        born = req.get("born")
        marriage = req.get("marriage")
        occupation = req.get("occupation")
        favorite = req.get("favorite")
        personality_text = req.get("personality")
        personality = personality_text + " personality, "
        creed = req.get("creed")
        
    
    prompt = "A portrait of " + country + " " + gender + ", named " + name  + ", at age of " + age + ", " + occupation + ", favorite in " + favorite + ", " + personality + "living in " + address + ", born in " + born + ", " + marriage + ", " + creed + ", taken with Canon 5D Mk4 with no background."
    #print(prompt)
    seed = random.randrange(0, 4294967295)
    filename = hashlib.sha256(prompt.encode("utf-8")).hexdigest() + "_" + str(seed) + ".png"
    hashName = hashlib.sha256(name.encode("utf-8")).hexdigest()
    hashAddress = hashlib.sha256(address.encode("utf-8")).hexdigest()
    
    userData = {"timestamp" : firestore.SERVER_TIMESTAMP, "name" : hashName, "gender" : gender, "age" : age, "country" : country, "address" : hashAddress, "born" : born, "marriage" : marriage, "occupation" : occupation, "favotite" : favorite, "personality" : personality_text, "creed" : creed, "seed" : seed, "filename" : filename}
    
    answers = stability_api.generate(
        prompt=prompt,
        seed=[seed],
        width=512,
        height=512,

    )
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
                return errorTextResponse("不適切な入力を検知しました\nDetected non safe input.", 400)
                
            if artifact.type == generation.ARTIFACT_IMAGE:
                #Upload to S3
                s3client.upload_fileobj(io.BytesIO(artifact.binary), bucket, "img/" + filename)
                
                #SaveToDB
                fsdb.collection(u'users').add(userData)
                
                #Return img
                return send_file(
                    io.BytesIO(artifact.binary),
                    mimetype='image/png'
                )

def errorTextResponse(text,code):
    response = make_response(text,code)
    response.statusText = "Detected non safe input."
    return response

if __name__ == "__main__":
    print("start app.py")
    serve(app, host="0.0.0.0", port=os.environ['PORT'], threads=10)

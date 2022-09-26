import io
import os
import warnings
from PIL import Image

from dotenv import load_dotenv
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from flask import Flask, request, send_file

import argostranslate.package, argostranslate.translate

load_dotenv()
stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'],
    verbose=True,
)

app = Flask(__name__)

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


@app.route("/", methods=["POST"])
def generate():
    req = request.form
    prompt = req.get("prompt", "")
    answers = stability_api.generate(
        prompt=translation.translate(prompt)
    )
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                return send_file(
                    io.BytesIO(artifact.binary),
                    mimetype='image/png'
                )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ['PORT'])

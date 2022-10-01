import argostranslate.package, argostranslate.translate

from_code = "ja"
to_code = "en"

#install Argos Translate package
download_path = "translate-ja_en.argosmodel"
argostranslate.package.install_from_path(download_path)

# Translate
installed_languages = argostranslate.translate.get_installed_languages()
from_lang = list(filter(
	lambda x: x.code == from_code,
	installed_languages))[0]
to_lang = list(filter(
	lambda x: x.code == to_code,
	installed_languages))[0]
translation = from_lang.get_translation(to_lang)
translatedText = translation.translate("こんにちは")
print(translatedText)
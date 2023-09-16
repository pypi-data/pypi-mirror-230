import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from pydantic import BaseModel
from faker import Faker
import os
import pandas as pd
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
nltk.download('stopwords')


class textAnonyms(BaseModel):
    originalText: str
    textFormat: str


stop_words = set(stopwords.words('french'))
liste_pays = ["afghanistan", "afrique du sud", "albanie", "algérie", "allemagne", "andorre", "angola", "antigua-et-barbuda", "arabie saoudite", "argentine", "arménie", "aruba", "australie", "autriche", "azerbaïdjan", "bahamas", "bahreïn", "bangladesh", "barbade", "belgique", "belize", "bélarus", "bénin", "bhoutan", "birmanie", "bolivie", "bosnie-herzégovine", "botswana", "brésil", "brunéi", "bulgarie", "burkina faso", "burundi", "cambodge", "cameroun", "canada", "cap-vert", "chili", "chine", "chypre", "colombie", "comores", "corée du nord", "corée du sud", "costa rica", "côte d'ivoire", "croatie", "cuba", "curaçao", "danemark", "djibouti", "dominique", "egypte", "el salvador", "émirats arabes unis", "équateur", "érythrée", "espagne", "estonie", "éthiopie", "fidji", "finlande", "france", "gabon", "gambie", "géorgie", "ghana", "grèce", "grenade", "guatemala", "guinée", "guinée équatoriale", "guinée-bissau", "guyana", "haïti", "honduras", "hongrie", "inde", "indonésie", "irak", "iran", "irlande", "islande", "israël", "italie", "jamaïque", "japon", "jordanie", "kazakhstan", "kenya", "kirghizistan", "kiribati", "kosovo", "koweït", "laos", "lesotho", "lettonie", "liban", "libéria", "libye", "liechtenstein", "lituanie", "luxembourg", "macédoine du nord", "madagascar", "malaisie", "malawi", "maldives", "mali", "malte", "maroc", "marshall", "maurice", "mauritanie", "mexique", "micronésie", "moldavie", "monaco", "mongolie", "monténégro", "mozambique", "namibie", "nauru", "nepal", "nicaragua", "niger", "nigeria", "niue", "norvège", "nouvelle-zélande", "oman", "ouganda", "ouzbékistan", "pakistan", "palaos", "panama", "papouasie nouvelle-guinée", "paraguay", "pays-bas", "pérou", "philippines", "pologne", "portugal", "qatar", "république centrafricaine", "république démocratique du congo", "république dominicaine", "république du congo", "république tchèque", "roumanie", "royaume-uni", "russie", "rwanda", "saint-christophe-et-niévès", "saint-marin", "saint-martin", "saint-vincent-et-les-grenadines", "sainte-lucie", "salomon", "salvador", "samoa", "são tomé-et-principe", "sénégal", "serbie", "seychelles", "sierra leone", "singapour", "slovaquie", "slovénie", "somalie", "soudan", "soudan du sud", "sri lanka", "suède", "suisse", "surinam", "swaziland", "syrie", "tadjikistan", "tanzanie", "tchad", "thaïlande", "timor oriental", "togo", "tonga", "trinité-et-tobago", "tunisie", "turkménistan", "turquie", "tuvalu", "ukraine", "uruguay", "vanuatu", "vatican", "venezuela", "vietnam", "yémen", "zambie", "zimbabwe"]
faker = Faker(["fr_FR"])



def anonymiser_mot(text: textAnonyms ):
    anonymisedData = pd.read_csv("words.csv", dtype={"original": str, "anonymous": str})

    if(text.textFormat == "PERSON"):
        fakeData = faker.name()
    elif(text.textFormat == "DATE"):
        fakeData = faker.date()
    elif(text.textFormat == "LOCATION"):
        fakeData = faker.address()
    elif(text.textFormat == "NUMBER"):
        fakeData = faker.numerify()
    elif(text.textFormat == "COUNTRY"):
        fakeData = faker.country()
    elif(text.textFormat == "ORGANIZATION"):
        fakeData = faker.company()



    while any(anonymisedData["anonymous"] == fakeData):
        fakeData = faker.name()

    anonymisedData = pd.concat([anonymisedData, pd.DataFrame([[text.originalText, fakeData]], columns=["original", "anonymous"])])
    anonymisedData.to_csv("words.csv", index=False)

    return fakeData



def desanonymiser_mot(anonymised_name):
    anonymisedData = pd.read_csv("words.csv", dtype={"original": str, "anonymous": str})
    if not anonymisedData.empty:
        originalData = anonymisedData[anonymisedData["anonymous"] == anonymised_name]["original"]
        if not originalData.empty:
            return originalData.iloc[0]
    return None

def initialiser():
    csv_file_path = "words.csv"

    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)

    empty_dataframe = pd.DataFrame(columns=["original", "anonymous"])

    empty_dataframe.to_csv(csv_file_path, index=False)




def anonymiser_paragraphe(paragraphe):

    phrase = paragraphe
    phrase = phrase.replace(".", ". ")
    phrase = phrase.replace(",", ", ")

    tokens = word_tokenize(phrase, language="french")
    tags = pos_tag(tokens )
    entites_nommees = []

    stop_words = set(stopwords.words('french'))
    pronoms_possessifs = ["mon", "ma", "mes", "ton", "ta", "tes", "son", "sa", "ses", "notre", "votre", "leur", "leurs","merci","alors","fh","intervention"]
    stop_words.update(pronoms_possessifs)

    for word, tag in tags:

        if word.lower() in liste_pays:
            entites_nommees.append(("COUNTRY", word))
        elif tag == "NNP" and "DS" in word :
            entites_nommees.append(("NUMBER", word))
        elif tag == "NNP" and word.isupper() and word.lower() not in stop_words:
            entites_nommees.append(("ORGANIZATION", word))
        elif tag == "NNP" and word.lower() not in stop_words:
            entites_nommees.append(("PERSON", word))
        elif tag == "CD" and "/" in word :
            entites_nommees.append(("DATE", word))
        elif tag == "CD":
            entites_nommees.append(("NUMBER", word))
        elif tag == "NNP" and word.lower() not in stop_words:
            entites_nommees.append(("LOCATION", word))


    for entity_type, entity_value in entites_nommees:
        text = textAnonyms(originalText=entity_value, textFormat=entity_type)
        paragraphe = paragraphe.replace(entity_value, anonymiser_mot(text))

    return paragraphe

def desanonymiser_paragraphe(anonymous_paragraphe):


    anonymisedData = pd.read_csv("words.csv", dtype={"original": str, "anonymous": str})
    for index, row in anonymisedData.iterrows():

        anonymous_paragraphe = anonymous_paragraphe.replace(row["anonymous"],row["original"])
    return anonymous_paragraphe

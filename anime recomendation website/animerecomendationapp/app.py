from flask import Flask, render_template, request
import csv
import ast
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import stopwords
from operator import itemgetter
import numpy as np
from nltk.corpus import wordnet
import nltk
import ssl
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

# Replace 'path/to/serviceAccountKey.json' with the actual path to your service account key file
cred = credentials.Certificate('serviceKey.json')
firebase_admin.initialize_app(cred)

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')


app = Flask(__name__)


#-------- HOME PAGE DATA --------
line_count = 0
homepage = []
shounen = []
romance = []
comedy = []

with open('anime_data.csv', newline='', encoding='UTF-8') as f:
	reader = csv.reader(f)
	for line in reader:
		try:
			new = ast.literal_eval(line[5])
			rating = float(line[2])
		except:
			new = ['none']
			rating = 5
		if 'Hentai' not in new and new != [] and 'Kids' not in new and 'Ecchi' not in new and rating >= 6.9:
			homepage.append(line)
			line_count += 1
		if 'Hentai' not in new and new != [] and 'Kids' not in new and 'Ecchi' not in new and rating >= 6.0 and 'Shounen' in new:
			shounen.append(line)
			line_count += 1
		if 'Hentai' not in new and new != [] and 'Kids' not in new and 'Ecchi' not in new and rating >= 6.0 and 'Romance' in new:
			romance.append(line)
			line_count += 1
		if 'Hentai' not in new and new != [] and 'Kids' not in new and 'Ecchi' not in new and rating >= 6.0 and 'Comedy' in new:
			comedy.append(line)
			line_count += 1
##--------------------------------



##--------------------------------
#-------- DATA --------
data_list = []

with open('anime_data.csv', newline='', encoding='UTF-8') as f:
	reader = csv.reader(f)
	for line in reader:
		try:
			new = ast.literal_eval(line[5])
			if new != [] and 'Hentai' not in new and 'Kids' not in new:		
				data_list.append(line)	
		except:
			pass	

#getting anime descriptions
print("Data Length: ",len(data_list))
anime_description = []
for line in data_list:
	try:
		anime_description.append(line[3]+" "+line[1])
	except:
		pass


#fuction to remove stop words
def filter_words(sent):
	stopword_list = stopwords.stopwords
	puncuation_removed = re.sub(r'[^\w\s]','',sent)
	splint_sentence = puncuation_removed.split(' ')
	new_sentence = []
	
	for word in splint_sentence:
		if word not in stopword_list:
			new_sentence.append(word)
			#try:
			#	if(wordnet.synsets(word).name().split('.', 1)[1] == "n"):
			#		for syn in wordnet.synsets(word):
			#			for i in syn.lemmas():
			#				new_sentence.append(i.name())
			#except:
			#	pass

	return ' '.join(new_sentence)

print("Cleaning Data")
cleaned_description_list = []
for des in anime_description:
	cleaned_description_list.append(filter_words(des))

print("Vectorizing Data")
#vectorize and tokenize
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(cleaned_description_list)
##--------------------------------
print("App ready!")

@app.route('/', methods=['GET','POST'])
def index():

	if request.method == 'POST':

		#getting form data
		user_description = request.form.get('inputform')

		#Get filtered user description
		user_description = filter_words(user_description)

		#This vectorizes the users entry
		Y = vectorizer.transform([user_description])

		#Get similarity
		similarities = [cosine_similarity(Y[0],X[i])[0][0] for i in range(len(cleaned_description_list))]
		thresh = max(similarities) * 0.25

		#check similarity between user sentence and anime descriptions
		index_count = 0
		index = []
		for i in similarities:
			if i >= thresh:
				index.append([index_count, i])
			if i == max(similarities):
				print(data_list[index_count])
			index_count += 1

		#Sort the data list
		index = sorted(index, key=itemgetter(1))
		index = [data_list[i[0]] for i in index]

		#this is for the HTML
		dataLength = 25
		if len(index) < 25:
			dataLength = len(index)
		
		return render_template('main.html', homepage_recs = homepage, 
										homepage_shounen = shounen,
										homepage_romance = romance,
										homepage_comedy = comedy,
										data1 = index,
										dataLength = dataLength, 
										loadedRecs = True)
	random.shuffle(homepage)
	random.shuffle(shounen)
	random.shuffle(romance)
	random.shuffle(comedy)
	return render_template('main.html', homepage_recs = homepage, 
										homepage_shounen = shounen,
										homepage_romance = romance,
										homepage_comedy = comedy,
										loadedRecs = False)





@app.route('/keyword', methods=['GET','POST'])
def keyword():

	return render_template('keyword.html')
	


if __name__ == '__main__':
	app.run(debug=True)

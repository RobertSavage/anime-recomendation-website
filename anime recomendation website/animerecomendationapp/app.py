from flask import Flask, render_template, request
import csv
import ast
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
import nltk
import re
import stopwords
from operator import itemgetter
#from nltk.corpus import wordnet
import os

#nltk.download(download_dir='C:/Users/edwar/Documents/Python/FLASK APPS/anime recomendation website')
#
#nltk.data.path.append(os.getcwd()+'\\corpora\\wordnet')

app = Flask(__name__)


#-------- HOME PAGE DATA --------
line_count = 0
homepage_imgs = []

with open('anime_data.csv', newline='', encoding='UTF-8') as f:
	reader = csv.reader(f)
	for line in reader:
		try:
			new = ast.literal_eval(line[5])
		except:
			print(line)
		if 'Hentai' not in new and new != [] and 'Kids' not in new and 'Ecchi' not in new:
			homepage_imgs.append(line)
			line_count += 1


##--------------------------------
#-------- GENRE PAGE DATA --------
data_list = []

with open('anime_data.csv', newline='', encoding='UTF-8') as f:
	reader = csv.reader(f)
	for line in reader:
		try:
			new = ast.literal_eval(line[5])
		except:
			print(line)
		if new != [] and 'Kids' not in new:		
			data_list.append(line)

##--------------------------------



@app.route('/')
def index():
	homepage_img_1= homepage_imgs[ random.randint(0,len(homepage_imgs)-1) ]
	homepage_img_2= homepage_imgs[ random.randint(0,len(homepage_imgs)-1) ]
	homepage_img_3= homepage_imgs[ random.randint(0,len(homepage_imgs)-1) ]
	homepage_img_4= homepage_imgs[ random.randint(0,len(homepage_imgs)-1) ]
	homepage_img_5= homepage_imgs[ random.randint(0,len(homepage_imgs)-1) ]
	return render_template('main.html', homepage_img_1= homepage_img_1,
										homepage_img_2= homepage_img_2,
										homepage_img_3= homepage_img_3,
										homepage_img_4= homepage_img_4,
										homepage_img_5= homepage_img_5)


@app.route('/genre', methods=['GET','POST'])
def genre():
	if request.method == 'POST':
		print(request.form.get('submit'))
		print(request.form.get('load_more'))
		if request.form.get('submit') == 'Submit':
			recived_list = []
			for line in data_list:
				try:
					new = ast.literal_eval(line[5])
					check = set(request.form.getlist('mycheckbox')).issubset(new)
					if check is True and len(new) > 0:
						recived_list.append(line)
				except IndexError:
					pass
			if len(recived_list) == 0:
				recived_list = [['','','','','','']]

			return render_template('genre_post_render.html', data1 = recived_list[ random.randint(0,len(recived_list)-1) ],
															data2 = recived_list[ random.randint(0,len(recived_list)-1) ],
															data3 = recived_list[ random.randint(0,len(recived_list)-1) ],
															data4 = recived_list[ random.randint(0,len(recived_list)-1) ],
															data5 = recived_list[ random.randint(0,len(recived_list)-1) ])

			
				
	return render_template('genre.html')




@app.route('/rated', methods=['GET','POST'])
def rated():
	if request.method == 'POST':
		recived_list = []
		for line in data_list:
			try:
				score = line[2]
				if request.form.get('sectionselect') == "higher":
					if int(request.form.get('inputform')) == 10 and float(request.form.get('inputform'))-0.99 <= float(score):
						recived_list.append(line)
					elif request.form.get('inputform') <= score:
						recived_list.append(line)
					else:
						pass
				elif request.form.get('sectionselect') == "lower":
					if request.form.get('inputform') >= score:
						recived_list.append(line)
					elif int(request.form.get('inputform')) == 1 and float(request.form.get('inputform'))+0.99 <= float(score):
						recived_list.append(line)
					else:
						pass
				elif request.form.get('sectionselect') == "equal":
					if int(request.form.get('inputform')) == 10 and float(request.form.get('inputform'))-0.9 <= float(score):
						recived_list.append(line)
					elif float(request.form.get('inputform'))-0.5 <= float(score) and float(request.form.get('inputform'))+0.5 >= float(score):
						recived_list.append(line)
					else:
						pass
				else:
					recived_list.append(['','','','','','','',''])
			except:
				pass
			len_recived_data = len(recived_list)
		return render_template('rated_post_render.html', data1 = recived_list[ random.randint(0,len(recived_list)-1) ],
														data2 = recived_list[ random.randint(0,len(recived_list)-1) ],
														data3 = recived_list[ random.randint(0,len(recived_list)-1) ],
														data4 = recived_list[ random.randint(0,len(recived_list)-1) ],
														data5 = recived_list[ random.randint(0,len(recived_list)-1) ])
	
	return render_template('Rated.html')


@app.route('/keyword', methods=['GET','POST'])
def keyword():
	if request.method == 'POST':

		#getting form data
		user_description = request.form.get('inputform')
		user_description = [str(user_description)]
		print(user_description)

		#getting anime descriptions
		anime_description = []
		for line in data_list:
			try:
				anime_description.append(line[3]+" "+line[1])
			except:
				pass
		merger_list = user_description + anime_description
		
		#fuction to remove stop words
		def filter_words(sent):
			stopword_list = stopwords.stopwords
			puncuation_removed = re.sub(r'[^\w\s]','',sent)
			splint_sentence = puncuation_removed.split(' ')
			new_sentence = []
			for word in splint_sentence:
				if word not in stopword_list:
					new_sentence.append(word)
			return ' '.join(new_sentence)

		cleaned_description_list = []
		for des in merger_list:
			cleaned_description_list.append(filter_words(des))

		#vectorize and tokenize
		vectorizer = TfidfVectorizer()
		X = vectorizer.fit_transform(cleaned_description_list)

		#determin threshhold
		similarities = [cosine_similarity(X[0],X[i])[0][0] for i in range(len(merger_list)) if cosine_similarity(X[0],X[i])[0][0] < 1.0]
		thresh = max(similarities) * 0.25
		print('thresh: ',thresh)
		#check similarity between user sentence and anime descriptions
		index_count = 0
		index = []
		for i in similarities:
			if i >= thresh:
				index.append([index_count, i])
			index_count += 1
		index = sorted(index, key=itemgetter(1))
		print('len index: ',len(index))
		

		if len(index) == 0:
			data1 = ['','','','','','','','']
			data2 = ['','','','','','','','']
			data3 = ['','','','','','','','']
			data4 = ['','','','','','','','']
			data5 = ['','','','','','','','']
		elif len(index) == 1:
			data1 =	data_list[index[0][0]]
			data2 = ['','','','','','','','']
			data3 = ['','','','','','','','']
			data4 = ['','','','','','','','']
			data5 = ['','','','','','','','']
		elif len(index) == 2:
			data1 =	data_list[index[0][0]]
			data2 =	data_list[index[1][0]]
			data3 = ['','','','','','','','']
			data4 = ['','','','','','','','']
			data5 = ['','','','','','','','']
		elif len(index) == 3:
			data1 =	data_list[index[0][0]]
			data2 =	data_list[index[1][0]]
			data3 =	data_list[index[2][0]]
			data4 = ['','','','','','','','']
			data5 = ['','','','','','','','']
		elif len(index) == 4:
			data1 =	data_list[index[0][0]]
			data2 =	data_list[index[1][0]]
			data3 =	data_list[index[2][0]]
			data4 =	data_list[index[3][0]]
			data5 = ['','','','','','','','']
		elif len(index) >= 5:
			data1 =	data_list[index[0][0]]
			data2 =	data_list[index[1][0]]
			data3 =	data_list[index[2][0]]
			data4 =	data_list[index[3][0]]
			data5 =	data_list[index[4][0]]
		else:
			data1 = ['','','','','','','','']
			data2 = ['','','','','','','','']
			data3 = ['','','','','','','','']
			data4 = ['','','','','','','','']
			data5 = ['','','','','','','','']		
		return render_template('keyword_post_render.html',data1 = data1,
														data2 = data2,
														data3 = data3,
														data4 = data4,
														data5 = data5)
	return render_template('keyword.html')
	


if __name__ == '__main__':
	app.run(debug=True)

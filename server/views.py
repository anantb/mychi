import json, sys, re


from django.http import *
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.core.context_processors import csrf

from algorithm.recommend import *
from db.prefs import *
from db.entity import *
from db.session import *
from db.authors import *


'''
@author: Anant Bhardwaj
@date: Feb 12, 2012
'''


manifest = """CACHE MANIFEST
/
/main
/schedule
/paper
/static/css/desktop.css
/static/css/third-party/jquery-ui.css
/static/javascript/third-party/jquery.min.js
/static/javascript/third-party/jquery-ui.js
/static/javascript/desktop.js
/static/img/affiliation.svg
/static/img/arrows.ai
/static/img/arrows copy.ai
/static/img/arts.acorn
/static/img/arts.png
/static/img/authors.svg
/static/img/best-paper.png
/static/img/best.png
/static/img/best.svg
/static/img/calendar.svg
/static/img/cci.acorn
/static/img/cci.png
/static/img/design.acorn
/static/img/design.png
/static/img/down.png
/static/img/engineering.acorn
/static/img/engineering.png
/static/img/games.acorn
/static/img/games.png
/static/img/hci4d.acorn
/static/img/hci4d.png
/static/img/health.acorn
/static/img/health.png
/static/img/logo.png
/static/img/logo.svg
/static/img/management.acorn
/static/img/management.png
/static/img/nominee.png
/static/img/nominee.svg
/static/img/paper.svg
/static/img/right.png
/static/img/sponsors.svg
/static/img/star_closed.svg
/static/img/star_open.png
/static/img/star_open.svg
/static/img/star_yellow.png
/static/img/star_yellow.svg
/static/img/sustainability.acorn
/static/img/sustainability.png
/static/img/user_experience.acorn
/static/img/user_experience.png
NETWORK:
*"""


r = Recommender()
e = Entity()
p = Prefs()
s = Session()

def init_session(email):
	pass

def login_form(request):
	c = {}
	c.update(csrf(request))
	return render_to_response('desktop/login.html', c)



def login(request):
	if request.method == "POST":
		try:
			login_email = request.POST["login_email"]

			if(login_email != ""):
				request.session.flush()
				cursor = connection.cursor()
				cursor.execute("""SELECT id, given_name, family_name from pcs_authors where email1 like '%s' or 
					email2 like '%s' or email3 like '%s';""" %(login_email, login_email, login_email))
				data = cursor.fetchall()
				request.session['id'] = data[0][0]
				request.session['email'] = login_email
				request.session['name'] = data[0][1] + ' ' + data[0][2]
				return HttpResponseRedirect('/home')
			else:
				return login_form(request)
		except:
			print sys.exc_info()
			return login_form(request)
	else:
		return login_form(request)
		


def logout(request):
	request.session.flush()
	return HttpResponseRedirect('/login')

def manifest(request):
	return HttpResponse(manifest, mimetype='text/cache-manifest')




def home(request):
	try:
		return render_to_response('desktop/main.html', 
		{'login_id': request.session['id'], 
		'login_name': request.session['name']})	
	except KeyError:
		return HttpResponse('/login')
	except:
		pass
	


def schedule(request):
	recs = []
	starred = {}
	try:
		return render_to_response('desktop/schedule.html', 
		{'login_id': request.session['id'], 
		'login_name': request.session['name']})		
	except KeyError:
		return HttpResponseRedirect('/login')
	except:
		pass
	

def paper(request):
	try:
		return render_to_response('desktop/paper.html', 
		{'login_id': request.session['id'], 
		'login_name': request.session['name']})
	except KeyError:
		return HttpResponseRedirect('/login')
	except:
		pass


@csrf_exempt
def data(request):
	user = request.session['id']
	recs = []
	starred = {}
	if(user in p.author_likes):
		starred = {s:True for s in p.author_likes[user]['likes']}
		recs = r.get_item_based_recommendations(starred)
	return HttpResponse(json.dumps({
		'login_id': request.session['id'], 
		'login_name': request.session['name'],
		'recs':recs, 
		'starred':starred, 
		'entities': e.entities, 
		'sessions':s.sessions
		}), mimetype="application/json")

@csrf_exempt
def get_recs(request):
	papers = json.loads(request.POST["papers"])
	recs = r.get_item_based_recommendations(papers)
	return HttpResponse(json.dumps(recs), mimetype="application/json")


@csrf_exempt
def like(request, like_str):
	papers = json.loads(request.POST["papers"])
	user = request.session['id']
	res = {}
	if(user not in p.author_likes):
		p.author_likes[user] = {}
		p.author_likes[user]['likes'] = []
	for paper_id in papers:
		if(like_str=='star' and (paper_id not in p.author_likes[user]['likes']) and paper_id != ''):
			p.author_likes[user]['likes'].append(paper_id)
		if(like_str=='unstar' and (paper_id in p.author_likes[user]['likes']) and paper_id != ''):
			p.author_likes[user]['likes'].remove(paper_id)
		if(paper_id in p.author_likes[user]['likes']):
			res[paper_id] = 'star'
		else:
			res[paper_id] = 'unstar'
	recs = r.get_item_based_recommendations(p.author_likes[user]['likes'])
	return HttpResponse(json.dumps({'recs':recs, 'likes':p.author_likes[user], 'res':res}), mimetype="application/json")




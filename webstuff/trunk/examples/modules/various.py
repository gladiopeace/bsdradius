"""
Example module.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/webstuff/trunk/examples/modules/various.py $
# Author:		$Author: valts $
# File version:	$Revision: 40 $
# Last changes:	$Date: 2006-05-18 13:26:32 +0300 (Ce, 18 Mai 2006) $


import webstuff.framework as fw
from webstuff.framework import web, sessions, db

def overview():
	web.header("Content-Type", "text/plain")
	web.output("Welcome!")

def login():
	web.header("Content-Type", "text/html")

	page = fw.loadTemplate("Login")

	#page.formaction = web.current_url()
	page.webRoot = web.getvar_env('SCRIPT_NAME')
	page.formaction = ""
	languageOptions = {}
	for lang, langConf in fw.languages.iteritems():
		languageOptions[lang] = langConf['langConf']['lang_name']
	page.languageOptions = languageOptions
	page.currentLanguage = fw.getLanguage()

	frm = fw.WebForm()
	frm.username = frm.TextField("str", "your name")
	frm.password = frm.TextField()

	sessid = web.getvar("sessid", "")
	web.output("your session ID: %s<br />" % sessid)
	
	web.setcookie("sessid", "HARRHARRHARR-Your-session-ID")
	sessionId = sessions.create('peizdaans', timeout = 60)
	if frm.submitted():
		frm.setSubmittedValues()
		
		if frm.validate():
			web.output("username: %s\n" % frm.username.value)
			web.output("password: %s\n" % frm.password.value)
			# create session and store session id in cookie
			sessionId = sessions.create(frm.username.value, timeout = 60)
		else:
			web.output("invalid input!")

	frm.fillTemplate(page)
	fw.displayTemplate(page)
	
	# look for session data
	sessionId = sessions.find()
	if sessionId:
		sessions.renew() # reset expiry timer
		sesData = sessions.getData(sessionId)
		fw.pfPrint("webstuff sessid: %s\nSession data: %s" % (sessionId, sesData))
		sessions.delete()

def logout():
	sessions.delete(web.getvar(sessionId))
	web.header("Content-Type", "text/plain")
	web.output("You logged out!")

import os
import urllib
import urllib2
import xbmc
import xbmcgui
import simplejson as json
import mc

# Specific functions
def show_main_window():
	mc.ActivateWindow(14000)
	
def show_latest_window():
	mc.ActivateWindow(14001)
	
def show_movie_window():
	mc.ActivateWindow(14002)
	
def show_preview_window():
	mc.ActivateWindow(14003)

def show_series_window():
	mc.ActivateWindow(14004)
	
def show_search_window():
	mc.ActivateWindow(14005)

def show_serieslist_window():
	mc.ActivateWindow(14006)

def set_items(items):
	mc.GetActiveWindow().GetList(1050).SetItems(items)

def set_series(items):
	mc.GetActiveWindow().GetList(1060).SetItems(items)

def get_popular_programs(page):
	set_items(mc.ListItems())
	url = 'http://r7.tv2.dk/api/sputnik/programs/sort-popularity/page-' + str(page) + '.json'
	items = get_items_from_url(url);
	set_items(items)
	
def get_latest_programs(page):
	set_items(mc.ListItems())
	url = 'http://r7.tv2.dk/api/sputnik/programs/sort-latest/page-' + str(page) + '.json'
	items = get_items_from_url(url);
	set_items(items)

def get_sneakpreviews():
	set_items(mc.ListItems())
	items = get_items_from_url("http://r7.tv2.dk/api/sputnik/programs/sneakpreview.json")
	set_items(items)
	
def get_latest_movies(page):
	set_items(mc.ListItems())
	url = 'http://r7.tv2.dk/api/sputnik/categories/5/programs/sort-latest/page-' + str(page) + '.json'
	items = get_items_from_url(url);
	set_items(items)
	
def get_series_program(series, page):
	set_items(mc.ListItems())
	url = 'http://r7.tv2.dk/api/sputnik/series/' + str(series) + '/programs/sort-latest/page-' + str(page) + '.json'
	items = get_items_from_url(url);
	set_items(items)
	
def get_series():
	set_series(mc.ListItems())
	url = 'http://r7.tv2.dk/api/sputnik/series.json'
	items = get_series_from_url(url);
	set_series(items)
	
def search():
	search = xbmc.getInfoLabel('App.String(search)')
	if(len(search)>3):
		get_search(search)
	else:
		dialog = xbmcgui.Dialog()
		dialog.ok('For kort!', 'Minimum 3 karakterer i søgordet')
	
def get_search(term):
	mc.ShowDialogWait()
	set_items(mc.ListItems())
	set_series(mc.ListItems())

	socket = urllib2.urlopen("http://r7.tv2.dk/api/sputnik/search.json?query=" + term)
	result = socket.read()
	socket.close()
	if ( result ):
		programs = mc.ListItems()
		series = mc.ListItems()
		resultObj = json.loads(result);
		for program in resultObj['programs']:
			item = get_item_from_program(program)
			programs.append(item)		
		set_items(programs)
		for ser in resultObj['series']:
			item = get_item_from_series(ser)
			series.append(item)
		set_series(series)
	mc.HideDialogWait()
	
def get_series_from_url(url):
	mc.ShowDialogWait()

	socket = urllib2.urlopen(url)
	result = socket.read()
	socket.close()
	if ( result ):
		series = mc.ListItems()
		resultObj = json.loads(result);
		for ser in resultObj['series']:
			item = get_item_from_series(ser)
			series.append(item)
	mc.HideDialogWait()
	return series
	
def play_current_list_item():
	list = mc.GetActiveWindow().GetList(1050)
	listitems = list.GetItems()
	listitem = listitems[list.GetFocusedItem()]
	play_program(listitem)
	
def open_current_series():
	list = mc.GetActiveWindow().GetList(1060)
	listitems = list.GetItems()
	listitem = listitems[list.GetFocusedItem()]
	show_serieslist_window()
	get_series_program(listitem.GetProperty("id"), 1)
	set_headline(listitem.GetLabel())

def set_headline(value):
	mc.GetWindow(14006).GetLabel(120).SetLabel(str(value))

#API
def get_item_from_program(program):
	item = mc.ListItem( mc.ListItem.MEDIA_VIDEO_EPISODE )
	item.SetLabel(unicode(program['title']).encode("utf-8"))
	item.SetDescription(unicode(program['description']).encode("utf-8"))
	thumb = get_image_from_program(program)
	if(thumb != None):
		item.SetThumbnail(thumb)
	try:
		if(program['series'] != None):
			item.SetTVShowTitle(unicode(program['series']['code']).encode('utf-8'))
	except Exception, e:
		item.SetTVShowTitle("")
	if(program['season'] != None):
		item.SetSeason(int(program['season']['title']))
	else:
		item.SetSeason(0)		
	if(program['episode'] != None):
		item.SetEpisode(int(program['episode']))
	else:
		item.SetEpisode(0)		
	if('category' in program):
		item.SetGenre(unicode(program['category']['code']).encode('utf-8'))
	path = get_path_from_program(program)
	item.SetPath(path)
	item.SetProperty("id", str(program['id']))
	return item

def get_item_from_series(series):
	item = mc.ListItem( mc.ListItem.MEDIA_UNKNOWN )
	item.SetLabel(unicode(series['code']).encode("utf-8"))
	item.SetDescription(unicode(series['description']).encode("utf-8"))
	thumb = get_image_from_program(series)
	if(thumb != None):
		item.SetThumbnail(thumb)
	item.SetProperty("id", str(series['id']))
	return item
	
def get_image_from_program(program):
	for image in program['media_images']:
		if(str(image['media_image_type']['code']) == '16:9-thumb'):
			for file in image['media_image_files']:
				if(str(file['width']) == '139' and str(file['height']) == '78'):
					return str(file['location_uri'])
		elif(str(image['media_image_type']['code'] == 'poster')):
			for file in image['media_image_files']:
				if(str(file['width']) == '320' and str(file['height']) == '460'):
					return str(file['location_uri'])
	return ""

def get_background(url):
	socket = urllib2.urlopen(url)
	result = socket.read()
	socket.close()
	if ( result ):
		resultObj = json.loads(result);
		if(resultObj['media_images'] != None):
			for image in resultObj['media_images']:
				if(str(image['media_image_type']['code']) == 'bg'):
					for file in image['media_image_files']:
						return str(file['location_uri'])
	return ""

def get_path_from_program(program):
	return 'http://sputnik.tv2.dk/play/'+str(program['id'])+'/'

def login_user(username, password):
	http = mc.Http()
	if(len(username)>0 and len(password)>0):
		params = "username="+username+"&password="+password
		result = http.Post('http://ajax.tv2.dk/login/user/login/', params)
		if ( result ):
			resultObj = json.loads(result);
			if(resultObj['success']):
				return True
	return False
	
def login():
	dialog = xbmcgui.Dialog()
	dp = xbmcgui.DialogProgress()

	username = xbmc.getInfoLabel('App.String(username)')
	password = xbmc.getInfoLabel('App.String(password)')
	
	if(len(username)>0):
		if not dialog.yesno('Ændre login', 'Vil du ændre nuværende login?'):
			return
		
	username = ""
	password = ""
		
	while len(username)==0 or len(password)==0:
		xbmc.executebuiltin('App.SetString(username,,Indtast sputnik brugernavn)')
		xbmc.executebuiltin('App.SetString(password,,Indtast sputnik adgangskode,true)')
		
		username = xbmc.getInfoLabel('App.String(username)')
		password = xbmc.getInfoLabel('App.String(password)')
		
		try:
			dp.create( "", "", "" )
			if(login_user(username, password)):
				dialog.ok('Sådan!', 'Du er nu logget ind!');
				break

			username = ""
			password = ""
			if not dialog.yesno('Login fejlet', 'Vi kunne ikke logge dig ind - Vil du prøve igen?'):
				break
							
		except Exception, e:
			dp.close()
			dialog.ok('Error', str(e))

def play_program(listitem):
	programid = listitem.GetProperty("id")
	type = "program" #TODO: Broadcasts
	dp = xbmcgui.DialogProgress()
	dialog = xbmcgui.Dialog()

	path = listitem.GetPath();
		
	username = xbmc.getInfoLabel('App.String(username)')
	password = xbmc.getInfoLabel('App.String(password)')
		
	try:
		if not (login_user(username, password)):
			raise Exception("Kunne ikke logge dig ind!");
		if not (login_user(username, password)):
			raise Exception("Kunne ikke logge dig ind!");
		newpath = str('flash://sputnik.dk/src=' + urllib.quote_plus("http://sputnik-dyn.tv2.dk/player/simple/id/"+programid+"/type/"+type+"/") + '&bx-ourl=' + urllib.quote_plus(path) + '&bx-jsactions=' + urllib.quote_plus('http://dl.dropbox.com/u/93155/controls.js'))
		listitem.SetPath(newpath)
		mc.GetPlayer().Play(listitem)
		listitem.SetPath(path)
			
	except Exception, e:
		dialog.ok('Error', str(e))
		dp.close()
			
def get_items_from_url(url):
	mc.ShowDialogWait()
	
	socket = urllib2.urlopen(url)
	result = socket.read()
	socket.close()
	if ( result ):
		resultObj = json.loads(result);
		items = mc.ListItems()
		for program in resultObj['programs']:
			item = get_item_from_program(program)
			items.append(item)		
				
	mc.HideDialogWait()
	return items


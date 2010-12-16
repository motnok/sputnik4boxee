import os
import urllib
import urllib2
import xbmc
import xbmcgui
import simplejson as json
import mc

# Specific functions
def set_items(items):
	mc.GetActiveWindow().GetList(1150).SetItems(items);
	mc.GetActiveWindow().GetControl(8110).SetVisible(True);
	
def set_series(series):
	mc.GetActiveWindow().GetList(1250).SetItems(series);
	mc.GetActiveWindow().GetControl(8120).SetVisible(True);
	
def set_categories(categories):
	mc.GetActiveWindow().GetList(1350).SetItems(categories);
	mc.GetActiveWindow().GetControl(8130).SetVisible(True);
	
def show_programs_view():
	mc.GetActiveWindow().GetList(1150).SetVisible(True);
	mc.GetActiveWindow().GetList(1250).SetVisible(False);
	mc.GetActiveWindow().GetList(1350).SetVisible(False);
	
def show_series_view():
	mc.GetActiveWindow().GetList(1150).SetVisible(False);
	mc.GetActiveWindow().GetList(1250).SetVisible(True);
	mc.GetActiveWindow().GetList(1350).SetVisible(False);

def show_categories_view():
	mc.GetActiveWindow().GetList(1150).SetVisible(False);
	mc.GetActiveWindow().GetList(1250).SetVisible(False);
	mc.GetActiveWindow().GetList(1350).SetVisible(True);
	
def focus_programs_view():
	mc.GetActiveWindow().GetControl(1150).SetFocus();
	
def focus_series_view():
	mc.GetActiveWindow().GetControl(1250).SetFocus();

def focus_categories_view():
	mc.GetActiveWindow().GetControl(1350).SetFocus();
	
def clear():
	mc.GetActiveWindow().GetList(1150).SetItems(mc.ListItems());
	mc.GetActiveWindow().GetList(1250).SetItems(mc.ListItems());
	mc.GetActiveWindow().GetList(1350).SetItems(mc.ListItems());
	mc.GetActiveWindow().GetControl(8110).SetVisible(False);
	mc.GetActiveWindow().GetControl(8120).SetVisible(False);
	mc.GetActiveWindow().GetControl(8130).SetVisible(False);

def set_headline(newLabel):
	label = mc.GetActiveWindow().GetLabel(120);
	label.SetLabel(newLabel);

def handle_item_select():
	list = mc.GetActiveWindow().GetList(1150);
	set_action_from_list(list);

def handle_series_select():
	list = mc.GetActiveWindow().GetList(1250);
	set_action_from_list(list);
	
def handle_categories_select():
	list = mc.GetActiveWindow().GetList(1350);
	set_action_from_list(list);

def set_action_from_list(list):
	listitems = list.GetItems();
	item = listitems[list.GetFocusedItem()];
	
	action = item.GetProperty("action");
	if(action != None):
		mc.GetActiveWindow().PushState();
		set_action(action, item);

def set_action(action, item = None):
	set_headline("");	
	if(action == 'popular'):
		show_popular_programs(1);
	elif(action == 'latest'):
		get_latest_programs(1);
	elif(action == 'previews'):
		get_sneakpreviews();
	elif(action == 'search'):
		search();
	elif(action == 'series'):
		if(item != None and item.GetProperty("id")):
			mc.GetActiveWindow().PushState();
			get_series_program(item.GetProperty("id"), 1);
		else:
			get_series();
	elif(action == 'broadcast'):
		if(item != None and item.GetProperty("id")):
			mc.GetActiveWindow().PushState();
			play_program(item, 'broadcast');
		else:
			get_broadcasts();
	elif(action == 'login'):
		login();
	elif(action == 'program'):
		play_program(item);
	elif(action == 'category'):
		if(item != None and item.GetProperty("id")):
			get_categories(item.GetProperty("id"));
		else:
			get_categories();
	
def show_popular_programs(page):
	clear();
	url = 'http://r7.tv2.dk/api/sputnik/programs/sort-popularity/page-' + str(page) + '.json'
	items = get_programs_from_url(url);
	set_items(items);
	show_programs_view();
	focus_programs_view();
 	set_headline("Mest populære");
	
def get_latest_programs(page):
	clear();
	url = 'http://r7.tv2.dk/api/sputnik/programs/sort-latest/page-' + str(page) + '.json'
	items = get_programs_from_url(url);
	set_items(items)
	show_programs_view();
	focus_programs_view();
	set_headline("Seneste");

def get_sneakpreviews():
	clear();
	items = get_programs_from_url("http://r7.tv2.dk/api/sputnik/programs/sneakpreview.json")
	set_items(items)
	show_programs_view();
	focus_programs_view();
	set_headline("Snigpræmierer");
	
def get_latest_movies(page):
	clear();
	url = 'http://r7.tv2.dk/api/sputnik/categories/5/programs/sort-latest/page-' + str(page) + '.json'
	items = get_programs_from_url(url);
	set_items(items);
	show_programs_view();
	focus_programs_view();
	
def get_series_program(series, page):
	clear();
	url = 'http://r7.tv2.dk/api/sputnik/series/' + str(series) + '/programs/sort-latest/page-' + str(page) + '.json'
	items = get_programs_from_url(url);
	set_items(items);
	show_programs_view();
	focus_programs_view();
	
def get_series():
	clear();
	url = 'http://r7.tv2.dk/api/sputnik/series.json'
	items = get_series_from_url(url);
	set_series(items)	
	set_headline("Serier");
	show_series_view();
	focus_series_view();
	
def get_categories(id = None):
	clear();
	set_headline("Kategorier");
	if(id != None):
		categories = get_categories_from_url('http://r7.tv2.dk/api/sputnik/categories/'+str(id)+'.json');
		if(len(categories)>0):
			set_categories(categories);
			show_categories_view();
			focus_categories_view();
		# Look for child programs and series
		
		series = get_series_from_url('http://r7-dyn.tv2.dk/api/sputnik/categories/'+str(id)+'/series.json');
		if(len(series)>0):
			set_series(series);
			if(len(categories)<1):
				show_series_view();
				focus_series_view();
				
		items = get_programs_from_url('http://r7.tv2.dk/api/sputnik/categories/'+str(id)+'/programs/sort-latest/page-1.json');
		if(len(items)>0):
			set_items(items);
			if(len(categories)<1 and len(series)<1):
				show_programs_view();
				focus_programs_view();
	else:
		categories = get_categories_from_url('http://r7.tv2.dk/api/sputnik/categories.json');
		set_categories(categories);
		show_categories_view();
		focus_categories_view();
	
def get_broadcasts():
	clear();
	items = get_broadcasts_from_url('http://r7-dyn.tv2.dk/api/sputnik/placeholder/687/content.json');
	set_items(items);
	show_programs_view();
	focus_programs_view();
	set_headline("Live TV");
		
def search():
	search = mc.ShowDialogKeyboard("Søg på sputnik.dk", "", False);
	if(search and len(search)>=3):
		get_search(search)
		set_headline("Søgning: " + search);
	else:
		dialog = xbmcgui.Dialog()
		dialog.ok('For kort!', 'Minimum 3 karakterer i søgordet')
	
def get_search(term):
	mc.ShowDialogWait()
	clear();
	hasResult = False;
	hasSeriesResult = False;
		
	socket = urllib2.urlopen("http://r7.tv2.dk/api/sputnik/search.json?query=" + urllib.quote(term))
	result = socket.read()
	socket.close()
	if ( result ):
		listitems = mc.ListItems();
		seriesItems = mc.ListItems();
		resultObj = json.loads(result);
		for program in resultObj['programs']:
			item = get_item_from_program(program)
			listitems.append(item)
			hasResult = True;
		if(len(listitems)>0):
			set_items(listitems);
		for ser in resultObj['series']:
			item = get_item_from_series(ser)
			newLabel = str(item.GetLabel())
			item.SetLabel(newLabel);
			seriesItems.append(item);
			hasResult = True;
			hasSeriesResult = True;
		if(len(seriesItems)>0):
			set_series(seriesItems);
		if not hasResult:
			mc.ShowDialogOk("Søg", "Ingen resultater for: " + term);
		else:
			if hasSeriesResult:
				show_series_view();
				focus_series_view();
			else:
				show_programs_view();
				focus_programs_view();
	mc.HideDialogWait()
	
def get_series_from_url(url, list = None):
	mc.ShowDialogWait()
	if(list == None):
		list = mc.ListItems();

	http = mc.Http()
	result = http.Get(url)
	if ( result ):
		resultObj = json.loads(result);
		for ser in resultObj['series']:
			item = get_item_from_series(ser)
			list.append(item)
	mc.HideDialogWait()
	return list
	
def get_broadcasts_from_url(url):
	mc.ShowDialogWait()
	list = mc.ListItems();
	
	http = mc.Http()
	result = http.Get(url)
	if ( result ):
		resultObj = json.loads(result);
		for broadcast in resultObj['entities']:
			item = get_item_from_program(broadcast)
			list.append(item)
	
	mc.HideDialogWait()
	return list	
	
def get_categories_from_url(url):
	mc.ShowDialogWait()
	categories = mc.ListItems();
	
	http = mc.Http()
	result = http.Get(url)
	if ( result ):
		resultObj = json.loads(result);
		if('categories' in resultObj):
			for cat in resultObj['categories']:
				item = get_item_from_category(cat);
				categories.append(item);
		elif('children' in resultObj):
			set_headline(unicode(resultObj['code']).encode('utf-8'));
			for cat in resultObj['children']:
				item = get_item_from_category(cat);
				categories.append(item);

	mc.HideDialogWait()
	return categories;
	
#API
def get_item_from_program(program):
	item = mc.ListItem( mc.ListItem.MEDIA_VIDEO_EPISODE )
	item.SetLabel(unicode(program['title']).encode("utf-8"))
	item.SetDescription(unicode(program['description']).encode("utf-8"))
	thumb = get_image_from_program(program)
	if(thumb != None):
		item.SetThumbnail(thumb)
	try:
		if('series' in program and program['series'] != None):
			item.SetTVShowTitle(unicode(program['series']['code']).encode('utf-8'))
	except Exception, e:
		item.SetTVShowTitle("")
	if('season' in program and program['season'] != None):
		item.SetSeason(int(program['season']['title']))
	else:
		item.SetSeason(0)		
	if('epsiode' in program and program['episode'] != None):
		item.SetEpisode(int(program['episode']))
	else:
		item.SetEpisode(0)		
	if('category' in program):
		item.SetGenre(unicode(program['category']['code']).encode('utf-8'))
	path = get_path_from_program(program)
	item.SetPath(path)
	item.SetProperty("id", str(program['id']))
	
	item.SetProperty('nocharge', "0");
	if('nocharge' in program and program['nocharge']):
		item.SetProperty('nocharge', "1");
	
	if('r7_type' in program):
		if(program['r7_type'] == "R7_Entity_Broadcast"):
			item.SetProperty("action", "broadcast");
		else:
			item.SetProperty("action", "program");		
	else:
		item.SetProperty("action", "program");
	return item

def get_item_from_series(series):
	item = mc.ListItem( mc.ListItem.MEDIA_UNKNOWN )
	item.SetLabel(unicode(series['code']).encode("utf-8"))
	item.SetDescription(unicode(series['description']).encode("utf-8"))
	thumb = get_image_from_program(series)
	mc.LogDebug(thumb);
	if(thumb != None):
		item.SetThumbnail(thumb)
	item.SetProperty("id", str(series['id']))
	item.SetProperty("action", "series")
	return item
	
def get_item_from_category(category):
	item = mc.ListItem( mc.ListItem.MEDIA_UNKNOWN )
	if(category['title'] != None):
		item.SetLabel(unicode(category['title']).encode("utf-8"));
	else:
		item.SetLabel(unicode(category['code']).encode("utf-8"));	
	if(category['description'] != None):
		item.SetDescription(unicode(category['description']).encode("utf-8"))
	item.SetProperty("id", str(category['id']));
	item.SetProperty("action", "category");

	return item;
	
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

def get_background(json):
	if('media_images' in json and json['media_images'] != None):
		for image in json['media_images']:
			if(str(image['media_image_type']['code']) == 'bg'):
				for file in image['media_image_files']:
					return str(file['location_uri'])
	return "http://sputnik-dyn.tv2.dk/css/gfx/backgrounds/generic/bluecircles_cedeea.jpg"

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

def play_program(listitem, type = "program"):
	programid = listitem.GetProperty("id");
	nocharge = listitem.GetProperty('nocharge');
	dp = xbmcgui.DialogProgress()
	dialog = xbmcgui.Dialog()

	path = listitem.GetPath();
		
	username = xbmc.getInfoLabel('App.String(username)')
	password = xbmc.getInfoLabel('App.String(password)')
		
	try:
		if (nocharge != "1"):
			if(username == ""):
				raise Exception("Du er ikke logget ind!");				
			if not (login_user(username, password)):
				raise Exception("Kunne ikke logge dig ind!");
			if not (login_user(username, password)):
				raise Exception("Kunne ikke logge dig ind!");
		newpath = str('flash://sputnik.dk/src=' + urllib.quote_plus("http://sputnik-dyn.tv2.dk/player/simple/id/"+programid+"/type/"+type+"/") + '&bx-ourl=' + urllib.quote_plus(path) + '&bx-jsactions=' + urllib.quote_plus('http://dl.dropbox.com/u/93155/boxee/controls.js'))
		listitem.SetPath(newpath)
		mc.GetPlayer().PlayWithActionMenu(listitem)
		listitem.SetPath(path)
			
	except Exception, e:
		dialog.ok('Error', str(e))
		dp.close()
			
def get_programs_from_url(url, list = None):
	mc.ShowDialogWait()
	if(list == None):
		list = mc.ListItems();
	
	socket = urllib2.urlopen(url)
	result = socket.read()
	socket.close()
	if ( result ):
		resultObj = json.loads(result);
		for program in resultObj['programs']:
			item = get_item_from_program(program)
			list.append(item)
				
	mc.HideDialogWait()
	return list


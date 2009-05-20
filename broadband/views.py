import gdata.spreadsheet.service, pycountry, operator
from django.conf import settings
from django.shortcuts import render_to_response

def map(request):
  """show a map of broadband enabled countries"""
  # create google data client and authenticate it
  gd_client = gdata.spreadsheet.service.SpreadsheetsService()
  gd_client.email = settings.GOOGLE_USERNAME
  gd_client.password = settings.GOOGLE_PASSWORD
  gd_client.source = 'markng-hacks-v0'
  gd_client.ProgrammaticLogin()
  # set the key and worksheet id to retrieve from google
  curr_key = 'rdhWg2r1TzRwTuVR5mee1DQ'
  curr_wksht_id = 'od6'
  # the listfeed is the most useful way of getting at data in the gdata spreadsheets API
  listfeed = gd_client.GetListFeed(curr_key, curr_wksht_id)
  data = {}
  # in this particular dataset, there were a couple of lines we needed to ignore
  ignore = ['OECD', 'SOURCE', 'DATALINK']
  for entry in listfeed.entry:
    try:
      if entry.custom['country'].text not in ignore:
        # we're using pycountry to change the country text into the alpha2 codes gcharts needs
        alpha2 = pycountry.countries.get(name=entry.custom['country'].text).alpha2
        # and rounding the data due to the requirements of gcharts
        rounded = int(round(float(entry.custom['broadbandpenetrationsubscribersper100inhabitantsdec2008'].text)))
        # for this particular dataset, I've applied a scaling factor of 2, so that colours show up properly
        data[alpha2] = rounded * 2
    except KeyError, e:
      if settings.DEBUG == True:
        # a couple of countries in this dataset weren't in the pycountry lookup table with that name
        print '%s missing from countries dictionary' % (e)
  # put the countries and values into a format gcharts can understand
  countries = reduce(operator.add, data.keys())
  values = reduce(lambda x, y: str(x) + ',' + str(y), data.values())
  # build the urls
  url = 'http://chart.apis.google.com/'
  url += 'chart?cht=t&chs=440x220&chco=CCCCCC,0000FF,00FF00,FF0000'
  url += '&chf=bg,s,EAF7FE&chld=%s&chd=t:%s' % (countries, values)
  europeurl = url + "&chtm=europe"
  worldurl = url + "&chtm=world"
  # and send them to the template
  c = { 
    'europeurl' : europeurl,
    'worldurl' : worldurl,
  }
  return render_to_response('broadband/map.html', c)
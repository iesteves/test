from collections import defaultdict

class Urlstats:
	def __init__(self):
		self.Called = 0
		self.Totalresponsetime = 0
		self.Median = []
		self.Mode = defaultdict(int)
		self.dyno = defaultdict(int)
	def update(self, a):
		self.Called += 1
		Connect = int( a[8].split( "=" )[1][:-2] )
		Service = int( a[9].split( "=" )[1][:-2] )
		Response = Connect + Service
		self.Totalresponsetime += Response
		self.Median.append( Response )
		self.Mode[Response] += 1
		dyno = a[7].split( "=" )[1]
		self.dyno[dyno] += 1

def median(a):
	b = sorted(a)
	n = len(b)
	if n % 2 == 0:
		return ( b[n / 2] + b[n / 2 - 1] ) / 2.0
	return b[n / 2]

if __name__ == "__main__":
	import sys
	import re
	
	Urlre1 = re.compile( r"^path=/api/users/[^/]+/(count_pending_messages|get_messages|get_friends_progress|get_friends_score)$" )
	Urlre2 = re.compile( r"^path=/api/users/[^/]+$" )

	with open( sys.argv[1], 'r') as f:
		Url = defaultdict(Urlstats)
		for Line in f:
			a = Line.split()
			Match = Urlre1.search( a[4] )
			if Match is not None and a[3] == "method=GET":
				Key = "GET /api/users/{{user_id}}/{}".format( Match.group(1) )
				Url[Key].update( a )
			else:
				Match = Urlre2.search( a[4] )
				if Match is not None:
					if a[3] == "method=GET":
						Key = "GET /api/users/{user_id}"
						Url[Key].update( a )
					elif a[3] == "method=POST":
						Key = "POST /api/users/{user_id}"
						Url[Key].update( a )
				
		for _Url, Stats in Url.iteritems():
			Mode = sorted(Stats.Mode, key=Stats.Mode.__getitem__, reverse=True )[0]
			dyno = sorted(Stats.dyno, key=Stats.dyno.__getitem__, reverse=True )[0]
			print "{} {} {:.1f} {} {} {}".format( _Url, Stats.Called, float( Stats.Totalresponsetime )/
				Stats.Called, median( Stats.Median ), Mode, dyno )

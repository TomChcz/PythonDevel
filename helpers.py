# helper functions for main app


# converts seconds into d, h, m, s

def convert_duration(duration):
	m, s = divmod(duration, 60)
	h, m = divmod(m, 60)
	d, h = divmod(h, 24)

	def addzero(x):

		if int(x) < 10: # add leading zero
			returnval = '0' + str(int(x))
		else:
			returnval = str(int(x))

		return returnval

	
	duration_formatted = '{}:{}:{}'.format(addzero(h), addzero(m), addzero(s))

	return duration_formatted



def getfield(field):
	pass

def getlist(field):
	pass
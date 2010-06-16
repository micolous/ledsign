#!/usr/bin/env python
import commands
import re

def snmpgetout(host, domain, oid, range, typemask=None):
	result = {}
	for interface in range:
		res = commands.getoutput("snmpget -v 1 -c %s %s .%s.%s" % (domain,host,oid,interface))
		res = res.split(" = ")[1]
		res = res.split(": ")
		if not typemask or res[0] == typemask:
			try:
				res[1] = int(res[1])
			except:
				pass
			result[interface] = res[1]
	return result

if __name__ == "__main__":
	print snmpgetout("10.7.0.2", "public", "1.3.6.1.2.1.2.2.1.16", range(1,26), 'Counter32')

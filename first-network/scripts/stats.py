import sys
import os
import time
import subprocess


if len(sys.argv)!= 2:
	print("Usage: {} <peer_name>".format(__file__))
	raise SystemExit


srvcName = sys.argv[1]

def getContainerId(service):
	# node ID
	p = subprocess.Popen(["docker service ps --format '{{{{.Node}}}}' --no-resolve {srvc}".format(srvc=service)], shell=True, stdout=subprocess.PIPE)
	srvc_id, _ = p.communicate()

	# node IP
	p = subprocess.Popen(["docker node inspect --format '{{{{.Status.Addr}}}}' {srvc}".format(srvc=srvc_id.strip())], shell=True, stdout=subprocess.PIPE)
	srvc_ip, _ = p.communicate()

	# container ID
	p = subprocess.Popen(["ssh ubuntu@{ip} \"docker container ls --format '{{{{.ID}}}} {{{{.Names}}}}'\" | grep {srvc}".format(ip=srvc_ip.strip(), srvc=service)], shell=True, stdout=subprocess.PIPE)
	cnts, _ = p.communicate()

	cnts = cnts.strip()
	cntId, _ = cnts.split()

	return cntId

def getStats(srvcIp, cntId):
	while True:
		p = subprocess.Popen()
		p.communicate()

cntId = getContainerId(srvcName)


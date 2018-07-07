import sys
import os
import time
import subprocess


if len(sys.argv)!= 2:
	print("Usage: {} <peer_name>".format(__file__))
	raise SystemExit


srvcName = sys.argv[1]

def getContainerPid(service):
	# node ID
    cmd = "docker service ps -f '{{{{.Node}}}}' --no-resolve {srvc}".format(srvc=service)
	p = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
	srvcId, _ = p.communicate()

	# node IP
    cmd = "docker node inspect -f '{{{{.Status.Addr}}}}' {srvc}".format(srvc=srvcId.strip())
	p = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
	srvcIp, _ = p.communicate()

	# container ID
    cmd = "ssh ubuntu@{ip} \"docker container ls -f '{{{{.ID}}}} {{{{.Names}}}}'\" | grep {srvc}".format(ip=srvcIp.strip(), srvc=service)
	p = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
	cnts, _ = p.communicate()
	cnts = cnts.strip()
	cntId, _ = cnts.split()

    # container PID
    cmd = "ssh ubuntu@{ip} \"docker inspect -f {{{{.State.Pid}}}} {cnt}\"".format(cnt=cntId)
    p = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
    cntPid, _ = p.communicate()

	return srvcIp, cntPid

def getStats(srvcIp, cntPid):
	while True:
        cmd = "ssh ubuntu@{ip} \"cat /proc/{cnt}/net/dev\"".format(ip=srvcIp, cnt=cndPid)
		p = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
		netIo, _ = p.communicate()

        print(netIo)

srvcIp, cntPid = getContainerPid(srvcName)



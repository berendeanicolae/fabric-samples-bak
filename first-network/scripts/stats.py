import sys
import os
import time
import subprocess


if len(sys.argv)!= 2:
	print("Usage: {} <peer_name>".format(__file__))
	raise SystemExit


sys.stdout = os.fdopen(sys.stdout.fileno(), "wb", 0)
sys.stderr = os.fdopen(sys.stderr.fileno(), "wb", 0)

srvcName = sys.argv[1]

def getContainerPid(service):
	# node ID
	cmd = "docker service ps --format '{{{{.Node}}}}' --no-resolve {srvc}".format(srvc=service)
	p = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
	srvcId, _ = p.communicate()

	# node IP
	cmd = "docker node inspect --format '{{{{.Status.Addr}}}}' {srvc}".format(srvc=srvcId.strip())
	p = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
	srvcIp, _ = p.communicate()

	# container ID
	cmd = "ssh ubuntu@{ip} \"docker container ls --format '{{{{.ID}}}} {{{{.Names}}}}'\" | grep {srvc}".format(ip=srvcIp.strip(), srvc=service)
	p = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
	cnts, _ = p.communicate()
	cnts = cnts.strip()
	cntId, _ = cnts.split()

    # container PID
	cmd = "ssh ubuntu@{ip} \"docker inspect --format {{{{.State.Pid}}}} {cnt}\"".format(ip=srvcIp.strip(), cnt=cntId)
	p = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
	cntPid, _ = p.communicate()

	return srvcIp.strip(), cntPid.strip()

def getStats(srvcIp, cntPid):
	idx = 0
	while True:
		cmd = "ssh ubuntu@{ip} \"cat /proc/{cnt}/net/dev\"".format(ip=srvcIp, cnt=cntPid)
		p = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
		netIo, _ = p.communicate()

		netIn = 0
		netOut = 0
		idx += 1
		for net in netIo.splitlines()[2:]:
			net = net.strip()
			if len(net) == 0: continue

			netIn += int(net.split()[1])
			netOut += int(net.split()[9])
		print("#{}: {}\t{}".format(idx, netIn, netOut))
		time.sleep(10)

srvcIp, cntPid = getContainerPid(srvcName)
getStats(srvcIp, cntPid)


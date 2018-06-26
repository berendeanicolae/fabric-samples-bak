import sys
import os
import subprocess


if len(sys.argv) != 2:
    print("Usage: {} <peer_count>".format(os.path.basename(__file__)))
    raise SystemExit


peer_count = int(sys.argv[1])

# generate crypto-config.yaml
template = '''
OrdererOrgs:
  - Name: Orderer
    Domain: example.com
    Specs:
      - Hostname: orderer
PeerOrgs:
  - Name: Org1
    Domain: org1.example.com
    EnableNodeOUs: true
    Template:
      Count: 10
    Users:
      Count: 1
  - Name: Org2
    Domain: org2.example.com
    EnableNodeOUs: true
    Template:
      Count: 2
    Users:
      Count: 1
  '''
fHandle = open("crypto-config.yaml", "w")
fHandle.write(template)
fHandle.close()


# generate crypto-config

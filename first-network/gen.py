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
  '''.format(peer_count)
fHandle = open("crypto-config_2.yaml", "w")
fHandle.write(template)
fHandle.close()


# generate crypto-config
p = subprocess.Popen(["./byfn.sh generate"], stdin=subprocess.PIPE, shell=True)
p.communicate(input="y")
p.wait()

# generate docker-compose-cli.yaml
peer_template = '''
  peer{cnt}_org1:
    hostname: peer{cnt}.org1.example.com
    image: hyperledger/fabric-peer:latest
    environment:
        - CORE_PEER_ID=peer{cnt}.org1.example.com
        - CORE_PEER_ADDRESS=peer{cnt}.org1.example.com:7051
        - CORE_PEER_GOSSIP_EXTERNALENDPOINT=peer{cnt}.org1.example.com:7051
        - CORE_PEER_GOSSIP_BOOTSTRAP=peer0.org1.example.com:7051
        - CORE_PEER_LOCALMSPID=Org1MSP
        - CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock
        # the following setting starts chaincode containers on the same
        # bridge network as the peers
        # https://docs.docker.com/compose/networking/
        - CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=hyperledger-ov
        - CORE_LOGGING_LEVEL=INFO
        # - CORE_LOGGING_LEVEL=DEBUG
        - CORE_PEER_TLS_ENABLED=true
        - CORE_PEER_GOSSIP_USELEADERELECTION=true
        - CORE_PEER_GOSSIP_ORGLEADER=false
        - CORE_PEER_PROFILE_ENABLED=true
        - CORE_PEER_TLS_CERT_FILE=/etc/hyperledger/fabric/tls/server.crt
        - CORE_PEER_TLS_KEY_FILE=/etc/hyperledger/fabric/tls/server.key
        - CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/fabric/tls/ca.crt
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric/peer
    command: peer node start
    volumes:
        - /var/run/:/host/var/run/
        - ./crypto-config/peerOrganizations/org1.example.com/peers/peer{cnt}.org1.example.com/msp:/etc/hyperledger/fabric/msp
        - ./crypto-config/peerOrganizations/org1.example.com/peers/peer{cnt}.org1.example.com/tls:/etc/hyperledger/fabric/tls
    networks:
      hyperledger-ov:
        aliases:
            - peer{cnt}.org1.example.com

'''
template = '''
version: '3'

networks:
  hyperledger-ov:
      external: true

services:
  orderer:
    hostname: orderer.example.com
    image: hyperledger/fabric-orderer:latest
    environment:
      - ORDERER_GENERAL_LOGLEVEL=INFO
      - ORDERER_GENERAL_LISTENADDRESS=0.0.0.0
      - ORDERER_GENERAL_GENESISMETHOD=file
      - ORDERER_GENERAL_GENESISFILE=/var/hyperledger/orderer/orderer.genesis.block
      - ORDERER_GENERAL_LOCALMSPID=OrdererMSP
      - ORDERER_GENERAL_LOCALMSPDIR=/var/hyperledger/orderer/msp
      # enabled TLS
      - ORDERER_GENERAL_TLS_ENABLED=true
      - ORDERER_GENERAL_TLS_PRIVATEKEY=/var/hyperledger/orderer/tls/server.key
      - ORDERER_GENERAL_TLS_CERTIFICATE=/var/hyperledger/orderer/tls/server.crt
      - ORDERER_GENERAL_TLS_ROOTCAS=[/var/hyperledger/orderer/tls/ca.crt]
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric
    command: orderer
    volumes:
    - ./channel-artifacts/genesis.block:/var/hyperledger/orderer/orderer.genesis.block
    - ./crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/msp:/var/hyperledger/orderer/msp
    - ./crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/tls/:/var/hyperledger/orderer/tls
    networks:
      hyperledger-ov:
        aliases:
            - orderer.example.com

  peer0_org1:
    hostname: peer0.org1.example.com
    image: hyperledger/fabric-peer:latest
    environment:
        - CORE_PEER_ID=peer0.org1.example.com
        - CORE_PEER_ADDRESS=peer0.org1.example.com:7051
        - CORE_PEER_GOSSIP_BOOTSTRAP=peer1.org1.example.com:7051
        - CORE_PEER_GOSSIP_EXTERNALENDPOINT=peer0.org1.example.com:7051
        - CORE_PEER_LOCALMSPID=Org1MSP
        - CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock
        # the following setting starts chaincode containers on the same
        # bridge network as the peers
        # https://docs.docker.com/compose/networking/
        - CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=hyperledger-ov
        - CORE_LOGGING_LEVEL=INFO
        # - CORE_LOGGING_LEVEL=DEBUG
        - CORE_PEER_TLS_ENABLED=true
        - CORE_PEER_GOSSIP_USELEADERELECTION=true
        - CORE_PEER_GOSSIP_ORGLEADER=false
        - CORE_PEER_PROFILE_ENABLED=true
        - CORE_PEER_TLS_CERT_FILE=/etc/hyperledger/fabric/tls/server.crt
        - CORE_PEER_TLS_KEY_FILE=/etc/hyperledger/fabric/tls/server.key
        - CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/fabric/tls/ca.crt
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric/peer
    command: peer node start
    volumes:
        - /var/run/:/host/var/run/
        - ./crypto-config/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/msp:/etc/hyperledger/fabric/msp
        - ./crypto-config/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls:/etc/hyperledger/fabric/tls
    networks:
      hyperledger-ov:
        aliases:
            - peer0.org1.example.com

{}

  peer0_org2:
    hostname: peer0.org2.example.com
    image: hyperledger/fabric-peer:latest
    environment:
        - CORE_PEER_ID=peer0.org2.example.com
        - CORE_PEER_ADDRESS=peer0.org2.example.com:7051
        - CORE_PEER_GOSSIP_EXTERNALENDPOINT=peer0.org2.example.com:7051
        - CORE_PEER_GOSSIP_BOOTSTRAP=peer1.org2.example.com:7051
        - CORE_PEER_LOCALMSPID=Org2MSP
        - CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock
        # the following setting starts chaincode containers on the same
        # bridge network as the peers
        # https://docs.docker.com/compose/networking/
        - CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=hyperledger-ov
        - CORE_LOGGING_LEVEL=INFO
        # - CORE_LOGGING_LEVEL=DEBUG
        - CORE_PEER_TLS_ENABLED=true
        - CORE_PEER_GOSSIP_USELEADERELECTION=true
        - CORE_PEER_GOSSIP_ORGLEADER=false
        - CORE_PEER_PROFILE_ENABLED=true
        - CORE_PEER_TLS_CERT_FILE=/etc/hyperledger/fabric/tls/server.crt
        - CORE_PEER_TLS_KEY_FILE=/etc/hyperledger/fabric/tls/server.key
        - CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/fabric/tls/ca.crt
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric/peer
    command: peer node start
    volumes:
        - /var/run/:/host/var/run/
        - ./crypto-config/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/msp:/etc/hyperledger/fabric/msp
        - ./crypto-config/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls:/etc/hyperledger/fabric/tls
    networks:
      hyperledger-ov:
        aliases:
            - peer0.org2.example.com

  peer1_org2:
    hostname: peer1.org2.example.com
    image: hyperledger/fabric-peer:latest
    environment:
        - CORE_PEER_ID=peer1.org2.example.com
        - CORE_PEER_ADDRESS=peer1.org2.example.com:7051
        - CORE_PEER_GOSSIP_EXTERNALENDPOINT=peer1.org2.example.com:7051
        - CORE_PEER_GOSSIP_BOOTSTRAP=peer0.org2.example.com:7051
        - CORE_PEER_LOCALMSPID=Org2MSP
        - CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock
        # the following setting starts chaincode containers on the same
        # bridge network as the peers
        # https://docs.docker.com/compose/networking/
        - CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=hyperledger-ov
        - CORE_LOGGING_LEVEL=INFO
        # - CORE_LOGGING_LEVEL=DEBUG
        - CORE_PEER_TLS_ENABLED=true
        - CORE_PEER_GOSSIP_USELEADERELECTION=true
        - CORE_PEER_GOSSIP_ORGLEADER=false
        - CORE_PEER_PROFILE_ENABLED=true
        - CORE_PEER_TLS_CERT_FILE=/etc/hyperledger/fabric/tls/server.crt
        - CORE_PEER_TLS_KEY_FILE=/etc/hyperledger/fabric/tls/server.key
        - CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/fabric/tls/ca.crt
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric/peer
    command: peer node start
    volumes:
        - /var/run/:/host/var/run/
        - ./crypto-config/peerOrganizations/org2.example.com/peers/peer1.org2.example.com/msp:/etc/hyperledger/fabric/msp
        - ./crypto-config/peerOrganizations/org2.example.com/peers/peer1.org2.example.com/tls:/etc/hyperledger/fabric/tls
    networks:
      hyperledger-ov:
        aliases:
            - peer1.org2.example.com

  cli:
    image: hyperledger/fabric-tools:latest
    environment:
      - GOPATH=/opt/gopath
      - CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock
      - CORE_LOGGING_LEVEL=DEBUG
      # - CORE_LOGGING_LEVEL=INFO
      - CORE_PEER_ID=cli
      - CORE_PEER_ADDRESS=peer0.org1.example.com:7051
      - CORE_PEER_LOCALMSPID=Org1MSP
      - CORE_PEER_TLS_ENABLED=true
      - CORE_PEER_TLS_CERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/server.crt
      - CORE_PEER_TLS_KEY_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/server.key
      - CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
      - CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric/peer
    command: sleep 1d
    volumes:
        - /var/run/:/host/var/run/
        - ./../chaincode/:/opt/gopath/src/github.com/chaincode
        - ./crypto-config:/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/
        - ./scripts:/opt/gopath/src/github.com/hyperledger/fabric/peer/scripts/
        - ./channel-artifacts:/opt/gopath/src/github.com/hyperledger/fabric/peer/channel-artifacts
    networks:
      hyperledger-ov:
        aliases:
            - cli

'''
peers = "\n".join([peer_template.format(cnt=i) for i in range(1, peer_count)])
fHandle = open("docker-compose-cli_2.yaml", "w")
fHandle.write(template.format(peers))
fHandle.close()

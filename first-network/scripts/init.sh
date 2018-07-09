

ORDERER_CA=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem

. scripts/utils.sh

createChannel() {
	setGlobals 0 1

    peer channel create -o orderer.example.com:7050 -c $CHANNEL_NAME -f ./channel-artifacts/channel.tx --tls --cafile $ORDERER_CA
}

joinChannel() {
    for peer in 0 1; do
        setGlobals $peer 2
		peer channel join -b $CHANNEL_NAME.block
    done

    for peer in $(seq 0 99); do
        setGlobals $peer 1
		peer channel join -b $CHANNEL_NAME.block
    done
}


updateAnchorPeers() {
    for org in 1 2; do
        setGlobals 0 $org
        peer channel update -o orderer.example.com:7050 -c $CHANNEL_NAME -f ./channel-artifacts/${CORE_PEER_LOCALMSPID}anchors.tx --tls $CORE_PEER_TLS_ENABLED --cafile $ORDERER_CA >&log.txt
    done
}


installChaincode() {
    for peer in 0 1; do
        setGlobals $peer 2
		peer chaincode install -n mycc -v 1.0 -p github.com/chaincode/chaincode_example02/go/
    done

    for peer in $(seq 0 99); do
        setGlobals $peer 1
		peer chaincode install -n mycc -v 1.0 -p github.com/chaincode/chaincode_example02/go/
    done
}

instantiateChaincode() {
    setGlobals 0 1
    peer chaincode instantiate -o orderer.example.com:7050 --tls --cafile $ORDERER_CA -C $CHANNEL_NAME -n mycc -l node -v 1.0 -c '{"Args":["init","a", "100", "b","200"]}' -P "AND ('Org1MSP.peer','Org2MSP.peer')"
}

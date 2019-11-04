#!/usr/bin/env bash

tidbLatestURL="http://fileserver.pingcap.net/download/builds/pingcap/release/tidb-latest-linux-amd64.tar.gz"
echo $tidbLatestURL
tidbCommitURL="curl -SLO http://fileserver.pingcap.net/download/builds/pingcap/tidb/$1/centos7/tidb-server.tar.gz"
echo $tidbCommitURL

tidbCommitDir="tidb-$1"
tidbLatestDir="tidb-latest-linux-amd64"
tidbCommitTar="tidb-$1-linux-amd64"

rm -rf $tidbLatestDir
rm -rf *.tar.gz
rm -rf $tidbCommitDir

mkdir $tidbCommitDir

curl $tidbLatestURL | tar xvz
curl $tidbCommitURL | tar xvz -C $tidbCommitDir

ls ${tidbLatestDir}/bin | grep -v "server" | xargs -I {} rm -rf ${tidbLatestDir}/bin/{}
cp ${tidbCommitDir}/bin/tidb-server ${tidbLatestDir}/bin
mv $tidbLatestDir $tidbCommitTar

tarFile=${tidbCommitTar}.tar.gz

tar -zcvf $tarFile $tidbCommitTar

curl -F  builds/pingcap/release/$tarFile=@$tarFile http://fileserver.pingcap.net/upload

echo "http://fileserver.pingcap.net/download/builds/pingcap/release/$tarFile"

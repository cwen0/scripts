#!/usr/bin/python 

import urllib2
import argparse 
import json

token = ""

def get_hash_by_tag(repo, tag):
    urlstr = "https://api.github.com/repos/pingcap/" + repo + "/git/refs/tags/" + tag
    if repo == "tikv":
        urlstr = "https://api.github.com/repos/tikv/" + repo + "/git/refs/tags/" + tag

    req = urllib2.Request(urlstr)
    req.add_header('Authorization', 'token %s' % token)
    response = urllib2.urlopen(req)
    data = json.load(response)   
    if data["object"]["type"] == "commit":
        return data["object"]["sha"].strip()

    req2 = urllib2.Request(data["object"]["url"])
    req2.add_header('Authorization', 'token %s' % token)
    response2 = urllib2.urlopen(req2)
    tag_data = json.load(response2)

    return tag_data["object"]["sha"].strip()


def get_hash_by_branch(repo, branch, fileserver):
    urlstr = fileserver + "/download/refs/pingcap/" + repo + "/" + branch + "/sha1"

    req = urllib2.Request(urlstr)
    req.add_header('Authorization', 'token %s' % token)
    response = urllib2.urlopen(req)
    return response.read().strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-repo", type=str, help="github repo")
    parser.add_argument("-version", type=str, help="github repo")
    parser.add_argument("-s", type=str, help="file server url", default='')

    args = parser.parse_args()

    if args.version[0] == 'v':
        print get_hash_by_tag(args.repo, args.version)
    else:
        print get_hash_by_branch(args.repo, args.version, args.s)

if __name__ == "__main__":
    main()

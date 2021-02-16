import requests, json, yaml, sys, os, threading, argparse, signal

import deefuzzer
import pydub

import fuzzgen

parser = argparse.ArgumentParser(description="Multithreaded Python fuzzer for Icecast server metadata.")

parser.add_argument("config", nargs=1, type=str, help="input configuration YAML file")
parser.add_argument("--generator", "-g", nargs=1, type=str, default="symbolFuzz", dest="fuzzgenerator", help="generator function for fuzzed data to send. define fuzz data generator functions in fuzzgen.py and provide them as arguments here")
parser.add_argument("--silence", action="store_true", help="generate silent signal mp3 in config-provided inputs directory to broadcast while fuzzing")

args = parser.parse_args()

config = (yaml.load(open(args.config[0])))['deefuzzer']['station']
inputs_dir = config['media']['source']
host = config['server']['host']
port = config['server']['port']
mount = config['server']['mountpoint']
password = config['server']['sourcepassword']

if args.silence:
    # create empty 10-second MP3 in order to persist connection
    if os.path.exists(inputs_dir) and not os.path.exists("%s/signal.mp3" % inputs_dir):
        pydub.AudioSegment.silent(duration=10000).export("%s/signal.mp3" % inputs_dir, format="mp3")

stream = deefuzzer.DeeFuzzer("serverconfig.yaml")
stream.start()

fg = fuzzgen.Generator()

while True:
    for (data, printdata) in fg.__getattribute__(args.fuzzgenerator)():
        try:
            requests.get("http://%s:%d/admin/metadata?mount=/%s&mode=updinfo&song=%s" % (host, port, mount, data), auth=("source", password))
            resp = requests.get("http://%s:%s/status-json.xsl" % (host, port)).text
            try:
                json.loads(resp)
            except json.decoder.JSONDecodeError:
                print("json decode error for input %s" % printdata)
        except requests.exceptions.ConnectionError:
            print("server downed on input %s" % data)
            sys.exit(0)

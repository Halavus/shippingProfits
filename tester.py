import json, sys
with open(sys.argv[1]) as f:
    data = json.load(f)

def t(product, cx, data):
    output = data["comex"]["broker"]["brokers"][product+"."+cx]
    return output


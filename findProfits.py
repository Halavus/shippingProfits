import json, csv, operator, math

debug = True

class Filewriter:
    def __init__(self, jsonstring, filepath):
        self.katAsk, self.katBid,
        self.promAsk = -1
        self.promBid = -1
        self.montAsk = -1
        self.montBid = -1

        self.weightOrVol = -1.0

        self.jsonstring = jsonstring
        self.filepath = filepath

    def _jsonparse(self, ticker, label):
        try:
            output = self.jsonstring[ticker][label]
        except (KeyError, ValueError) as e:
            output = None
        return output

    def test(self, teststring, ticker, cx):
        return self.jsonparse(ticker, cx+"."+teststring)

    def _get_row(self, ticker):
        # Get weight/volume
        ''' TODO: IMPLEMENT PROPERLY: make weight module'''
        weight = 1.0
        volume = 1.0

        weightOrVol = -1.0
        if(weight > volume):
            self.weightOrVol = weight
        else:
            self.weightOrVol = volume

        checkdic = {"ticker": ticker}
        # Check if asks/bids exist
        checkdic["cx"] = "CI1"
        try:
            katAsk = float(test("ask", **checkdic))
        except (TypeError, ValueError) as e:
            katAsk = -1

        try:
            katBid = float(test("bid", **checkdic))
        except (TypeError, ValueError) as e:
            katBid = -1

        checkdic["cx"]="IC1"
        try:
            promAsk = float(test("ask", **checkdic))
        except (TypeError, ValueError) as e:
            promAsk = -1
        try:
            promBid = float(test("bid", **checkdic))
        except (TypeError, ValueError) as e:
            promBid = -1

        checkdic["cx"]="NC1"
        try:
            montAsk = float(test("ask", **checkdic))
        except (TypeError, ValueError) as e:
            montAsk = -1
        try:
            montBid = float(test("bid", **checkdic))
        except (TypeError, ValueError) as e:
            montBid = -1

        # bidDest - askSource = sales
        # Determine sales
        # Kat -> Prom
        if(promBid > 0 and katAsk > 0):
            katProm = promBid - katAsk
        else:
            katProm = -1

        # Kat -> Mont
        if(montBid > 0 and katAsk > 0):
            katMont = montBid - katAsk
        else:
            katMont = -1

        # Prom -> Kat
        if(katBid > 0 and promAsk > 0):
            promKat = katBid - promAsk
        else:
            promKat = -1

        # Prom -> Mont
        if(montBid > 0 and promAsk > 0):
            promMont = montBid - promAsk
        else:
            promMont = -1

        # Mont -> Kat
        if(katBid > 0 and montAsk > 0):
            montKat = katBid - montAsk
        else:
            montKat = -1

        # Mont -> Prom
        if(promBid > 0 and montAsk > 0):
            montProm = promBid - montAsk
        else:
            montProm = -1

        # Find max profit
        ''' no use for profitList
        profitList = [
            katProm,
            katMont,
            promKat,
            promMont,
            montKat,
            montProm]
        '''
        profitDict = {
            "Kat -> Prom": katProm,
            "Kat -> Mont": katMont,
            "Prom -> Kat": promKat,
            "Prom -> Mont": promMont,
            "Mont -> Kat": montKat,
            "Mont -> Prom": montProm,
        }

        # Find best route and corresponding profit per unit
        bestRoute = max(profitDict.items(), key=operator.itemgetter(1))[0]
        maxPPU = profitDict.get(bestRoute)

        if debug:
            print("Best route: "+bestRoute+" with ppu: "+str(maxPPU))

        # Figure out where the best buy was
        if(bestRoute.startswith("Kat")):
            bestBuy = katAsk
        elif(bestRoute.startswith("Prom")):
            bestBuy = promAsk
        elif(bestRoute.startswith("Mont")):
            bestBuy = montAsk

        # Write line
        with open(filepath, mode='w', newline='') as ag:
            agWriter = csv.writer(ag, delimiter=',',
                                  quotechar='"',
                                  quoting=csv.QUOTE_MINIMAL)

            agWriter.writerow([ticker,
                               weightOrVol,
                               math.floor(400/weightOrVol),
                               katAsk,
                               katBid,
                               promAsk,
                               promBid,
                               montAsk,
                               montBid,
                               "",
                               katProm,
                               katMont,
                               promKat,
                               promMont,
                               montKat,
                               montProm,
                               "",
                               bestRoute,
                               round(maxPPU*(400/weightOrVol), 2),
                               # Investment
                               round(bestBuy*(400/weightOrVol), 2),
                              ])

    def tablemaker(self):
        with open(self.filepath, mode='w', newline='') as ag:
            agWriter = csv.writer(ag, delimiter=',',
                                  quotechar='"',
                                  quoting=csv.QUOTE_MINIMAL)

            agWriter.writerow(['ticker',
                               'Volume || weight',
                               'Units/ship',
                               'Ask Katoa',
                               'Bid Katoa',
                               'Ask Prom',
                               'Bid Prom',
                               'Ask Montem',
                               'Bid Montem',
                               '',
                               'Kat -> Prom',
                               'Kat -> Montem',
                               'Prom -> Kat',
                               'Prom -> Montem',
                               'Montem -> Kat',
                               'Montem -> Prom',
                               '',
                               'Best route',
                               'Max sales/ship',
                               'Investment',
                              ])

        data = json.load(self.jsonstring)
        for i in data.keys():
            try:
                _get_row(i)
            except (KeyError, ValueError) as e:
                pass

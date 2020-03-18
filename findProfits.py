import json
import csv
from operator import itemgetter
from math import floor

from sizes import sizes

debug = True


class Filewriter:
    def __init__(self, jsonstring, filepath):
        ' "cell" values are added dynamically from _get_row()'

        self.weightOrVol = -1.0

        with open(jsonstring, "r") as f:
            self.jsonstring = json.load(f)

        self.filepath = filepath

    def _jsonparse(self, ticker, label):
        if debug:
            print(ticker)
            print(self.jsonstring[ticker])
        try:
            output = self.jsonstring[ticker][label].replace(",", "")
        except (KeyError, ValueError) as e:
            output = None
        return output

    def _test(self, teststring, ticker, cx):
        return self._jsonparse(ticker, cx+"."+teststring)

    def _get_row(self, ticker):
        # Get weight/volume
        weight = sizes[ticker]["weight"]
        volume = sizes[ticker]["volume"]

        if(weight > volume):
            self.weightOrVol = weight
        else:
            self.weightOrVol = volume

        checkdic = {"ticker": ticker}
        # Check if asks/bids exist
        checkdic["cx"] = "CI1"
        try:
            katAsk = float(self._test("ask", **checkdic))
        except (TypeError, ValueError) as e:
            katAsk = -1

        try:
            katBid = float(self._test("bid", **checkdic))
        except (TypeError, ValueError) as e:
            katBid = -1

        checkdic["cx"] = "IC1"
        try:
            promAsk = float(self._test("ask", **checkdic))
        except (TypeError, ValueError) as e:
            promAsk = -1
        try:
            promBid = float(self._test("bid", **checkdic))
        except (TypeError, ValueError) as e:
            promBid = -1

        checkdic["cx"] = "NC1"
        try:
            montAsk = float(self._test("ask", **checkdic))
        except (TypeError, ValueError) as e:
            montAsk = -1
        try:
            montBid = float(self._test("bid", **checkdic))
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
        profitDict = {
            "Kat -> Prom": katProm,
            "Kat -> Mont": katMont,
            "Prom -> Kat": promKat,
            "Prom -> Mont": promMont,
            "Mont -> Kat": montKat,
            "Mont -> Prom": montProm,
        }

        # Find best route and corresponding profit per unit
        bestRoute = max(profitDict.items(), key=itemgetter(1))[0]
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

        # Set attributes
        attr = {
            "ticker": ticker,
            "katAsk": katAsk,
            "katBid": katBid,
            "promAsk": promAsk,
            "promBid": promBid,
            "montAsk": montAsk,
            "montBid": montBid,
            "katProm": katProm,
            "katMont": katMont,
            "promKat": promKat,
            "promMont": promMont,
            "montKat": montKat,
            "montProm": montProm,
            "bestRoute": bestRoute,
            "bestBuy": bestBuy,
            "maxPPU": maxPPU,
            }

        for i in attr:
            setattr(self, i, attr[i])

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

            data = self.jsonstring
            for i in data.keys():
                try:
                    self._get_row(i)

                    agWriter.writerow([self.ticker,
                                       self.weightOrVol,
                                       floor(400/self.weightOrVol),
                                       self.katAsk,
                                       self.katBid,
                                       self.promAsk,
                                       self.promBid,
                                       self.montAsk,
                                       self.montBid,
                                       "",
                                       self.katProm,
                                       self.katMont,
                                       self.promKat,
                                       self.promMont,
                                       self.montKat,
                                       self.montProm,
                                       "",
                                       self.bestRoute,
                                       round(self.maxPPU*(400/self.weightOrVol), 2),
                                       # Investment
                                       round(self.bestBuy*(400/self.weightOrVol), 2),
                                       ])
                except (KeyError, ValueError) as e:
                    print("Error in _get_row()"+str(e))

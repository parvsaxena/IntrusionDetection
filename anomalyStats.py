import json;

# methods for manipulating the stats of a single period
def newStats():
    stats = {
        'numPackets' : 0
    }
    return stats

# Add one packet to stats
def updateStats(stats, packet):
    stats['numPackets'] += 1

# aggregate stats
class AnomalyStats():
    def __init__(self, n):
        self.avgStats = [newStats() for i in range(n)]
        self.numData = [0 for i in range(n)]

    # add to stats
    def addToAvg(self, index, stats):
        self.numData[index] += 1
        toUpdate = self.avgStats[index]

        # average everything
        for key in toUpdate:
            toUpdate[key] = (toUpdate[key] + stats[key])/self.numData[index]


    def save(self):
        print(json.dumps(self.avgStats))

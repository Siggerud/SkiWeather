class SkiLubrication:
    def __init__(self, temperatures):
        self._temperatures = temperatures
        self._lubricationsDict = {range(-30, -10): "green", range(-10,-2): "blue", range(-2,0): "violet",
                                  range(0,3): "red", range(3, 10): "klister"}

    def getLubricationTip(self):
        lubricationTracker = {}
        for temp in self._temperatures:
            for interval in self._lubricationsDict:
                if temp in interval:
                    color = self._lubricationsDict[interval]
                    if color in lubricationTracker:
                        lubricationTracker[color] += 1
                    else:
                        lubricationTracker[color] = 1
        lubricationTracker = sorted(lubricationTracker.items(), key=lambda x:x[1], reverse=True)

        lubricationPack = []
        for lubrication in lubricationTracker:
            lubricationPack.append(lubrication[0])

        return lubricationPack


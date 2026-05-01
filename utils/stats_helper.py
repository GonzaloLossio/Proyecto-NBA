def calcAverages(games):
        i = len(games)
        if i == 0:
                return {"points" : 0, "assists" :0, "rebounds" : 0}
        return { 
            "points" : round(sum(g["PTS"] for g in games)/i,1), 
            "assists" :round(sum(g["AST"] for g in games)/i,1), 
            "rebounds" : round(sum(g["REB"] for g in games)/i,1)
        }
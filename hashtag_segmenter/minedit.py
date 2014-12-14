# Credit Jim Martin (Univ. of Colorado)

def  minEditDist(target, source):
    ''' Computes the min edit distance from target to source. Assume that
    insertions, deletions and (actual) substitutions all cost 1.'''
    
    n = len(target)
    m = len(source)

    distance = [[0 for i in range(m+1)] for j in range(n+1)]

    for i in range(1,n+1):
        distance[i][0] = distance[i-1][0] + insertCost(target[i-1])

    for j in range(1,m+1):
        distance[0][j] = distance[0][j-1] + deleteCost(source[j-1])

    for i in range(1,n+1):
        for j in range(1,m+1):
            distance[i][j] = min(distance[i-1][j]+insertCost(target[i-1]),
                                 distance[i][j-1]+insertCost(source[j-1]),
                                 distance[i-1][j-1]+substCost(source[j-1],target[i-1]))
    return distance[n][m]

def insertCost(cell):
  return 1

def deleteCost(cell):
  return 1

def substCost(cell, cell2):
  if cell == cell2:
    return 0
  return 2

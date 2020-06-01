import math,random


class Ai:
    def __init__(self,mines,revealed,marked,nums,x_w,y_w,TOT_MINES):
        # game info
        self.mines = mines
        self.revealed = revealed
        self.marked = marked
        self.nums = nums
        self.x_w = x_w
        self.y_w = y_w
        self.TOT_MINES = TOT_MINES

        # for tanksolver
        # current route's danger
        self.knownMine = []
        # current route's safe
        self.knownEmpty = []
        self.BF_LIMIT = 8
        self.tank_solutions = []
        # cache the safe tiles
        self.savedSafes = []
        # cache the dangerous tiles
        self.savedDangers = []

    # pick next target
    def pickNext(self):

        #if there is aready solution in cache

        if(len(self.savedSafes)>0):
            safe = self.savedSafes.pop(0)
            return {"position":{"x":safe[0],"y":safe[1]},"mine":False}
        
        if(len(self.savedDangers)>0):
            danger= self.savedDangers.pop(0)
            return {"position":{"x":danger[0],"y":danger[1]},"mine":True}


        #get the apparent solution from adjacent tiles

        safes = self.getApparentSafes()
        if(len(safes)>0):
            for i in range(1,len(safes),1):
                self.savedSafes.append(safes[i])
            print("click x:"+str(safes[0][0])+",y:"+str(safes[0][1])+" from apparent algorithm.")
            return {"position":{"x":safes[0][0],"y":safes[0][1]},"mine":False}

        dangers = self.getApparentDangers()
        if(len(dangers)>0):
            for i in range(1,len(dangers),1):
                self.savedDangers.append(dangers[i])
            print("mark x:"+str(dangers[0][0])+",y:"+str(dangers[0][1])+" from apparent algorithm.")
            return {"position":{"x":dangers[0][0],"y":dangers[0][1]},"mine":True}
        

        # if no apparent result using tanksolver
        return self.tankSolver()


    def countFreeSquaresAround(self,x,y):
        revealed = self.revealed
        marked = self.marked
        adjacents = self.getAdjacentTiles(x,y)
        freeSquares = 0
        for adjacent in adjacents:
            if(marked[adjacent[0]][adjacent[1]] == False and revealed[adjacent[0][adjacent[1]] == False]):
                freeSquares+=1

        return freeSquares

    
    #tanksolver algorithm 
    def tankSolver(self):
        x_w = self.x_w
        y_w = self.y_w
        revealed = self.revealed
        marked = self.marked
        BF_LIMIT = self.BF_LIMIT

        # border tiles
        borderTiles = []
        # unmarked and unrevealed
        emptyTiles = []

        self.borderOptimization = False

        #current bomb count
        bombNow = 0
        for x in range(x_w):
            for y in range(y_w):
                if(revealed[x][y] == False and marked[x][y] == False):
                    emptyTiles.append([x,y])
                    if(self.isBoundry(x,y)):
                        borderTiles.append([x,y])
                if(marked[x][y]):
                    bombNow +=1

        bombLeft = self.TOT_MINES - bombNow
        numOutSquares = len(emptyTiles) - len(borderTiles)

        if(numOutSquares > BF_LIMIT):
            self.borderOptimization = True
        else:
            borderTiles = emptyTiles

        # patition the tiles for speeding up
        segregated = []
        if(not self.borderOptimization):
            segregated.append(borderTiles)
        else:
            segregated = self.tankSegregate(borderTiles)

        totalMultCases = 1

        # best probablity
        prob_best = 0
        # best tile's index in the segregation
        prob_bsettile = -1
        #index of segregation
        prob_best_s = []

        bombInBorder = 0

        for s in segregated:

            self.knownEmpty = []
            for x in range(x_w):
                self.knownEmpty.append([])
                for y in range(y_w):
                    self.knownEmpty[x].append(revealed[x][y])

            self.knownMine = []
            for x in range(x_w):
                self.knownMine.append([])
                for y in range(y_w):
                    self.knownMine[x].append(marked[x][y])


            self.tank_solutions = []
            self.tankRecurse(s,0)

            # every tile in this segregation
            for i in range(len(s)):
                #all solutions say the tile is mine or safe
                allMine = True
                allEmpty = True
                for sln in self.tank_solutions:
                    if(not sln[i]):
                        allMine = False
                    if(sln[i]):
                        allEmpty = False

                tile = s[i]
                if(allMine):
                    print("mark x:"+str(tile[0])+",y:"+str(tile[1])+" from tanksolver algorithm 100%.")
                    return {"position":{"x":tile[0],"y":tile[1]},"mine":True}
                
                if(allEmpty):
                    # success = True
                    print("click x:"+str(tile[0])+",y:"+str(tile[1])+" from tanksolver algorithm 100%.")
                    return {"position":{"x":tile[0],"y":tile[1]},"mine":False}

            totalMultCases *= len(self.tank_solutions)

                # if(success):
                #     continue

            maxEmpty = -10000
            isEmpty = -1
            for i in range(len(s)):
                nEmpty = 0
                for sln in self.tank_solutions:
                    if(not sln[i]):
                        nEmpty+=1

                bombInBorder += (1-(nEmpty/len(self.tank_solutions)))
                if(nEmpty>maxEmpty):
                    maxEmpty = nEmpty
                    isEmpty = i


            probability = maxEmpty/len(self.tank_solutions)




            if(probability>prob_best):
                prob_best = probability
                prob_bsettile = isEmpty
                prob_best_s = s


        # print(str((len(emptyTiles) -bombLeft)/len(emptyTiles)))
        if(len(prob_best_s)!=0):
            if((numOutSquares-(bombLeft-bombInBorder))/len(emptyTiles)<prob_best):
                q = prob_best_s[prob_bsettile]
                print("click x:"+str(q[0])+",y:"+str(q[1])+" from tank algorithm "+str(prob_best)+".")
                return {"position":{"x":q[0],"y":q[1]},"mine":False}
            else:
                position = self.chooseRandomly()
                print("click x:"+str(position[0])+",y:"+str(position[1])+" from random algorithm.")
                return {"position":{"x":position[0],"y":position[1]},"mine":False}
        else:
            position = self.chooseRandomly()
            print("click x:"+str(position[0])+",y:"+str(position[1])+" from random algorithm.")
            return {"position":{"x":position[0],"y":position[1]},"mine":False}

    def chooseRandomly(self):
        revealed = self.revealed
        marked = self.marked
        x_w = self.x_w
        y_w = self.y_w

        cornerCount = 0

        if(revealed[0][0] == False and marked[0][0] == False):
            cornerCount +=1
        
        if(revealed[x_w-1][0] == False and marked[x_w-1][0] == False):
            cornerCount +=1
        
        if(revealed[x_w-1][y_w-1] == False and marked[x_w-1][y_w-1] == False):
            cornerCount +=1

        if(revealed[0][y_w-1] == False and marked[0][y_w-1] == False):
            cornerCount +=1

        if(cornerCount==0):
            x = random.randint(0,x_w-1)
            y = random.randint(0,y_w-1)
            while(revealed[x][y] == True or marked[x][y] == True):
                x = random.randint(0,x_w-1)
                y = random.randint(0,y_w-1)
            return [x,y]
        
        rand = random.randint(0,3)
        if(rand == 0):
            x = 0
            y = 0         
        elif(rand == 1):
            x = x_w-1
            y = 0
        
        elif(rand ==2):
            x = 0
            y = y_w -1
        else:
            x = x_w -1
            y = y_w -1
        return [x,y]
        


    def tankRecurse(self,borderTiles,k):
        x_w = self.x_w
        y_w = self.y_w
        knownMine = self.knownMine
        knownEmpty = self.knownEmpty
        nums = self.nums
        revealed = self.revealed
        flagCount = 0
        TOT_MINES = self.TOT_MINES
        borderOptimization = self.borderOptimization

        for x in range(x_w):
            for y in range(y_w):
                if(knownMine[x][y]):
                    flagCount+=1
                if(not revealed[x][y]):
                    continue

                num = nums[x][y] 
                surround = 0
                if((x==0 and y==0) or (x==y_w-1 and y==x_w-1)):
                    surround = 3
                elif(x==0 or y==0 or y==y_w-1 or x==x_w-1):
                    surround = 5
                else:
                    surround = 8
                
                numFlags = countFlagAround(knownMine,x,y)
                numFree = countFlagAround(knownEmpty,x,y)

                if(num<numFlags):
                    return
                if(surround-numFree<num):
                    return
        
        if(flagCount > TOT_MINES):
            return 

        if(k == len(borderTiles)):
            if(not borderOptimization and flagCount < TOT_MINES):
                return
            solution = []
            for i in range(0,len(borderTiles)):
                s = borderTiles[i]
                sx = s[0]
                sy = s[1]

                solution.append(knownMine[sx][sy])
            
            self.tank_solutions.append(solution)
            return

        q = borderTiles[k]
        qx = q[0]
        qy = q[1]

        knownMine[qx][qy] = True
        self.tankRecurse(borderTiles,k+1)
        knownMine[qx][qy] = False

        knownEmpty[qx][qy] = True
        self.tankRecurse(borderTiles,k+1)
        knownEmpty[qx][qy] = False


    def tankSegregate(self,borderTiles):
        x_w = self.x_w
        y_w = self.y_w
        revealed = self.revealed
        allRegions = []
        covered = []

        while(True):
            queue = []
            finishedRegion = []

            for tile in borderTiles:
                if(not (tile in covered)):
                    queue.append(tile)
                    break
            
            if(len(queue)==0):
                break

            while(not (len(queue) == 0)):
                curTile = queue.pop(0)
                xh = curTile[0]
                yh = curTile[1]
                finishedRegion.append(curTile)
                covered.append(curTile)
                for tile in borderTiles:
                    xt = tile[0]
                    xt = tile[1]
                    isConnected = False
                    if(tile in finishedRegion):
                        continue
                    if(abs(xh-xh)>2 or abs(xt-xt)>2):
                        isConnected = False
                    else:
                        for x in range(x_w):
                            for y in range(y_w):
                                isB = False
                                if(revealed[x][y]==False):
                                    if(abs(xh-x)<=1 and abs(yh-y)<=1 and abs(xt-x)<=1 and abs(xh-y)<=1):
                                        isConnected = True
                                        isB = True
                                if(isB):
                                    break
                    if(not isConnected):
                        continue
                    if(not(tile in queue)):
                        queue.append(tile)
            allRegions.append(finishedRegion)
        return allRegions






    def isBoundry(self,x,y):
        revealed = self.revealed
        x_w = self.x_w
        y_w = self.y_w

        oU = oD = oL = oR = False
        isboundry = False

        if(x==0):
            oL = True
        if(y==0):
            oU = True
        if(x==x_w-1):
            oR = True
        if(y==y_w-1):
            oD = True

        if(not oU and revealed[x][y-1]):
            isboundry = True
        if(not oL and  revealed[x-1][y]):
            isboundry = True
        if(not oR and revealed[x+1][y]):
            isboundry = True
        if(not oD and revealed[x][y+1]):
            isboundry = True
        if(not oU and not oL and(revealed[x-1][y-1])):
            isboundry = True
        if(not oU and not oR and(revealed[x+1][y-1])):
            isboundry = True
        if(not oD and not oL and(revealed[x-1][y+1])):
            isboundry = True
        if(not oD and not oR and(revealed[x+1][y+1])):
            isboundry = True        
        return isboundry

    def getApparentSafes(self):
        revealed = self.revealed
        marked = self.marked
        nums = self.nums
        safes = []
        for x in range(self.x_w):
            for y in range(self.y_w):
                if(revealed[x][y]==False or nums[x][y]==0):
                    continue
                else:
                    adjacents = self.getAdjacentTiles(x,y)
                    minesSurroundCount = nums[x][y]
                    
                    markedMinesCount = 0
                    surroundSafes = []
                    for adjacent in adjacents:
                        if(marked[adjacent[0]][adjacent[1]]):
                            markedMinesCount += 1
                        elif(revealed[adjacent[0]][adjacent[1]]==False):
                            surroundSafes.append([adjacent[0],adjacent[1]])
                    
                    if(markedMinesCount==minesSurroundCount):
                        for safe in surroundSafes:
                            safes.append(safe)
        return safes

    




    def getApparentDangers(self):
        revealed = self.revealed
        marked = self.marked
        nums = self.nums
        dangers = []
        for x in range(self.x_w):
            for y in range(self.y_w):
                if(revealed[x][y]==False or nums[x][y]==0):
                    continue
                else:
                    adjacents = self.getAdjacentTiles(x,y)
                    minesSurroundCount = nums[x][y]
                    
                    markedMinesCount = 0
                    unRevealedCount = 0
                    
                    surroundDangers = []
                    for adjacent in adjacents:
                        if(marked[adjacent[0]][adjacent[1]]):
                            markedMinesCount += 1
                        elif(revealed[adjacent[0]][adjacent[1]]==False):
                            surroundDangers.append([adjacent[0],adjacent[1]])
                            unRevealedCount+=1
                    
                    if(minesSurroundCount-markedMinesCount == unRevealedCount):
                        for danger in surroundDangers:
                            dangers.append(danger)
        return dangers


    def getAdjacentTiles(self,x,y):
        x_w = self.x_w
        y_w = self.y_w

        adjacents = []
        if x!=0:
            adjacents.append([x-1,y])
            if y!= 0:
                adjacents.append([x-1,y-1])
            if y!= y_w-1:
                adjacents.append([x-1,y+1])
        
        if x!= x_w -1:
            adjacents.append([x+1,y])
            if y!= 0:
                adjacents.append([x+1,y-1])
            if y!= y_w-1:
                adjacents.append([x+1,y+1])           

        if y!= 0:
            adjacents.append([x,y-1])
        if y!= y_w-1:
            adjacents.append([x,y+1])

        return adjacents


def getAdjacentTiles(x,y):
    # get box XY coordinates for all adjacent boxes to (box_x, box_y)
    x_w =20
    y_w = 20
    adjacents = []
    if x!=0:
        adjacents.append([x-1,y])
        if y!= 0:
            adjacents.append([x-1,y-1])
        if y!= y_w-1:
            adjacents.append([x-1,y+1])
    if x!= x_w -1:
        adjacents.append([x+1,y])
        if y!= 0:
            adjacents.append([x+1,y-1])
        if y!= y_w-1:
            adjacents.append([x+1,y+1])           
    if y!= 0:
        adjacents.append([x,y-1])
    if y!= y_w-1:
        adjacents.append([x,y+1])
    return adjacents

def countFlagAround(arr,x,y):
    x_w = len(arr)
    y_w = len(arr[0])
    oU = oD = oL = oR = False

    count = 0
    if(x==0):
        oL = True
    if(y==0):
        oU = True
    if(x==x_w-1):
        oR = True
    if(y==y_w-1):
        oD = True
    if(not oU and arr[x][y-1]):
        count+=1
    if(not oL and  arr[x-1][y]):
        count+=1
    if(not oR and arr[x+1][y]):
        count+=1
    if(not oD and arr[x][y+1]):
        count+=1
    if(not oU and not oL and(arr[x-1][y-1])):
        count+=1
    if(not oU and not oR and(arr[x+1][y-1])):
        count+=1
    if(not oD and not oL and(arr[x-1][y+1])):
        count+=1
    if(not oD and not oR and(arr[x+1][y+1])):
        count+=1        
    return count   
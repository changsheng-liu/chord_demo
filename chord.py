BITLENGTH = 8

class FingerTable(object):

    nodeId = None
    nodes = None
    starts = None

    def __init__(self, nodeId):
        self.nodeId = nodeId
        self.nodes = [None] * (BITLENGTH+1)
        self.starts = [nodeId]+[(pow(2,x)+nodeId)%pow(2,BITLENGTH) for x in range(BITLENGTH)]

    def prettyPrint(self):
        print("    For Node "+str(self.nodeId)+":")
        for i in range(1,BITLENGTH+1):
            print("        Start: " + str(self.starts[i]) + ", Successor ID: " + str(self.nodes[i].id_))

class Node(object):

    id_ = None
    finger = None
    localKeys = None
    predecessor = None

    def __init__(self, nodeId):
        self.id_ = nodeId
        self.finger = FingerTable(self.id_)
        self.localKeys = {"key":"value"}
    
    def join(self, node):
        if not node:
            self.finger.nodes = [self for x in self.finger.nodes]
            self.predecessor = self
            print("Initial Node's finger table: ")
            self.finger.prettyPrint()
            return
        self.init_finger_table(node)

        print("New joint Node created a following finger table: ")
        self.finger.prettyPrint()

        self.update_others(self.successor())
        print("    Migrated keys are from Node "+str(self.predecessor.id_) + " to Node "+str(self.id_))
        for key in list(self.successor().localKeys):
            if isinstance(key, int):
                if self.betweenCheck(key, self.predecessor.id_, False, self.id_, True):
                    print("    Migrated Key by joining: "+str(key))
                    self.localKeys.update({key:self.successor().localKeys[key]}) 
                    self.successor().localKeys.pop(key)
           
    def leave(self):
        if self.predecessor is self:
            return
        print("    Migrated keys are from Node "+str(self.id_) + " to Node "+str(self.successor().id_))
        for key in list(self.localKeys):
            if isinstance(key, int):
                print("    Migrated Key by leaving: "+str(key))
                self.successor().localKeys.update({key:self.localKeys[key]}) 
        self.successor().predecessor = self.predecessor
        self.predecessor.finger.nodes[1] = self.successor()
        self.update_finger_table(self.successor())
        self.successor().update_others(self.successor().successor())
        self.finger.nodes = [None] * (BITLENGTH+1)

    def find(self, key):
        node = self.find_successor(key,True)
        if key in node.localKeys:
            return node
        return None
    
    def insert(self, key):
        node = self.find_successor(key,False)
        if key in node.localKeys:
            node.localKeys[key] = key
        else:
            node.localKeys.update({key:key})
        return node

    def remove(self, key):
        node = self.find_successor(key,False)
        print("    Finally node which holds the removed key: " + str(node.id_))
        if key in node.localKeys:
            node.localKeys.pop(key)
        return node

    def find_successor(self, key, needPrint):
        node = self.find_predecessor(key,needPrint)
        return node.successor()

    def find_predecessor(self, key, needPrint):
        cur = self
        while not self.betweenCheck(key,cur.id_,False,cur.successor().id_,True):
            if needPrint:
                print("    Involved Lookup Node: " + str(cur.id_))
            cur = cur.closest_preceding_finger(key)
        if needPrint:
            print("    Involved Lookup Node: " + str(cur.id_))
            if cur.successor() is not cur:
                print("    Involved Lookup Node: " + str(cur.successor().id_))
        return cur
    
    def closest_preceding_finger(self, key):
        for i in range(BITLENGTH,0,-1):
            if self.betweenCheck(self.finger.nodes[i].id_,self.id_,False,key,False):
                return self.finger.nodes[i]
        return self
    
    def init_finger_table(self,node):
        self.finger.nodes[0] = self
        self.finger.nodes[1] = node.find_successor(self.finger.starts[1],False)
        self.predecessor = self.successor().predecessor
        self.successor().predecessor = self
        self.predecessor.finger.nodes[1] = self
        self.update_finger_table(self)

    def update_others(self,node):
        if node is self:
            return 
        self.update_finger_table(node)
        self.update_others(node.successor())

    def update_finger_table(self,node):
        printFlag = False
        for i in range(1,BITLENGTH):
            target = node.finger.starts[i+1]
            preNode = node.finger.nodes[i+1].id_ if node.finger.nodes[i+1] else -1
            cur = node
            while True:
                if self.betweenCheck(target, cur.id_, False, cur.successor().id_, True):
                    node.finger.nodes[i+1] = cur.successor()
                    if node.finger.nodes[i+1].id_ != preNode:
                        printFlag = True
                    break
                else:
                    cur = cur.successor()
        if (printFlag and node is not self) or node is self.predecessor:
            print("Caused updating-finger-table node by new:")
            node.finger.prettyPrint()
                
    def successor(self):
        return self.finger.nodes[1]
        
    def betweenCheck(self, checkedKey, left, isLeftClosed, right, isRightClosed):
        if right == left:
            return True
        if not isLeftClosed and not isRightClosed:
            return (left < right and checkedKey > left and checkedKey < right) \
        or (right < left and \
        ((checkedKey > right and checkedKey > left) \
        or (checkedKey < right and checkedKey < left)))

        if not isLeftClosed and isRightClosed:
            return (left < right and checkedKey > left and checkedKey <= right) \
        or (right < left and \
        ((checkedKey >= right and checkedKey > left) \
        or (checkedKey <= right and checkedKey < left)))

        if isLeftClosed and not isRightClosed:
            return (left < right and checkedKey >= left and checkedKey < right) \
        or (right < left and \
        ((checkedKey > right and checkedKey >= left) \
        or (checkedKey < right and checkedKey <= left)))
        
        if isLeftClosed and isRightClosed:
            return (left < right and checkedKey >= left and checkedKey <= right) \
        or (right < left and \
        ((checkedKey >= right and checkedKey >= left) \
        or (checkedKey <= right and checkedKey <= left)))

def main():
    print("---Begin Chord Testing:")
    vectorNode = [229, 208, 214, 187, 8, 165, 18, 143, 193, 83, 238, 201, 192, 14, 134, 98, 123, 70, 253, 105]
    keylist = [21, 92, 168, 240, 215, 18, 209, 222, 19, 223, 137, 101, 248, 122, 241, 185, 160, 187, 237, 245, 133, 143, 211, 1, 139, 88, 252, 57, 178, 138, 95, 219, 86, 162, 221, 179, 231, 52, 242, 232, 234, 40, 59, 145, 42, 220, 29, 228, 112, 74, 141, 9, 34, 23, 65, 176, 63, 84, 189, 136, 31, 230, 62, 13, 170, 182, 96, 247, 6, 164, 208, 192, 58, 163, 204, 198, 17, 39, 98, 188, 181, 202, 30, 35, 233, 254, 251, 174, 171, 108, 151, 239, 167, 50, 15, 45, 214, 229, 60, 43, 155, 180, 195, 44, 76, 3, 12, 113, 207, 173, 0, 157, 47, 4, 194, 193, 105, 16, 201, 97, 161, 66, 85, 116, 100, 117, 67, 152, 77, 81, 71, 28, 33, 38, 107, 196, 149, 213, 90, 190, 78, 135, 243, 93, 186, 225, 236, 238, 72, 121, 150, 250, 70, 123, 128, 246, 172, 169, 46, 235, 114, 20, 130, 255, 25, 64, 197, 226, 184, 148, 224, 158, 154, 7, 91, 8, 244, 147, 177, 5, 24, 10, 102, 203, 82, 166, 134, 69, 216, 212, 26, 156, 249, 131, 253, 49, 119, 79, 218, 227]
    findlist = list()
    nodeList = list()
    for i in range(len(vectorNode)):
        print()
        tmp = {0:"1st",1:"2nd",2:"3rd"}
        idx = str(i+1) + "th" if i+1 > 3 else tmp[i]
        node = Node(vectorNode[i])
        existingNode = nodeList[i-2 if i > 3 else i-1] if nodeList else None
        if not existingNode:
            print("---Join--- The 1st Node is trying to join. Initial Chord by Node " + str(node.id_))
        else:
            print("---Join--- The " +idx+ " Node is trying to join. Node " + str(node.id_) + " is joining Chord by Node " + str(existingNode.id_))
        node.join(existingNode)
        nodeList.append(node)
        print()
        for _ in range(10):
            targetkey = keylist.pop(0)
            print("---Insert--- Insert Key "+str(targetkey))
            node.insert(targetkey)
            findlist.append(targetkey)
        print()
        for e in nodeList:
            print("Node " + str(e.id_) + " has following keys:")
            print(e.localKeys)
    
    for i,findKey in enumerate(findlist):
        print()
        findNode = nodeList[i%len(nodeList)]
        findresult = findNode.find(findKey)
        if findresult:
            print("---Find--- search from Node " + str(findNode.id_)+": key " + str(findKey) + " is in Node "+ str(findresult.id_))

    removeCount = 50
    for i in range(removeCount):
        print()
        rkey = findlist.pop(0)
        t = nodeList[(i+3)%20] 
        rnode = t.remove(rkey)
        print("---Remove--- remove Key " + str(rkey) + " from Node " + str(rnode.id_)+", request from Node "+ str(t.id_))
        keylist.append(rkey)

    seed = [14,9,2,6,8]
    for k,i in enumerate(seed):
        print()
        leaveNode = nodeList.pop(i)
        print("---Leave--- Leaving Node "+str(leaveNode.id_))
        leaveNode.leave()
        reinsertNode = nodeList[i+2]
        refindNode = nodeList[i+4]
        for rikey in keylist[k*10:(k+1)*10]:
            rinode = reinsertNode.insert(rikey)
            print("---Insert After Leave--- Insert Key "+str(rikey)+" from Node " + str(reinsertNode.id_)+" stored in Node " + str(rinode.id_))
            locate = refindNode.find(rikey)
            if locate:
                print("---Find After Leave--- search from Node " + str(refindNode.id_)+": key " + str(rikey) + " is in Node "+ str(locate.id_))
    print()
    for e in nodeList:
        print("Node " + str(e.id_) + " has following keys:")
        print(e.localKeys)

    print()
    print("---End Chord Testing!")
    

if __name__ == "__main__":
    main()

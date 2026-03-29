import argparse, random

class BBox:
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.y1 = min(x1,x2), min(y1,y2)
        self.x2, self.y2 = max(x1,x2), max(y1,y2)
    def area(self): return (self.x2-self.x1)*(self.y2-self.y1)
    def union(self, other):
        return BBox(min(self.x1,other.x1),min(self.y1,other.y1),max(self.x2,other.x2),max(self.y2,other.y2))
    def intersects(self, other):
        return self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1
    def enlargement(self, other):
        return self.union(other).area() - self.area()

class RNode:
    def __init__(self, bbox, data=None, children=None):
        self.bbox = bbox; self.data = data; self.children = children or []
    def is_leaf(self): return self.data is not None

class RTree:
    def __init__(self, max_entries=4):
        self.root = None; self.max = max_entries; self.count = 0
    def insert(self, bbox, data=None):
        node = RNode(bbox, data or f"item_{self.count}")
        if not self.root:
            self.root = RNode(bbox, children=[node])
        else:
            self._insert(self.root, node)
        self.count += 1
    def _insert(self, parent, node):
        if all(c.is_leaf() for c in parent.children) or not parent.children:
            parent.children.append(node)
            parent.bbox = parent.bbox.union(node.bbox)
            if len(parent.children) > self.max:
                pass  # simplified: no split
        else:
            best = min(parent.children, key=lambda c: c.bbox.enlargement(node.bbox))
            self._insert(best, node)
            parent.bbox = parent.bbox.union(node.bbox)
    def search(self, query_bbox):
        results = []
        if self.root: self._search(self.root, query_bbox, results)
        return results
    def _search(self, node, query, results):
        if not node.bbox.intersects(query): return
        if node.is_leaf():
            results.append((node.bbox, node.data))
        for child in node.children:
            self._search(child, query, results)

def main():
    p = argparse.ArgumentParser(description="R-tree spatial index")
    p.add_argument("--demo", action="store_true")
    p.add_argument("-n", type=int, default=20)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    if args.demo:
        random.seed(args.seed)
        rt = RTree()
        for i in range(args.n):
            x, y = random.randint(0,90), random.randint(0,90)
            w, h = random.randint(2,10), random.randint(2,10)
            rt.insert(BBox(x, y, x+w, y+h), f"rect_{i}")
        query = BBox(30, 30, 60, 60)
        results = rt.search(query)
        print(f"Inserted {rt.count} rectangles")
        print(f"Query [30,30,60,60]: {len(results)} results")
        for bbox, data in results:
            print(f"  {data}: [{bbox.x1},{bbox.y1},{bbox.x2},{bbox.y2}]")
    else: p.print_help()

if __name__ == "__main__":
    main()

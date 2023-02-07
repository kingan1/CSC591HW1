import math
from typing import Union, List, Dict

from cols import Cols
from num import Num
from options import options
from row import Row
from sym import Sym
from utils import csv, many, cosine, any, copy, helper


class Data:
    def __init__(self, src: Union[str, List]) -> None:
        self.rows = list()
        self.cols = None
        if type(src) == str:
            csv(src, self.add)
        else:
            self.add(src or [])

    def add(self, t: Union[List, Row]):
        """
        Adds a new row and updates column headers.

        :param t: Row to be added
        """
        if self.cols:
            t = t if isinstance(t, Row) else Row(t)

            self.rows.append(t)
            self.cols.add(t)
        else:
            self.cols = Cols(t)

    def clone(self, init: List) -> 'Data':
        """
        Returns a clone with the same structure as self.

        :param init: Initial data for the clone
        """
        data = Data(list(self.cols.names))
        list(map(data.add, init or []))

        return data

    def stats(self, cols: List[Union[Sym, Num]], nplaces: int, what: str = "mid") -> Dict:
        """
        Returns mid or div of cols (defaults to i.cols.y).

        :param cols: Columns to collect statistics for
        :param nplaces: Decimal places to round the statistics
        :param what: Statistics to collect
        :return: Dict with all statistics for the columns
        """
        return dict(sorted({col.txt: col.rnd(getattr(col, what)(), nplaces) for col in cols or self.cols.y}.items()))

    def cluster(self, rows: List[Row] = None, cols: List[Union[Sym, Num]] = None, above: Row = None):
        """
        Performs N-level bi clustering on the rows.

        :param rows: Data points to cluster
        :param min_: Clustering threshold value
        :param cols: Columns to cluster on
        :param above: Point chosen as A
        :return: Rows under the current node
        """
        rows = self.rows if rows is None else rows
        cols = self.cols.x if cols is None else cols


        node = {"data": self.clone(rows)}

        if len(rows) >= 2:
            left, right, node['A'], node['B'], node['mid'], node['c'] = self.half(rows, cols, above)

            node['left'] = self.cluster(left, cols, node['A'])
            node['right'] = self.cluster(right, cols, node['B'])

        return node
 
    def dist(self,row1,row2,cols=None):
        n = 0
        dis = 0
        cols = (cols if cols else self.cols.x)
        for _,c in enumerate(cols):
            n = n + 1
            dis = dis + c.dist(row1.cells[c.at], row2.cells[c.at]) ** options['p']
        return (dis/n) ** (1/options['p'])
    
    def around(self, row1, rows=None, cols=None):
        """
        sort other `rows` by distance to `row`
        """
        rows = (rows if rows else self.rows)
        cols = (cols if cols else self.cols.x)

        def func(row2):
            return {'row': row2, 'dist': self.dist(row1, row2, cols)}
            
        return sorted(list(map(func, rows)), key=lambda x: x['dist'])

    def half(self, rows=None, cols=None, above=None):
        """
        divides data using 2 far points
        """
        def dist(row1, row2):
            return self.dist(row1, row2, cols)

        def project(row, x=None, y=None):
            x,y = cosine(dist(row,A), dist(row,B),c)
            row.x = row.x or x
            row.y = row.y or y
            return {"row":row, "x":x,"y":y}
        
        left , right = [],[]
        rows = (rows if rows else self.rows) 
        A = above if above else any(rows)
        B = self.furthest(A, rows)['row']
        c = dist(A,B)

        for n, tmp in enumerate(sorted(list(map(project, rows)), key=lambda x: x["x"])):
            if n <= len(rows) // 2:
                left.append(tmp["row"])
                mid = tmp["row"]
            else:
                right.append(tmp["row"])

        return left, right, A, B, mid, c
    
    def furthest(self, row1=None,  rows=None,cols=None):
        """ 
        sort other `rows` by distance to `row`
        """
        t=self.around(row1,rows,cols)
        return t[len(t)-1]


def rep_rows(t, rows):
    rows = copy(rows)

    for j, s in rows[-1]:
        rows[1][j] += (":" + s)

    del rows[-1]

    for n, row in enumerate(rows):
        if n == 1:
            row.append("thingX")
        else:
            u = t.rows[-(n - 1)]
            row.append(u[-1])

    return Data(rows)


def rep_cols(cols):
    cols = copy(cols)

    for column in cols:
        column[len(column)-1] = str(column[0]) + ':' + str(column[len(column)-1])

        for j in range(1, len(column)):
            column[j-1] = column[j]

        column.pop()

    cols.insert(0, [helper(i) for i in range(len(cols[0])-1)])
    cols[0][len(cols[0])-1] = "thingX"

    return Data(cols)

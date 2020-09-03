import sys 
import collections
try:
    num = int(sys.stdin.readline().strip().split()[0])
    while True:
        line1 = sys.stdin.readline().strip()
        if line1 == '':
            break
        line2 = sys.stdin.readline().strip()
        res = 0
        lines1 = line1.split()
        lines2 = line2.split()
        count = int(lines1[0])
        seen = set()
        boolean = False
        for i in lines2:
            ans = bin(int(i))[2::]
            dic = collections.Counter(ans)
            if '1' not in ans:
                boolean = True
            if '1' in dic and dic['1'] not in seen:
                seen.add(dic['1'])
        if boolean:
            print len(seen)+1
        else:
            print len(seen)
except:
    pass
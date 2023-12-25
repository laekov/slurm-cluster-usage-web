import os
import sys
from datetime import datetime
from config import clusters, days, outdir, allname


commandt = 'ssh {headnode} sreport -P user topuse start=now-{day}days end=now topcount=1000 group'


with open('ranklist-template.html', 'r') as f:
    htmlt = f.read()
htmlt = htmlt.replace("RDATE", datetime.isoformat(datetime.now()))
rowt = "<tr><td>{i}</td><td>{n}</td><td>{u}</td></tr>"
tho = "<th>Rank</th> <th>User</th> <th>Usage</th>"


def main(outdir='./', aday=30):
    overall = dict()
    for c in clusters:
        for d in days:
            rows = []
            cmd = commandt.format(headnode=clusters[c], day=d)
            with os.popen(cmd, 'r') as fi:
                for l in fi:
                    ls = l.split('|')
                    if ls[0] != c:
                        continue
                    rows.append((ls[1], int(ls[-2])))
                    if ls[1] not in overall:
                        overall[ls[1]] = dict()
                    overall[ls[1]][f"{c}-{d}"] = int(ls[-2])
            tbody = "\n".join([rowt.format(i=i, n=n, u=u) for i, (n, u) in enumerate(rows)])
            html = htmlt.replace("RTH", tho).replace('RDAY', f'{d}').replace('RCLUSTER', c).replace('RTBODY', tbody)
            with open(f"{outdir}/ranklist-{c}-{d}.html", 'w') as f:
                f.write(html)
            print(f'{c}-{d} done')
    for u in overall:
        tot = 0
        for c in clusters:
            k = f"{c}-{aday}"
            tot += overall[u].get(k, 0)
        overall[u]["total"] = tot
    th = f"<th>Rank</th><th>User</th><th>Total ({aday} days)</th>" 
    th += "".join([f"<th><a href='ranklist-{c}-{d}.html'>{c} ({d} days)</a></th>"
        for c in clusters for d in days])
    tbody = ""
    ul = reversed(sorted(overall.keys(), key=lambda k: overall[k]["total"]))
    for i, u in enumerate(ul):
        tr = ("<td>{}</td>" * 3).format(i, u, overall[u]["total"]) 
        tr += "".join(["<td>{}</td>".format(overall[u].get(f"{c}-{d}", 0))
            for c in clusters for d in days])
        tbody += f"<tr>{tr}</tr>\n"
    html = htmlt.replace("RTH", th).replace('RDAY', f'{aday}').replace('RCLUSTER', allname).replace('RTBODY', tbody)
    with open(f"{outdir}/clusterank.html", "w" ) as f:
        f.write(html)



if __name__ == '__main__':
    main(outdir)

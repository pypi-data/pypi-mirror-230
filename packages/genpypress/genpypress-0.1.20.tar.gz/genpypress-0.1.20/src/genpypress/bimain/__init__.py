import gitlab
import os

# token = glpat-KMWDJaomuu7MYv_unXj2
for k in ("HTTP_PROXY", "HTTPS_PROXY"):
    try:
        del os.environ[k]
    except KeyError:
        pass
gl = gitlab.Gitlab('https://git-it.cz.o2', private_token='glpat-KMWDJaomuu7MYv_unXj2', ssl_verify=False)
_projects = gl.projects.list()
bimain = None
for p in _projects:    
    if p.name.lower()=="bimain":
        bimain=p

assert bimain
print(bimain)

# merge requests
for m in gl.mergerequests.list():
    if m.project_id == bimain.id and m.state == "opened":
        # print(m)
        print(f"{m.title=} {m.author=} {m.references=}")
        print("-" * 80)
        # title, 
from aclib.dm import *

dl = DmDotsetLib.fromfile(r"E:\#project\python\PersonalLib\.test\ddd")
for d in dl:
    d.print()

dm = DM()
print(dm.Ver())

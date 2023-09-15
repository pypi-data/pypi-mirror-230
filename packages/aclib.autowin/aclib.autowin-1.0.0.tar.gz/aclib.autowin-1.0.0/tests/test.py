from aclib.cv import Dotset, DotsetLib, FontLib
from aclib.autowin.windows import Window

win = Window('一梦江湖', 'Messiah_Game')
print(win)

# d = Dotset.fromimage('1', win.cvcapture((778,277,821,318,)), '208050--2fbf7f', matchcolor=1, cropmode=2, cropmargin=1)
# d.print()

# fl = FontLib.fromfile('tests/num')
# fl.add(d)
# fl.list()
# fl.tofile('tests/num')

win.cvset(dotsetlib='num', fontlib='num')

texts = win.cvocr((528,212,1631,976,), '889999--ffffff', txtwrap=True, similarity=0.7)
print(texts)

# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.5.2
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x06\xbc\
/\
*\x0a * libstored, \
distributed debu\
ggable data stor\
es.\x0a * Copyright\
 (C) 2020-2023  \
Jochem Rutgers\x0a \
*\x0a * This Source\
 Code Form is su\
bject to the ter\
ms of the Mozill\
a Public\x0a * Lice\
nse, v. 2.0. If \
a copy of the MP\
L was not distri\
buted with this\x0a\
 * file, You can\
 obtain one at h\
ttps://mozilla.o\
rg/MPL/2.0/.\x0a */\
\x0a\x0aimport QtQuick\
 2.12\x0aimport QtQ\
uick.Layouts 1.1\
5\x0aimport QtQuick\
.Window 2.2\x0aimpo\
rt QtQuick.Contr\
ols 2.5\x0a\x0aWindow \
{\x0a\x0a    id: root\x0a\
    visible: tru\
e\x0a    width: 400\
\x0a    height: 300\
\x0a\x0a    readonly p\
roperty int font\
Size: 10\x0a\x0a    Co\
mponent.onComple\
ted: {\x0a        v\
ar text = \x22Visu\x22\
\x0a\x0a        var id\
 = client.identi\
fication()\x0a     \
   if(id && id !\
== \x22?\x22)\x0a        \
{\x0a            te\
xt += \x22: \x22 + id\x0a\
\x0a            var\
 v = client.vers\
ion()\x0a          \
  if(v && v !== \
\x22?\x22)\x0a           \
     text += \x22 (\
\x22 + v + \x22)\x22\x0a    \
    }\x0a\x0a        r\
oot.title = text\
\x0a    }\x0a\x0a    Colu\
mnLayout {\x0a     \
   anchors.fill:\
 parent\x0a        \
anchors.margins:\
 5\x0a\x0a        Text\
Field {\x0a        \
    id: req\x0a    \
        Layout.p\
referredHeight: \
root.fontSize * \
2\x0a            fo\
nt.pixelSize: ro\
ot.fontSize\x0a    \
        Layout.f\
illWidth: true\x0a \
           place\
holderText: \x22ent\
er command\x22\x0a    \
        backgrou\
nd.antialiasing:\
 true\x0a          \
  topPadding: 0\x0a\
            bott\
omPadding: 0\x0a\x0a  \
          onAcce\
pted: {\x0a        \
        rep.text\
 = client.req(te\
xt)\x0a            \
}\x0a        }\x0a\x0a   \
     ScrollView \
{\x0a            La\
yout.fillWidth: \
true\x0a           \
 Layout.fillHeig\
ht: true\x0a       \
     clip: true\x0a\
\x0a            Tex\
tArea {\x0a        \
        id: rep\x0a\
                \
readOnly: true\x0a \
               f\
ont.pixelSize: r\
oot.fontSize\x0a   \
         }\x0a\x0a    \
        backgrou\
nd: Rectangle {\x0a\
                \
antialiasing: tr\
ue\x0a             \
   border.color:\
 \x22#c0c0c0\x22\x0a     \
       }\x0a       \
 }\x0a    }\x0a}\x0a\
\x00\x00\x06A\
/\
*\x0a * libstored, \
distributed debu\
ggable data stor\
es.\x0a * Copyright\
 (C) 2020-2023  \
Jochem Rutgers\x0a \
*\x0a * This Source\
 Code Form is su\
bject to the ter\
ms of the Mozill\
a Public\x0a * Lice\
nse, v. 2.0. If \
a copy of the MP\
L was not distri\
buted with this\x0a\
 * file, You can\
 obtain one at h\
ttps://mozilla.o\
rg/MPL/2.0/.\x0a */\
\x0a\x0aimport QtQuick\
.Controls\x0aimport\
 QtQuick\x0a\x0aTextFi\
eld {\x0a    id: co\
mp\x0a\x0a    backgrou\
nd.antialiasing:\
 true\x0a\x0a    topPa\
dding: 0\x0a    bot\
tomPadding: 0\x0a  \
  leftPadding: 0\
\x0a    horizontalA\
lignment: TextIn\
put.AlignRight\x0a \
   readOnly: tru\
e\x0a\x0a    property \
string unit: ''\x0a\
\x0a    property al\
ias ref: o.ref\x0a \
   property alia\
s obj: o.obj\x0a   \
 property alias \
pollInterval: o.\
pollInterval\x0a   \
 property alias \
refreshed: o.ref\
reshed\x0a    prope\
rty alias value:\
 o.value\x0a    pro\
perty bool conne\
cted: o.obj !== \
null\x0a    propert\
y alias autoRead\
OnInit: o.autoRe\
adOnInit\x0a\x0a    pr\
operty var o: St\
oreObject {\x0a    \
    id: o\x0a    }\x0a\
\x0a    // Specify \
a (lambda) funct\
ion, which will \
be used to conve\
rt the value\x0a   \
 // to a string.\
 If null, the va\
lueString of the\
 object is used.\
\x0a    property va\
r formatter: nul\
l\x0a\x0a    property \
string valueForm\
atted: {\x0a       \
 var s;\x0a\x0a       \
 if(!connected)\x0a\
            s = \
'';\x0a        else\
 if(formatter)\x0a \
           s = f\
ormatter(o.value\
);\x0a        else\x0a\
            s = \
o.valueString;\x0a\x0a\
        return s\
\x0a    }\x0a\x0a    prop\
erty string _tex\
t: {\x0a        var\
 s = '';\x0a       \
 if(!connected)\x0a\
            s = \
'?';\x0a        els\
e\x0a            s \
= valueFormatted\
;\x0a\x0a        if(un\
it != '')\x0a      \
      s += ' ' +\
 unit\x0a\x0a        r\
eturn s\x0a    }\x0a  \
  text: _text\x0a\x0a \
   color: !conne\
cted ? \x22gray\x22 : \
refreshed ? \x22blu\
e\x22 : \x22black\x22\x0a}\x0a\x0a\
\
\x00\x00\x06^\
/\
*\x0a * libstored, \
distributed debu\
ggable data stor\
es.\x0a * Copyright\
 (C) 2020-2023  \
Jochem Rutgers\x0a \
*\x0a * This Source\
 Code Form is su\
bject to the ter\
ms of the Mozill\
a Public\x0a * Lice\
nse, v. 2.0. If \
a copy of the MP\
L was not distri\
buted with this\x0a\
 * file, You can\
 obtain one at h\
ttps://mozilla.o\
rg/MPL/2.0/.\x0a */\
\x0a\x0aimport QtQuick\
.Controls\x0aimport\
 QtQuick\x0a\x0aMeasur\
ement {\x0a    read\
Only: false\x0a    \
pollInterval: 0\x0a\
\x0a    property bo\
ol editing: acti\
veFocus && displ\
ayText != valueF\
ormatted\x0a\x0a    pr\
operty bool _edi\
ted: false\x0a    o\
nEditingChanged \
: {\x0a        if(!\
editing) {\x0a     \
       _edited =\
 true\x0a          \
  Qt.callLater(f\
unction() { _edi\
ted: false })\x0a  \
      }\x0a    }\x0a\x0a \
   property bool\
 valid: true\x0a   \
 property color \
validBackgroundC\
olor: \x22white\x22\x0a  \
  property color\
 invalidBackgrou\
ndColor: \x22#ffe0e\
0\x22\x0a    palette.b\
ase: valid ? val\
idBackgroundColo\
r : invalidBackg\
roundColor\x0a\x0a    \
color: editing ?\
 \x22red\x22 : !connec\
ted ? \x22gray\x22 : r\
efreshed && !_ed\
ited ? \x22blue\x22 : \
\x22black\x22\x0a    text\
: \x22\x22\x0a\x0a    onAcce\
pted: {\x0a        \
o.set(displayTex\
t)\x0a        Qt.ca\
llLater(function\
() { text = valu\
eFormatted })\x0a  \
  }\x0a\x0a    onActiv\
eFocusChanged: {\
\x0a        if(acti\
veFocus)\x0a       \
     text = valu\
eFormatted\x0a     \
   else\x0a        \
    text = _text\
\x0a    }\x0a\x0a    on_T\
extChanged: {\x0a  \
      if(!editin\
g)\x0a            t\
ext = _text\x0a    \
}\x0a\x0a    Keys.forw\
ardTo: decimalPo\
intConversion\x0a  \
  Item {\x0a       \
 id: decimalPoin\
tConversion\x0a    \
    Keys.onPress\
ed: (event) => {\
\x0a            if(\
obj !== null && \
event.key == Qt.\
Key_Period && (e\
vent.modifiers &\
 Qt.KeypadModifi\
er)) {\x0a         \
       event.acc\
epted = true\x0a   \
             obj\
.injectDecimalPo\
int(parent)\x0a    \
        }\x0a      \
  }\x0a    }\x0a}\x0a\x0a\
\x00\x00\x00p\
m\
odule Libstored.\
Components\x0aInput\
 1.0 Input.qml\x0aM\
easurement 1.0 M\
easurement.qml\x0aS\
toreObject 1.0 S\
toreObject.qml\x0a\
\x00\x00\x06\xbb\
/\
*\x0a * libstored, \
distributed debu\
ggable data stor\
es.\x0a * Copyright\
 (C) 2020-2023  \
Jochem Rutgers\x0a \
*\x0a * This Source\
 Code Form is su\
bject to the ter\
ms of the Mozill\
a Public\x0a * Lice\
nse, v. 2.0. If \
a copy of the MP\
L was not distri\
buted with this\x0a\
 * file, You can\
 obtain one at h\
ttps://mozilla.o\
rg/MPL/2.0/.\x0a */\
\x0a\x0aimport QtQuick\
\x0a\x0aItem {\x0a    id:\
 comp\x0a\x0a    requi\
red property var\
 ref\x0a    propert\
y var obj: null\x0a\
    property str\
ing name: obj ? \
obj.name : \x22\x22\x0a  \
  property real \
pollInterval: 2\x0a\
    property boo\
l autoReadOnInit\
: true\x0a\x0a    onRe\
fChanged: {\x0a    \
    if(typeof(re\
f) != \x22string\x22) \
{\x0a            ob\
j = ref\x0a        \
} else if(typeof\
(client) == \x22und\
efined\x22) {\x0a     \
       obj = nul\
l\x0a        } else\
 {\x0a            o\
bj = client.obj(\
ref)\x0a        }\x0a \
   }\x0a\x0a    onObjC\
hanged: {\x0a      \
  if(obj) {\x0a    \
        value = \
obj.valueSafe\x0a\x0a \
           if(!o\
bj.polling) {\x0a  \
              if\
(pollInterval > \
0)\x0a             \
       obj.poll(\
pollInterval)\x0a  \
              el\
se if(autoReadOn\
Init)\x0a          \
          obj.as\
yncRead()\x0a      \
      } else if(\
pollInterval > 0\
 && obj.pollInte\
rval > pollInter\
val) {\x0a         \
       // Prefer\
 the faster sett\
ing, if there ar\
e multiple.\x0a    \
            obj.\
poll(pollInterva\
l)\x0a            }\
\x0a        } else \
{\x0a            va\
lue = null\x0a     \
   }\x0a    }\x0a\x0a    \
property string \
valueString: obj\
 ? obj.valueStri\
ng : ''\x0a    prop\
erty var value: \
null\x0a\x0a    proper\
ty bool refreshe\
d: false\x0a\x0a    Ti\
mer {\x0a        id\
: updatedTimer\x0a \
       interval:\
 1100\x0a        on\
Triggered: comp.\
refreshed = fals\
e\x0a    }\x0a\x0a    onV\
alueStringChange\
d: {\x0a        if(\
obj)\x0a           \
 value = obj.val\
ueSafe\x0a\x0a        \
comp.refreshed =\
 true\x0a        up\
datedTimer.resta\
rt()\x0a    }\x0a\x0a    \
function set(x) \
{\x0a        if(obj\
)\x0a            ob\
j.valueString = \
x\x0a    }\x0a}\x0a\
"

qt_resource_name = b"\
\x00\x09\
\x09\xab\xcdT\
\x00L\
\x00i\x00b\x00s\x00t\x00o\x00r\x00e\x00d\
\x00\x08\
\x08\x01Z\x5c\
\x00m\
\x00a\x00i\x00n\x00.\x00q\x00m\x00l\
\x00\x0a\
\x07n\x093\
\x00C\
\x00o\x00m\x00p\x00o\x00n\x00e\x00n\x00t\x00s\
\x00\x0f\
\x0d\x0f\x0a\xbc\
\x00M\
\x00e\x00a\x00s\x00u\x00r\x00e\x00m\x00e\x00n\x00t\x00.\x00q\x00m\x00l\
\x00\x09\
\x07\xc7\xf8\x9c\
\x00I\
\x00n\x00p\x00u\x00t\x00.\x00q\x00m\x00l\
\x00\x06\
\x07\x84+\x02\
\x00q\
\x00m\x00l\x00d\x00i\x00r\
\x00\x0f\
\x06\xb2\x90\xfc\
\x00S\
\x00t\x00o\x00r\x00e\x00O\x00b\x00j\x00e\x00c\x00t\x00.\x00q\x00m\x00l\
"

qt_resource_struct = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x18\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x01\x89\xba/\xbdm\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x03\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00.\x00\x02\x00\x00\x00\x04\x00\x00\x00\x04\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x96\x00\x00\x00\x00\x00\x01\x00\x00\x13\xdb\
\x00\x00\x01\x89\xba/\xbdm\
\x00\x00\x00\x84\x00\x00\x00\x00\x00\x01\x00\x00\x13g\
\x00\x00\x01\x89\xba/\xbdm\
\x00\x00\x00l\x00\x00\x00\x00\x00\x01\x00\x00\x0d\x05\
\x00\x00\x01\x89\xba/\xbdm\
\x00\x00\x00H\x00\x00\x00\x00\x00\x01\x00\x00\x06\xc0\
\x00\x00\x01\x89\xba/\xbdm\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()

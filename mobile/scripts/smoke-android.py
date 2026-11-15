"""Verify the installed release starts on Android 10 and the four tabs respond."""
import os, re, subprocess, time, xml.etree.ElementTree as ET
from pathlib import Path

def adb(*args):
    return subprocess.check_output(['adb', *args], text=True)

def nodes():
    adb('shell','uiautomator','dump','/sdcard/window.xml')
    return ET.fromstring(adb('shell','cat','/sdcard/window.xml')).iter('node')

def tap(label):
    matches=[n for n in nodes() if n.get('text')==label or n.get('content-desc')==label]
    assert matches, f'Missing control: {label}'
    bounds=list(map(int,re.findall(r'\d+',matches[0].get('bounds',''))))
    assert len(bounds)==4
    adb('shell','input','tap',str((bounds[0]+bounds[2])//2),str((bounds[1]+bounds[3])//2))
    time.sleep(1)

adb('logcat','-c')
adb('shell','am','start','-W','-n','bg.spestoslav.preview/.MainActivity')
for _ in range(20):
    if any('Спестовник' in n.get('text','') for n in nodes()): break
    time.sleep(1)
else: raise AssertionError('App did not render its header')
for tab in ['Горива','Дом','Техника','Храни']:
    tap(tab)
tap('Моят списък')
assert any('Списъкът е празен' in n.get('text','') for n in nodes())
tap('Сканирай')
assert any('Камерата' in n.get('text','') for n in nodes())
tap('Храни')
assert adb('shell','pidof','bg.spestoslav.preview').strip(), 'App process died'
logs=adb('logcat','-d')
assert 'FATAL EXCEPTION' not in logs, logs
Path('android-smoke.log').write_text(logs)
with open('android-preview-'+os.environ.get('PREVIEW_SEQUENCE','001')+'.png','wb') as f:
    f.write(subprocess.check_output(['adb','exec-out','screencap','-p']))
print('Android 10 smoke passed: launch, four tabs, empty list, honest camera state; process alive.')

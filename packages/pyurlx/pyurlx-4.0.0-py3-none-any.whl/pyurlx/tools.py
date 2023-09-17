import urllib.request

def shorten(url):
  page = urllib.request.urlopen(f'https://mcpi.cc/api.php?url={url}')
  short = str(page.read())
  if short.find("b\'") != -1:
    short = short.split("b'")[1]
  if short.find("\\n") != -1:
    short = short.split("\\n")[0]
  return short

def qr(url):
  page = urllib.request.urlopen(f'https://mcpi.cc/qrapi.php?url={url}')
  qr = str(page.read())
  if qr.find("b\'") != -1:
    qr = qr.split("b'")[1]
  if qr.find("\\n") != -1:
    qr = qr.split("\\n")[0]
  return qr
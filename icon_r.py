import base64

favicon = open("static/favicon.ico", "rb")
favicon_str = base64.b64encode(favicon.read())
favicon.close()

write_data = "img = %s" % favicon_str
f = open("icon.py", "w+")
f.write(write_data)
f.close()

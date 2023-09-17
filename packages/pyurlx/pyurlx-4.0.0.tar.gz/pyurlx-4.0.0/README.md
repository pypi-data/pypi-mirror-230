
# pyURLx
This is a simple module built with requests that allows you to shorten long URLs and create QR codes using the URLx api.

## Prerequisites
Before running the application, make sure you have Python installed on your system.

## Installation
To use the module, you can install it through pip:
`pip install pyurlx`
## How to Use
You can use the module to shorten links and create qr codes. The module is very simple to use. To shorten a link, use the following code:
<code>
from pyurlx import tools<br>
link = tools.shorten("example.com")<br>
print(link)
</code>
To create a qr code, use the following code:
<code>
from pyurlx import tools<br>
link = tools.qr("example.com")<br>
print(link)
</code>

## Contributing
Contributions are welcome! If you find any bugs or have suggestions for improvements, please feel free to open an issue or submit a pull request at https://github.com/urlxdev/pyurlx.

## License
This project is licensed under the BSD-3 License.
from pyurlx import tools
link = tools.shorten("example.com")
print(link)
</code>

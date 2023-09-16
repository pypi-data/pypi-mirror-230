# Converts an image to ASCII art using numpy / numexpr / cv2

## Tested against Windows 10 / Python 3.11 / Anaconda

### pip install numpyasciiart


```python
Convert an image to ASCII art.

Parameters:
	img (str or numpy.ndarray): url/path/base64/bin/np.array/PIL.Image representing an image.
	width (int): Width of the ASCII art output.
	height_adjust_stretch (float): Vertical stretch factor for the ASCII art.
	letters (str): The set of characters to use for varying shades in the ASCII art.

Returns:
	str: ASCII art representation of the input image.

Example:
	To convert an image and print it as ASCII art:
	from numpyasciiart import to_ascii
	pic = to_ascii(
		img=r"https://www.python.org/static/img/python-logo.png",
		width=160,
		height_adjust_stretch=2.5,
		letters="█▓▓▒▒░░ ",
	)

	print(pic)
```
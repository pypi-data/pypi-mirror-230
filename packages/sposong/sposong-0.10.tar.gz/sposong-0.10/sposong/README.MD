# Finds similar songs

## Tested against Windows 10 / Python 3.10 / Anaconda

## pip install sposong



```python

Args:
	allplaylists (list): A list of Spotify playlist URLs to scrape data from.
	savefolder (str): The folder where the scraped data will be saved as Excel files.
	opera_browser_exe (str): The path to the Opera GX browser executable.
	opera_driver_exe (str): The path to the Opera WebDriver executable.
	userdir (str): The path to the user directory for the Opera browser.

Returns:
	None: The scraped data is saved as Excel files in the specified 'savefolder'.

Example Usage:
	parse_artists(
		allplaylists=[
			'https://open.spotify.com/playlist/3DBZUCUA2w8JcE8mBA0wUB',
			'https://open.spotify.com/playlist/37i9dQZF1DWZLiXDryu4Fe',
			'https://open.spotify.com/playlist/6DSfG4qBWdpaNK9PclUeAI',
			'https://open.spotify.com/playlist/37i9dQZF1DXdSjVZQzv2tl',
			'https://open.spotify.com/playlist/1XhfOTC9d3VwyJrS3EW8iW'
		],
		savefolder="c:\\savedmusic",
		opera_browser_exe=r"C:\Program Files\Opera GX\opera.exe",
		opera_driver_exe=r"C:\ProgramData\anaconda3\envs\dfdir\operadriver.exe",
		userdir="c:\\operabrowserprofile2"
	)

```
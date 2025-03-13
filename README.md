# Gallery-dl organizer script
This is a script I use to download artists galleries from multiple sources without putting too much thought into it
Right now it only works for Windows

---

To use, copy the !_BASE folder and rename it to the artists username, then open the `links.json` file and add some links like this
```json
[
    {"directory": "./Folder1", "url": "https://example.com/artistpage"},
    {"directory": "./Folder2", "url": "https://example.net/artistpage"}
]
```
Open `gdlconf.conf` and change whatever you need to, like the filenames. Download [cookies.txt](https://github.com/hrdl-github/cookies-txt) to export your cookies, some websites require you to do this.
Now run `downloader.py`, you can select a number to pick a folder or type "all" to go through them all one by one.

When everything is done you'll have a folder tree like this, you can also add your own folders if you want to
```
root
├── cookies.txt
├── downloader.py
├── gdl.exe
├── gdlconf.conf
├── !_BASE
│   └── links.json
└── Artist
    ├── links.json
    └── Folder1
        ├── image.png
        └── meta
            └── image.json
```

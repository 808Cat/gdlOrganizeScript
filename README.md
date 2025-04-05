# Gallery-DL organizer script
This is a script I use to download artists galleries from multiple sources without putting too much thought into it.

It should support Windows and Linux, but I don't use Windows anymore so I won't test it.

I wrote all this with AI.. I don't want to learn how to program just to download some furry porn, okay? It works, and it hasn't exploded yet, so it's fine to me.

---

To use, copy the !_BASE folder and rename it to the artists username, then open the `links.json` file and add some links like this
```json
[
    {"directory": "./Folder1", "url": "https://example.com/artistpage"},
    {"directory": "./Folder2", "url": "https://example.net/artistpage"}
]
```
Open `gdlconf.conf` and change whatever you need to, like the filenames and logins. Download [cookies.txt](https://github.com/hrdl-github/cookies-txt) to export your cookies, some websites require you to do this. Export the cookies by site, and add them to a `cookies.txt` file. You could also have multiple `cookies.txt` files if you really want to.

Now run `downloader.py`, you can select a number to pick a folder or type "all" to go through them all one by one. If you want to skip a download for any reason, such as Furaffinity having a dogshit API that makes Gallery-DL go through every fucking post one by one, press `S` and then `Enter`.

When everything is done you'll have a folder tree like this, you can also add your own folders for stuff not downloaded using Gallery-DL.
```
root
├── cookies.txt
├── downloader.py
├── gdl.exe (or gdl.bin)
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

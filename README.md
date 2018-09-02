# ALExport

Creates MAL style xml of your AniList Anime and Manga list. This xml is importable by AniList.

I can not guarantee 100% functionality for imports, I did test it with my list, but there might be edge cases that could kill your list.
Import to MAL will probably not work with the current format, but untill they enable their import I can't test that.

The Rewatching status will be lost using this, since MAL doesn't have one everything set to Rewatching on AL will be Watching, the count should be carried over regardless.

# Usage
Get python 3 and install requests and lxml

`pip3 install requests`

`pip3 install lxml`

After that you can run the script from console and it’ll create an xml of your lists in the current folder.


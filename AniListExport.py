import requests
import json
from lxml import etree
import sys
import codecs

mangaConversions = {
    "PAUSED" : "On-Hold",
    "COMPLETED":"Completed",
    "CURRENT":"Reading",
    "PLANNING":"Plan to Read",
    "DROPPED": "Dropped",
    "REPEATING": "Reading",
    "MANGA":"MANGA",
    "NOVEL":"NOVEL",
    "ONE_SHOT":"ONE_SHOT",
    None:"Unknown"
}

animeConversions = {
    "PAUSED" : "On-Hold",
    "COMPLETED":"Completed",
    "CURRENT":"Watching",
    "PLANNING":"Plan to Watch",
    "DROPPED": "Dropped",
    "REPEATING": "Watching",
    "OVA": "OVA",
    "SPECIAL": "Special",
    "ONA": "ONA",
    "TV_SHORT": "TV",
    "TV":"TV",
    "MOVIE": "Movie",
    "MANGA":"MANGA",
    "NOVEL":"NOVEL",
    "ONE_SHOT":"ONE_SHOT",
    "MUSIC":"MUSIC",
    None:"Unknown"
}

Query = '''query ($userName: String) {
  manga: MediaListCollection(userName: $userName, type: MANGA) {
    lists {
      name
      isCustomList
      entries {
        score(format: POINT_100)
        repeat
        progress
        progressVolumes
        notes
        completedAt {
          year
          month
          day
        }
        startedAt {
          year
          month
          day
        }
        status
        media {
          title {
            romaji
          }
          idMal
          id
          format
          chapters
          volumes
          siteUrl
        }
      }
    }
  }
  anime: MediaListCollection(userName: $userName, type: ANIME) {
    lists {
      name
      isCustomList
      entries {
        score(format: POINT_100)
        repeat
        progress
        notes
        completedAt {
          year
          month
          day
        }
        startedAt {
          year
          month
          day
        }
        status
        media {
          title {
            romaji
          }
          idMal
          id
          format
          episodes
          siteUrl
        }
      }
    }
  }
}'''



requestUrl = 'https://graphql.anilist.co'



userName = input('Enter your Username: ')


response = requests.post(requestUrl, json={"query" : Query, "variables" : {"userName" : userName}})

if response.status_code != 200:
    print("Could not find User")
    sys.exit()

responseJson = response.json()

root = etree.Element("myanimelist")

info = etree.SubElement(root, 'myinfo')

etree.SubElement(info, 'user_export_type').text = '1'

processedIds = []
failedEntries =[]

file = codecs.open("anime_list.csv", "w", "utf-8")
file.write("Title,Score,Progress,Type\n'")
for listType in responseJson['data']['anime']['lists']:
  for listentry in listType['entries']:
    if listentry['media']['id'] not in processedIds:
      if listentry['media']['idMal'] is None:
        failedEntries.append(listentry['media'])
      processedIds.append(listentry['media']['id'])
      anime = etree.SubElement(root,'anime')
      etree.SubElement(anime, 'series_animedb_id').text =str(listentry['media']['idMal'])
      etree.SubElement(anime, 'series_anilist_id').text = str(listentry['media']['id'])
      etree.SubElement(anime,'series_title').text = etree.CDATA(listentry['media']['title']['romaji'])
      etree.SubElement(anime, 'series_type').text = animeConversions[listentry['media']['format']]
      etree.SubElement(anime,'series_episodes').text = str(listentry['media']['episodes'])
      etree.SubElement(anime, 'my_watched_episodes').text = str(listentry['progress']) if listentry['repeat'] == 0 else str(listentry['media']['episodes'])
      if listentry['startedAt']['year'] is not None:
          etree.SubElement(anime, 'my_start_date').text = str(listentry['startedAt']['year']) + '-' + str(listentry['startedAt']['month']) + '-' + str(listentry['startedAt']['day'])
      else:
          etree.SubElement(anime, 'my_start_date').text = '0000-00-00'
      if listentry['completedAt']['year'] is not None:
          etree.SubElement(anime, 'my_finish_date').text = str(listentry['completedAt']['year']) + '-' + str(listentry['completedAt']['month']) + '-' + str(listentry['completedAt']['day'])
      else:
          etree.SubElement(anime, 'my_finish_date').text = '0000-00-00'
      etree.SubElement(anime,'my_score').text = str(int(listentry['score']/10))
      etree.SubElement(anime, 'my_status').text = animeConversions[listentry['status']]
      etree.SubElement(anime, 'my_comments').text = etree.CDATA('')
      etree.SubElement(anime,'my_times_watched').text = str(listentry['repeat'])
      etree.SubElement(anime, "my_rewatching_ep").text = str(listentry['progress']) if listentry['repeat'] !=0 else  str(0)
      etree.SubElement(anime, "update_on_import").text = '1'

      file.write(listentry['media']['title']['romaji'])
      file.write(',')
      file.write(str(int(listentry['score']/10)))
      file.write(',')
      file.write(str(listentry['progress']))
      file.write(',')
      file.write(animeConversions[listentry['media']['format']])
      file.write('\n')


fileObj = open('AnimeList.xml', "wb")
content = etree.tostring(root, pretty_print=True, xml_declaration = True, encoding="UTF-8")
fileObj.write(content)
fileObj.close()

print('Missing Anime:')
for entry in failedEntries:
  print(entry['title']['romaji'] +' ' +  entry['siteUrl'])

failedEntries.clear()

root = etree.Element("myanimelist")

info = etree.SubElement(root, 'myinfo')

etree.SubElement(info, 'user_export_type').text = '2'

processedIds =[]

file = codecs.open("manga_list.csv", "w", "utf-8")
file.write("Title,Score,ProgressChapter,ProgressVolumes,Type\n'")
for listType in responseJson['data']['manga']['lists']:
  for listentry in listType['entries']:
    if listentry['media']['id'] not in processedIds:
      if listentry['media']['idMal'] is None:
        failedEntries.append(listentry['media'])
      processedIds.append(listentry['media']['id'])
      anime = etree.SubElement(root,'manga')
      etree.SubElement(anime, 'manga_mangadb_id').text =str(listentry['media']['idMal'])
      etree.SubElement(anime, 'manga_anilist_id').text = str(listentry['media']['id'])
      etree.SubElement(anime,'manga_title').text = etree.CDATA(listentry['media']['title']['romaji'])
      etree.SubElement(anime,'manga_volumes').text = str(listentry['media']['volumes'])
      etree.SubElement(anime,'manga_chapters').text = str(listentry['media']['chapters'])
      etree.SubElement(anime, 'my_read_volumes').text = str(listentry['progressVolumes']) if listentry['repeat'] == 0 else str(listentry['media']['volumes'])
      etree.SubElement(anime, 'my_read_chapters').text = str(listentry['progress']) if listentry['repeat'] == 0 else str(listentry['media']['chapters'])
      if listentry['startedAt']['year'] is not None:
          etree.SubElement(anime, 'my_start_date').text = str(listentry['startedAt']['year']) + '-' + str(listentry['startedAt']['month']) + '-' + str(listentry['startedAt']['day'])
      else:
          etree.SubElement(anime, 'my_start_date').text = '0000-00-00'
      if listentry['completedAt']['year'] is not None:
          etree.SubElement(anime, 'my_finish_date').text = str(listentry['completedAt']['year']) + '-' + str(listentry['completedAt']['month']) + '-' + str(listentry['completedAt']['day'])
      else:
          etree.SubElement(anime, 'my_finish_date').text = '0000-00-00'
      etree.SubElement(anime,'my_score').text = str(int(listentry['score']/10))
      etree.SubElement(anime, 'my_status').text = mangaConversions[listentry['status']]
      etree.SubElement(anime,'my_times_read').text = str(listentry['repeat'])
      etree.SubElement(anime, "update_on_import").text = '1'

      file.write(listentry['media']['title']['romaji'])
      file.write(',')
      file.write(str(int(listentry['score']/10)))
      file.write(',')
      file.write(str(listentry['progress']))
      file.write(',')
      file.write(str(listentry['progressVolumes']))
      file.write(',')
      file.write(mangaConversions[listentry['media']['format']])
      file.write('\n')


fileObj = open('MangaList.xml', "wb")
content = etree.tostring(root, pretty_print=True, xml_declaration = True, encoding="UTF-8")
fileObj.write(content)
fileObj.close()

print('Missing Manga:')
for entry in failedEntries:
  print(entry['title']['romaji'] + ' ' + entry['siteUrl'])

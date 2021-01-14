from spotdl.search.spotifyClient import get_spotify_client
from spotdl.search.songObj import SongObj

from typing import List
import bisect
# path = "C:/Users/Awesome/OneDrive/Documents/unique-links.txt"
path = "C:/Users/Awesome/Google Drive/Desktop/unique-links.txt"
file = open(path,'r')

links =[line[:len(line)-1] for line in file]

links.sort()

def song_present(url: str):
    if bisect.bisect_left(links,url) != len(links):
        if links[bisect.bisect_left(links,url)] == url:
            return True
    return False
#TODO: skip songs from the skip file
def search_for_song(query: str) ->  SongObj:
    '''
    `str` `query` : what you'd type into spotify's search box

    Queries Spotify for a song and returns the best match
    '''

    # get a spotify client
    spotifyClient = get_spotify_client()

    # get possible matches from spotify
    result = spotifyClient.search(query, type = 'track')

    # return first result link or if no matches are found, raise and Exception
    if len(result['tracks']['items']) == 0:
        raise Exception('No song matches found on Spotify')
    else:
        for songResult in result['tracks']['items']:
            songUrl = 'http://open.spotify.com/track/' + songResult['id']
            song = SongObj.from_url(songUrl)

            if song.get_youtube_link() != None:
                return song

        raise Exception('Could not match any of the results on YouTube')

def get_album_tracks(albumUrl: str) -> List[SongObj]:
    '''
    `str` `albumUrl` : Spotify Url of the album whose tracks are to be
    retrieved

    returns a `list<songObj>` containing Url's of each track in the given album
    '''

    spotifyClient = get_spotify_client()
    albumTracks = []
    albumUrls = []
    trackResponse = spotifyClient.album_tracks(albumUrl)

    # while loop acts like do-while
    offset = 0
    while True:

        for track in trackResponse['items']:
            url = 'https://open.spotify.com/track/' + track['id']
            if song_present(url):
                # the link is present in the skip file
                continue
            else:
                albumUrls.append(url)

        offset += 100
        # check if more tracks are to be passed
        if trackResponse['next']:
            trackResponse = spotifyClient.album_tracks(
                albumUrl,
                offset = offset
            )
        else:
            break
    for url in albumUrls:
        song = SongObj.from_url(url)
        if song.get_youtube_link() != None:
            albumTracks.append(song)

    print(len(albumTracks))
    return albumTracks

def get_playlist_tracks(playlistUrl: str) -> List[SongObj]:
    '''
    `str` `playlistUrl` : Spotify Url of the album whose tracks are to be
    retrieved

    returns a `list<songObj>` containing Url's of each track in the given playlist
    '''

    spotifyClient = get_spotify_client()
    playlistTracks = []
    playlistUrls = []

    playlistResponse = spotifyClient.playlist_tracks(playlistUrl)

    # while loop to mimic do-while
    offset = 0
    while True:
        for songEntry in playlistResponse['items']:
            url = 'https://open.spotify.com/track/' + songEntry['track']['id']
            if song_present(url):
                # the link is present in the skip file
                continue
            else:
                playlistUrls.append(url)
        offset += 100    
        # check if more tracks are to be passed
        if playlistResponse['next']:
            print(f"fetching next, offset is {offset}")
            playlistResponse = spotifyClient.playlist_tracks(
                playlistUrl,
                offset = offset
            )
        else:
            break
    for url in playlistUrls:
        song = SongObj.from_url(url)

        if song.get_youtube_link() != None:
            playlistTracks.append(song)

        
    print(len(playlistTracks))
    return playlistTracks

#TODO: skip songs from the skip file
def get_artist_tracks(artistUrl: str) -> List[SongObj]:
    '''
    `str` `artistUrl` : Spotify Url of the artist whose tracks are to be
    retrieved

    returns a `List` containing Url's of each track of the artist.
    '''

    spotifyClient = get_spotify_client()
    artistAlbums = []
    artistTracks = []

    artistResponse = spotifyClient.artist_albums(artistUrl)
    artistName     = spotifyClient.artist(artistUrl)['name']

    while True:

        for album in artistResponse['items']:
            albumUrl  = album['external_urls']['spotify']

            artistAlbums.append(albumUrl)

        # Check if the artist has more albums.
        if artistResponse['next']:
            artistResponse = spotifyClient.artist_albums(
                artistUrl,
                offset = len(artistAlbums)
            )
        else:
            break

    for album in artistAlbums:
        albumTracks = get_album_tracks(album)

        artistTracks += albumTracks

    #! Filter out the Songs in which the given artist has not contributed.
    artistTracks = [track for track in artistTracks if artistName in track.get_contributing_artists()]

    return artistTracks

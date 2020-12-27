var socket = io()

socket.on('connect', () => {
	socket.emit('player current')
	// setInterval(() => {
	// 	socket.emit('player current')
	// }, 4321);
})

socket.on('player current', (track) => {
	console.log(track)
	var context = track.context
	var item = track.item

	var album = item.album

	document.getElementById('song-title').innerHTML = item.name

	if (album.images.length > 0) {
		document.getElementById('current-album-art').src = album.images[0].url
	}

	if (item.artists.length > 0) {
		var song_artist = document.getElementById('song-artist')

		song_artist.innerHTML = item.artists[0].name
	}

	document.getElementById('song-album').innerHTML = album.name
})

var socket = io()

socket.on('state_change', (track) => {
	console.log(track)

	if (!('name' in track)) {
		console.error('track_window not in track')
		return
	}

	var img_url = select_image(track.album.images, 640)
	document.getElementById('album-image').src = img_url

	var song_title = track.name
	var song_album = track.album.name
	var artists = track.artists[0].name

	document.getElementById('song-title').innerHTML = song_title
	document.getElementById('song-artists').innerHTML = artists
	document.getElementById('song-album').innerHTML = song_album

})


function select_image(images, width) {
	var url = images[0].url
	images.forEach(img => {
		if (img.width == width) {
			url = img.url
		}
	});

	return url
}

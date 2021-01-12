var socket = io()

socket.on('state_change', (state) => {
	// console.log(state)

	if (!('name' in state)) {
		console.error('track_window not in state')
		return
	}

	var img_url = select_image(state.album.images, 640)
	document.getElementById('album-image').src = img_url

	var song_title = state.name
	var song_album = state.album.name
	var artists = state.artists[0].name

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

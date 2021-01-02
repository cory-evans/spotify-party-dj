var socket = io()

socket.on('connect', () => {
	socket.emit('player current')
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

function toggle_liked_song() {
	var icon = document.getElementById('button-like-song')
	var currently_liked = icon.classList.contains('bi-heart-fill')
	if (currently_liked) {
		icon.classList.remove('bi-heart-fill')
		icon.classList.add('bi-heart')
	} else {
		icon.classList.remove('bi-heart')
		icon.classList.add('bi-heart-fill')
	}
}

function toggle_skip_song() {
	var icon = document.getElementById('button-skip-song')
	var currently_active = icon.classList.contains('bi-skip-forward-fill')
	if (currently_active) {
		// disable
		icon.classList.remove('bi-skip-forward-fill')
		icon.classList.add('bi-skip-forward')

		socket.emit('vote skip', false)
	} else {
		// enable
		icon.classList.remove('bi-skip-forward')
		icon.classList.add('bi-skip-forward-fill')

		socket.emit('vote skip', true)
	}
}

function set_liked_song(state) {
	var icon = document.getElementById('button-skip-song')
	if (state) {
		icon.classList.remove('bi-skip-forward-fill')
		icon.classList.add('bi-skip-forward')
	} else {
		icon.classList.remove('bi-skip-forward')
		icon.classList.add('bi-skip-forward-fill')
	}
}

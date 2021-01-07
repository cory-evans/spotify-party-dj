var socket = io()

socket.on('state_change', (state) => {
	console.log(state)

	var current_track = state.track_window.current_track
	var queue = state.track_window.next_tracks

	update_doc(current_track, queue)

})

function update_doc(current_track, next_tracks) {
	var img_url = select_image(current_track.album.images, 640)
	document.getElementById('album-image').src = img_url

	var song_title = current_track.name
	var song_album = current_track.album.name
	var artists = current_track.artists[0].name

	document.getElementById('song-title').innerHTML = song_title
	document.getElementById('song-artists').innerHTML = artists
	document.getElementById('song-album').innerHTML = song_album

	document.getElementById('next-tracks').innerHTML = ''

	for (let index = 0; index < next_tracks.length; index++) {
		const element = next_tracks[index];
		var list_element = create_song_list_element(element, false)
		document.getElementById('next-tracks').appendChild(list_element)
	}
}


function select_image(images, width) {
	var url = images[0].url
	images.forEach(img => {
		if (img.width == width) {
			url = img.url
		}
	});

	return url
}

function create_song_list_element(track, is_button, callback_on_click) {
	if (is_button) {
		var el = document.createElement('button')
		el.classList.add('list-group-action')
		el.onclick = callback_on_click
	} else {
		var el = document.createElement('li')
	}
	el.classList.add('list-group-item')

	el.innerHTML = `${track.name} - ${track.artists[0].name}`

	return el
}

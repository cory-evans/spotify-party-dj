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

function on_search_input(search_input) {
	$(search_input).data('last_oninput', new Date().getTime())
	var search_term = $(search_input).val()

	var timeout_ms = 700

	setTimeout(() => {
		var now = new Date().getTime()
		if (now - $(search_input).data('last_oninput') > timeout_ms - 20) {
			// Search for the tracks
			if (search_term == '') { return }

			spotifyApi.searchTracks(search_term, null, populate_search_results)
		} else {
			console.log('skipping ', search_term);
		}
	}, timeout_ms);
}

function populate_search_results(err, results) {
	if (err) {
		console.err(err)
		return
	}

	$('#search-results').html('')

	results.tracks.items.forEach(track => {
		var tr = document.createElement('tr')

		var img_tr = document.createElement('tr')
		var img = document.createElement('img')

		img.src = select_image(track.album.images, 64)

		$(img_tr).append(img)

		var title = document.createElement('td')
		title.innerHTML = track.name

		var artist = document.createElement('td')
		artist.innerHTML = track.artists[0].name

		var album = document.createElement('td')
		album.innerHTML = track.album.name


		$(tr).append(img_tr)
		$(tr).append(title)
		$(tr).append(artist)
		$(tr).append(album)

		$('#search-results').append(tr)
	});
}

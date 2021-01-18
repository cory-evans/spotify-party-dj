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

socket.on('queue update', (queue) => {
	console.log('queue length:', queue.length)
	$('#queue-table').children('.table-row').remove()
	queue.forEach(track => {
		var row = $('<div class="table-row"></div>')
		var result = $('<div class="search-result row"></div>')
		row.append(result)


		var img = $('<img class="col-2"></img>')
		img.attr('src', select_image(track.album.images, 64))

		var title = $('<span class="col-5"></span>')
		title.text(track.name)

		var artist = $('<span class="col-5"></span>')
		artist.text(track.artists[0].name)

		result.append(img)
		result.append(title)
		result.append(artist)

		// create_confirm_dialog(row, track.uri)
		$('#queue-table').append(row)
	});
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
			if (search_term == '') {
				$('#search-results').children('.table-row').remove()
				return
			 }

			spotifyApi.searchTracks(search_term, null, populate_search_results)
		}
	}, timeout_ms);
}

function populate_search_results(err, results) {
	if (err) {
		console.err(err)
		return
	}

	function create_confirm_dialog(table_row, track_uri) {
		var div = $('<div class="confirm row fs-1 d-none"></div>')

		var decline = $('<i class="bg-danger bi bi-x"></i>')
		var accept = $('<i class="bg-success bi bi-plus"></i>')

		div.append(decline)
		div.append(accept)

		div.children('i').addClass('col-6 text-center text-light')

		accept.click(() => {
			add_to_queue(track_uri)
			hide_dialog(table_row)
		})

		decline.click(() => {
			hide_dialog(table_row)
		})

		$(table_row).append(div)
	}

	$('#search-results').children('.table-row').remove()

	results.tracks.items.forEach(track => {
		var row = $('<div class="table-row"></div>')
		var result = $('<div class="search-result row"></div>')
		result.click(() => {
			show_dialog(row)
		})
		row.append(result)


		var img = $('<img class="col-2"></img>')
		img.attr('src', select_image(track.album.images, 64))

		var title = $('<span class="col-5"></span>')
		title.text(track.name)

		var artist = $('<span class="col-5"></span>')
		artist.text(track.artists[0].name)

		result.append(img)
		result.append(title)
		result.append(artist)

		create_confirm_dialog(row, track.uri)
		$('#search-results').append(row)
	});
}

function add_to_queue(uri) {
	console.log('add_to_queue', uri)
	socket.emit('queue add item', uri)
}

function show_dialog(row) {
	const dialog_shown = $(row).data('dialog_shown')

	if (!dialog_shown) {
		$(row).children('.search-result').addClass('d-none')
		$(row).children('.confirm').removeClass('d-none')
	}

	$(row).data('dialog_shown', true)
}

function hide_dialog(row) {
	console.log("hide", row)
	const dialog_shown = $(row).data('dialog_shown')

	if (dialog_shown) {
		$(row).children('.search-result').removeClass('d-none')
		$(row).children('.confirm').addClass('d-none')
	}

	$(row).data('dialog_shown', false)
}

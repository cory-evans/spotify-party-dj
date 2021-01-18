var socket = io()

function refresh_device_list() {
	spotifyApi.getMyDevices((err, data) => {
		if (err) {
			spotify_handle_err(err)
			return
		}

		var devices = document.getElementById('devices')
		devices.innerHTML = '<option selected value=null>Select a device</option>';
		data.devices.forEach(device => {
			var el = document.createElement('option')

			el.value = device.id
			el.innerHTML = `${device.name} - ${device.type}`

			devices.appendChild(el)
		});
	})
}

function fetch_currently_playing() {
	spotifyApi.getMyCurrentPlaybackState((err, data) => {
		if (err) {
			spotify_handle_err(err)
			return
		}
		data.item.progress_ms = data.progress_ms

		// console.log(data.item);
		socket.emit('state_change', data.item)
	})
}


setInterval(() => {
	fetch_currently_playing()
}, 3021);

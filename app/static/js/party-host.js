var socket = io()
var spotifyApi = new SpotifyWebApi()

spotifyApi.setAccessToken(SPOTIFY_ACCESS_TOKEN)


function refresh_device_list() {
	spotifyApi.getMyDevices((err, data) => {
		if (err) {
			console.error(err)
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
			console.error(err)
			return
		}
		data.item.progress_ms = data.progress_ms

		console.log(data.item);
		socket.emit('state_change', data.item)
	})
}


setInterval(() => {
	fetch_currently_playing()
}, 2531);

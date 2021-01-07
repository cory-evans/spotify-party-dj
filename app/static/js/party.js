var socket = io()
var player

window.onSpotifyWebPlaybackSDKReady = async () => {
	console.log('token is', token)
	const player_init = new Spotify.Player({
		name: 'Party DJ Web Player',
		getOAuthToken: cb => { cb(token) }
	})

	player_init.addListener('initialization_error', ({ message }) => { console.error(message); });
	player_init.addListener('authentication_error', ({ message }) => { console.error(message); });
	player_init.addListener('account_error', ({ message }) => { console.error(message); });
	player_init.addListener('playback_error', ({ message }) => { console.error(message); });

	player_init.addListener('player_state_changed', state => {
		socket.emit('state_change', (state))
	 })
	player_init.addListener('ready', ({ device_id }) => {
		console.log('Ready with device ID', device_id)
	})

	player_init.addListener('not_ready', ({ device_id }) => {
		console.log('Device ID has gone offline', device_id)
	})

	player_init.connect()
	player = player_init
}

async function getOAuthToken(access_token) {
	let token = await fetch('/auth/refresh_token', {
			method: 'POST',
			body: JSON.stringify({token: access_token}),
			headers: {
				'Content-Type': 'application/json'
			}
		}
	)
	.then(resp => resp.json())
	.then(json => json['access_token'])

	return token
}

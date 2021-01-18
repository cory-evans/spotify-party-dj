var spotifyApi = new SpotifyWebApi()

spotifyApi.setAccessToken(SPOTIFY_ACCESS_TOKEN)


function spotify_handle_err(resp) {
	var err_json = JSON.parse(resp.response).error
	console.log(err_json)
	if (err_json.status == 401) {
		console.info('refreshing access token')
		refresh_token()
	}
}

function refresh_token() {
	fetch('/auth/refresh_token')
		.then(resp => resp.json())
		.then(data => {
			console.log('token: ', data);
			spotifyApi.setAccessToken(data.access_token)
		})
}

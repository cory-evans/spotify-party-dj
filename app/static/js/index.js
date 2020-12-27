function join_room() {
	var code = document.getElementById('input-party-code').value
	if (code == '') {
		return
	}

	window.location.pathname = '/party/join/' + code.toUpperCase()
}

function host_room() {
	window.location.pathname = '/party/host'
}

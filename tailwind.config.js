module.exports = {
  purge: {
	  enabled: false,
	  content: [
		  'app/templates/**/*.html',
		  'app/templates/**/*.js'
	  ]
  },
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {},
  },
  variants: {
    extend: {
		ringColor: ['hover']
	},
  },
  plugins: [],
}

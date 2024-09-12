module.exports = {
    content: [
        './templates/**/*.html',
        // Templates in other apps
        // Ignore files in node_modules
       // '!./**/node_modules',
        // Include JavaScript files that might contain Tailwind CSS classes
       // './../**/*.js',
        // Include Python files that might contain Tailwind CSS classes
       './**/*.py',

        './node_modules/flowbite/**/*.js'
    ],
    theme: {
        extend: {
            fontSize: {
                "normal": "14px",
                "small": "12px",
                "large": "16px",
                "xlarge": "20px",
                "xsmall": "10px",
            },
            fontFamily: {
                "sans": "'Nunito', sans-serif"
            },
            colors: {
                border: '#eaeded',
                'soft-paper': '#fafafa',
                paper: '#f2f3f3'
            }
        },
    },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
        require('flowbite/plugin')
    ],
}

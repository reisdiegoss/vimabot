/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#0f172a",
                foreground: "#f8fafc",
                netflix: {
                    red: "#E50914",
                    black: "#141414",
                },
            },
        },
    },
    plugins: [],
}

window.addEventListener('load', () => {

console.log('loading gifs');
    // List of GIF URLs to preload
    const gifUrls = [
        GASAM_game_tic_tac_toe_coin_choice_heads_URL,
        GASAM_game_tic_tac_toe_coin_choice_tails_URL,
        GASAM_game_tic_tac_toe_coin_heads_to_tails_URL,
        GASAM_game_tic_tac_toe_coin_tails_to_heads_URL,
        GASAM_game_tic_tac_toe_coin_choice_undecided_URL,
        GASAM_game_tic_tac_toe_coin_won_heads_URL,
        GASAM_game_tic_tac_toe_coin_won_tails_URL,
        // Add more URLs as needed
    ];

    // Get the target div element where the images will be added
    const loadImagesDiv = document.querySelector('.game_tic_tac_toe-load-images');

    // Function to fetch each GIF and check the response status
    const preloadGif = (url) => {
        fetch(url, { method: 'GET' })
            .then((response) => {
                if (response.ok) {
                    console.log(`GIF ${url} loaded successfully with status: ${response.status}`);
                    const img = new Image();
                    img.src = url;
                    document.querySelector('.game_tic_tac_toe-load-images').appendChild(img);
                } else {
                    console.error(`Error loading GIF ${url}: ${response.status}`);
                }
            })
            .catch((error) => {
                console.error(`Network error loading GIF ${url}:`, error);
            });
    };

    // Preload each GIF and check its status
    gifUrls.forEach(preloadGif);

});
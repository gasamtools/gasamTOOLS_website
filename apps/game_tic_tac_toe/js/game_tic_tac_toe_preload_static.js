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

    // Function to create and append a <link rel="preload"> tag
    const preloadGif = (url) => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = url;
        link.as = 'image';
        document.head.appendChild(link);
    };

    const preloadImages = (urls) => {
        const loadedImages = [];  // Store the preloaded images
        urls.forEach((url) => {
            const img = new Image();
            img.src = url;
            loadedImages.push(img);  // Keep reference to avoid garbage collection
            console.log(`Preloading: ${url}`);
        });
    };

    // Preload each GIF
    gifUrls.forEach(preloadGif);
    preloadImages(gifUrls);


console.log('gifs loaded');

});
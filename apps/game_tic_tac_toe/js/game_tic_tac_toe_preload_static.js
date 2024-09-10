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

    // Preload images using Image object and store references to them
    const preloadedImages = [];

    gifUrls.forEach((url) => {
        const img = new Image();
        img.src = url;

        // Add an event listener to confirm when the image has been fully loaded
        img.onload = () => {
            console.log(`GIF ${url} fully loaded and cached.`);
        };

        img.onerror = () => {
            console.error(`Failed to load GIF ${url}`);
        };

        preloadedImages.push(img); // Store the preloaded image
    });

    // Once the images are preloaded, they will be available from the cache for quick display
    console.log('GIFs preloading initiated...');

    // Example: Attach images to a hidden div when needed
    const loadImagesDiv = document.querySelector('.game_tic_tac_toe-load-images');

    preloadedImages.forEach((img) => {
        loadImagesDiv.appendChild(img);
    });

});
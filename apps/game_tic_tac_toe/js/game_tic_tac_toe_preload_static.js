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

    // Function to create and append <img> elements
    gifUrls.forEach((url) => {
        const img = document.createElement('img');
        img.src = url;            // Set the image source
        img.alt = 'Preloaded GIF'; // Set an alternative text
        img.classList.add('hidden'); // Initially hide the images with a class (if needed)

        loadImagesDiv.appendChild(img); // Append the image to the div
    });

    console.log('Images appended to the div');

});
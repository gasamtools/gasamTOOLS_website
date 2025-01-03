window.addEventListener('load', () => {

    const modalLoadingElement = document.getElementById('game_tic_tac_toeLoadingModal');
    const this_modal = bootstrap.Modal.getOrCreateInstance(modalLoadingElement, {
        backdrop: 'static',
        keyboard: false // Set to true if you want to allow closing via the keyboard
    });
        if (this_modal) {
            this_modal.show();
            $('.modal-backdrop.fade.show').show();
        } else {
            console.error('Modal instance not found.');
        }

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
    let loadedCount = 0; // Keep track of loaded GIFs
    const failedImages = [];

    gifUrls.forEach((url) => {
        const img = new Image();
        img.src = url;

        // Add an event listener to confirm when the image has been fully loaded
        img.onload = () => {
            console.log(`GIF ${url} fully loaded and cached.`);
            loadedCount++;

            // Check if this is the last image in the array
            if (loadedCount === gifUrls.length) {
                console.log('All GIFs have been preloaded.');
                console.log('Failed to load: '+failedImages);
                setTimeout(() => {
                    if (failedImages.length == 0) {
                        if (this_modal) {
                            this_modal.hide();
                            $('.modal-backdrop.fade.show').hide();
                        } else {
                            console.error('Modal instance not found.');
                        }
                    }
                }, 500)
            }
        };

        img.onerror = () => {
            console.error(`Failed to load GIF ${url}`);
            failedImages.push(loadedCount);
            loadedCount++;
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
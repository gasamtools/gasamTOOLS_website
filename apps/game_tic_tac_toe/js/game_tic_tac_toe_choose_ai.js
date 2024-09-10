document.addEventListener("DOMContentLoaded", () => {
    let game_tic_tac_toe_coin_choice;
    const toggleSwitch = document.getElementById('flexSwitchCheckDefault');
    const closeModalButton = document.getElementById('game_tic_tac_toeCloseModalButton');
    const modalElement = document.getElementById('game_tic_tac_toeModal');
    const coinBttns = document.querySelectorAll('button.game_tic_tac_toe.coin.btn');
    const flipCoinModalButton = document.getElementById('game_tic_tac_toeFlipCoinModalBttn');
    const coinImage = document.getElementById('game_tic_tac_toeCoinImg');

    // tracking if modal window is cancelled or closed without flipping the coin
    closeModalButton.addEventListener('click', function() {
        toggleSwitch.checked = false;
    });

    modalElement.addEventListener('hide.bs.modal', function (event) {
        toggleSwitch.checked = false;
    });

    // Add an event listener for buttons heads and tails
    coinBttns.forEach(bttn => {
        bttn.addEventListener('click', function() {
            $('button.game_tic_tac_toe.coin.btn').removeClass('btn-dark chosen');
            bttn.classList.add('btn-dark','chosen');
            const classes = bttn.classList;
            game_tic_tac_toe_coin_choice = classes[0];
            flipCoinModalButton.disabled = false;
            if (game_tic_tac_toe_coin_choice == 'heads') {
                if (coinImage.src.includes(GASAM_game_tic_tac_toe_coin_choice_undecided_URL)) {
                    coinImage.src = GASAM_game_tic_tac_toe_coin_choice_heads_URL;
                } else if (coinImage.src.includes(GASAM_game_tic_tac_toe_coin_choice_tails_URL) || coinImage.src.includes(GASAM_game_tic_tac_toe_coin_heads_to_tails_URL)){
                    coinImage.src = GASAM_game_tic_tac_toe_coin_tails_to_heads_URL;
                }
            } else if (game_tic_tac_toe_coin_choice == 'tails') {
                if (coinImage.src.includes(GASAM_game_tic_tac_toe_coin_choice_undecided_URL)) {
                    coinImage.src = GASAM_game_tic_tac_toe_coin_choice_tails_URL;
                } else if (coinImage.src.includes(GASAM_game_tic_tac_toe_coin_choice_heads_URL) || coinImage.src.includes(GASAM_game_tic_tac_toe_coin_tails_to_heads_URL)){
                    coinImage.src = GASAM_game_tic_tac_toe_coin_heads_to_tails_URL;
                }
            }
        });
    });

    // submitting coin choice and flipping the coin

    flipCoinModalButton.addEventListener('click', function() {
        flipCoinModalButton.disabled = true;
        $('button.game_tic_tac_toe.coin.btn').prop('disabled', true);
        // Get CSRF token from meta tag
        var csrfToken = $('meta[name="csrf-token"]').attr('content');

        const formObject = {
            'js_function': 'game_tic_tac_toe_choose_ai',
            'coin_choice': game_tic_tac_toe_coin_choice
        };
        fetch(GASAM_game_tic_tac_toe_URL, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // Include the CSRF token in the headers
            },
            body: JSON.stringify(formObject)
        })
        .then(response => {
            return response.json()
        })
        .then(data => {
            if ( (data['user_choice_status'] == false && data['coin_choice'] == 'heads') || (data['user_choice_status'] == true && data['coin_choice'] == 'tails' ) ) {
                coinImage.src = GASAM_game_tic_tac_toe_coin_won_tails_URL;
            } else if ( (data['user_choice_status'] == true && data['coin_choice'] == 'heads') || (data['user_choice_status'] == false && data['coin_choice'] == 'tails' ) ) {
                coinImage.src = GASAM_game_tic_tac_toe_coin_won_heads_URL;
            }

            if (data['user_choice_status'] == true) {
                $('#game_tic_tac_toeCoinAnnouncement').html('You Won! You go first!');
            } else if (data['user_choice_status'] == false) {
                $('#game_tic_tac_toeCoinAnnouncement').html('You Lost! AI goes first!');
            }

            setTimeout(() => {
                $('.game_tic_tac_toe.coin-announcement-container').removeClass('hidden');
            }, 3500)

            setTimeout(() => {
                const this_modal = bootstrap.Modal.getInstance(modalElement);
                if (this_modal) {
                    this_modal.hide();
                    $('.modal-backdrop.fade.show').hide();

                    // disable option turning OFF  AI
                    toggleSwitch.disabled = true;
                } else {
                    console.error('Modal instance not found.');
                }
            }, 5500)

            if (data['ai_move']) {
                if (data['player_move'] == 'circle') {
                    data['player_move'] = 'cross'
                } else if (data['player_move'] == 'cross') {
                    data['player_move'] = 'circle'
                }
                setTimeout(() => {
                    var this_ai_move = 'square-'+data['ai_move'];
                    GASAM_game_tic_tac_toe_make_a_move(data, this_ai_move);
                }, 6000)
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

});
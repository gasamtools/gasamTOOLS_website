document.addEventListener("DOMContentLoaded", () => {
    const cells = document.querySelectorAll('td.game_tic_tac_toe.td');
    const toggleSwitch = document.getElementById('flexSwitchCheckDefault');
    const modalPlayAgainElement = document.getElementById('game_tic_tac_toePlayAgainModal');
    const PlayAgainBttn = document.getElementById('game_tic_tac_toeFlipPlayAgainModalBttn');
    const coinImage = document.getElementById('game_tic_tac_toeCoinImg');
    const flipCoinModalButton = document.getElementById('game_tic_tac_toeFlipCoinModalBttn');


    cells.forEach(cell => {
        cell.addEventListener('click', function() {
            // disable option playing with AI
            toggleSwitch.disabled = true;

            if (this.classList.contains('clickable')) {
                const classes = cell.classList;
                const square_clicked = classes[0];

                var csrfToken = $('meta[name="csrf-token"]').attr('content');

                const formObject = {
                    'js_function': 'game_tic_tac_toe_game_engine',
                    'square_clicked': square_clicked
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

                    GASAM_game_tic_tac_toe_make_a_move(data, square_clicked);

                    if (data['ai_move']) {
                        if (data['player_move'] == 'circle') {
                            data['player_move'] = 'cross'
                        } else if (data['player_move'] == 'cross') {
                            data['player_move'] = 'circle'
                        }
                        setTimeout(() => {
                            var this_ai_move = 'square-'+data['ai_move'];
                            GASAM_game_tic_tac_toe_make_a_move(data, this_ai_move);
                        }, 2000)
                    }

                    if (data['winner']) {

                        if ( !data['ai_plays'] ) {
                            $('.game_tic_tac_toe.box_size.crossing-element').removeClass('hidden');
                            $('.game_tic_tac_toe.path.' + data['winner_strike']).removeClass('hidden');
                            $('td.game_tic_tac_toe.td').removeClass('clickable');


                            setTimeout(() => {
                                const this_modal = bootstrap.Modal.getOrCreateInstance(modalPlayAgainElement);
                                if (data['winner'] == 'cross') {
                                    $('#game_tic_tac_toePlayAgainAnnouncement').html('Player "X" Won!');
                                } else if (data['winner'] == 'circle') {
                                    $('#game_tic_tac_toePlayAgainAnnouncement').html('Player "O" Won!');
                                } else if (data['winner'] == 'none') {
                                    $('#game_tic_tac_toePlayAgainAnnouncement').html('Tie!');
                                }
                                if (this_modal) {
                                    this_modal.show();
                                    $('.modal-backdrop.fade.show').show();
                                } else {
                                    console.error('Modal instance not found.');
                                }
                            }, 1500)
                        } else {
                            setTimeout(() => {
                                $('.game_tic_tac_toe.box_size.crossing-element').removeClass('hidden');
                                $('.game_tic_tac_toe.path.' + data['winner_strike']).removeClass('hidden');
                                $('td.game_tic_tac_toe.td').removeClass('clickable');
                            }, 2500)

                            setTimeout(() => {
                                const this_modal = bootstrap.Modal.getOrCreateInstance(modalPlayAgainElement);
                                if (data['winner'] == 'cross') {
                                    $('#game_tic_tac_toePlayAgainAnnouncement').html('Player "X" Won!');
                                } else if (data['winner'] == 'circle') {
                                    $('#game_tic_tac_toePlayAgainAnnouncement').html('Player "O" Won!');
                                } else if (data['winner'] == 'none') {
                                    $('#game_tic_tac_toePlayAgainAnnouncement').html('Tie!');
                                }
                                if (this_modal) {
                                    this_modal.show();
                                    $('.modal-backdrop.fade.show').show();
                                } else {
                                    console.error('Modal instance not found.');
                                }
                            }, 3500)
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }
        });
    });


    PlayAgainBttn.addEventListener('click', function() {
        const this_modal = bootstrap.Modal.getOrCreateInstance(modalPlayAgainElement);
        if (this_modal) {
            this_modal.hide();
            $('.modal-backdrop.fade.show').hide();
        } else {
            console.error('Modal instance not found.');
        }

        var csrfToken = $('meta[name="csrf-token"]').attr('content');

        const formObject = {
            'js_function': 'game_tic_tac_toe_game_engine_reset',
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
            $('td.game_tic_tac_toe.td').addClass('clickable');
            $('svg.game_tic_tac_toe.cross').addClass('hidden');
            $('svg.game_tic_tac_toe.circle').addClass('hidden');
            $('.game_tic_tac_toe.box_size.crossing-element').addClass('hidden');
            $('.game_tic_tac_toe.path.crossing').addClass('hidden');
            $('.game_tic_tac_toe.player.btn').removeClass('btn-dark chosen');
            $('.game_tic_tac_toe.player.btn.cross').addClass('btn-dark chosen');
            toggleSwitch.checked = false;
            toggleSwitch.disabled = false;
            coinImage.src = GASAM_game_tic_tac_toe_coin_choice_undecided_URL;
            $('button.game_tic_tac_toe.coin.btn').removeClass('btn-dark chosen');
            $('button.game_tic_tac_toe.coin.btn').removeAttr('disabled');
            flipCoinModalButton.disabled = true;
            $('.game_tic_tac_toe.coin-announcement-container').addClass('hidden');
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});

function GASAM_game_tic_tac_toe_make_a_move(data, square_clicked) {

    $('.game_tic_tac_toe.player.btn').removeClass('btn-dark chosen');
    if (data['player_move'] == 'cross') {
        $('.game_tic_tac_toe.cross.' + square_clicked).removeClass('hidden');
        $('.game_tic_tac_toe.player.btn.circle').addClass('btn-dark chosen');
    } else if (data['player_move'] == 'circle') {
        $('.game_tic_tac_toe.circle.' + square_clicked).removeClass('hidden');
        $('.game_tic_tac_toe.player.btn.cross').addClass('btn-dark chosen');
    }
    $('td.game_tic_tac_toe.td.' + square_clicked).removeClass('clickable');
}
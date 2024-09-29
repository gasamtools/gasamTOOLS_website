function sendTypingTextRequest() {

    // Get CSRF token from meta tag
    var csrfToken = $('meta[name="csrf-token"]').attr('content');

    const formData = new FormData();
    formData.append('js_function', 'typing_speed_test_get_text'); // Append additional data if needed

    fetch(GASAM_typing_speed_test_URL, {
        method: 'PUT',
        headers: {
            'X-CSRFToken': csrfToken  // Include the CSRF token in the headers
            // 'Content-Type': 'multipart/form-data' // Do not set Content-Type header manually; FormData sets it
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {

        var html_data = '';
        for (let i = 0; i < data['text'].length; i++) {
            html_data += `<span class='char-${i} gasam tst chars '>${data['text'][i]}</span>`
        }

        $('#typing_speed_testMainText').html(html_data);
        typingSpeedEngine(data['user_record']);

    })
    .catch(error => {
        console.error('Error:', error);
    });

}

function userUpdateScore(new_score) {

    // Get CSRF token from meta tag
    var csrfToken = $('meta[name="csrf-token"]').attr('content');

    const formData = new FormData();
    formData.append('js_function', 'typing_speed_test_update_record'); // Append additional data if needed
    formData.append('new_score', new_score); // Append additional data if needed

    fetch(GASAM_typing_speed_test_URL, {
        method: 'PUT',
        headers: {
            'X-CSRFToken': csrfToken  // Include the CSRF token in the headers
            // 'Content-Type': 'multipart/form-data' // Do not set Content-Type header manually; FormData sets it
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {

    })
    .catch(error => {
        console.error('Error:', error);
    });

}

function typingSpeedEngine(user_record) {
    let previousMistakesCount = 0;
    let acceptedCharsCount = 0;
    let mistakesCount = 0;
    let finalWPM = 0;
    let startTime;
    let gameOn = true;

    let skipKeySoft = ['Shift', 'CapsLock',];
    let skipKeyHard = ['Tab', 'Shift', 'Meta', 'Alt', 'CapsLock', 'ArrowUp', 'ArrowLeft', 'ArrowDown', 'ArrowRight'];

    $('#typing_speed_testMSGbttn').addClass('hidden');
    $('#typing_speed_testMSG').html('Press ENTER to start');
    $('#typing_speed_testPrevious').html(user_record + ' wpm');

    document.addEventListener('keydown', function(event) {
        if (!gameOn) return;  // Exit if the game is not on

        if (!skipKeySoft.includes(event.key)) {

            if ($('.gasam.tst.chars').hasClass('active')) {

                var firstClass = $('.gasam.tst.chars.active').attr('class').split(' ')[0];
                var currentChar = $('.gasam.tst.chars.active').html();
                var currentCharNumber = firstClass.match(/\d+/)[0];


                if (currentChar == event.key) {
                    $('.gasam.tst.chars.active').addClass('good');
                } else {
                    $('.gasam.tst.chars.active').addClass('bad');
                    mistakesCount++;
                }
                finalWPM = wordsCountEngine(mistakesCount, startTime);

                $('#typing_speed_testMistakes').html(mistakesCount);
                $('#typing_speed_testCurrent').html( finalWPM + ' wpm');

                if ($('.gasam.tst.chars.active').is('.gasam.tst.chars:last')) {
                    $('.gasam.tst.chars').removeClass('active');
                    $('#typing_speed_testMSGcontainer').slideDown(100);
                    $('#typing_speed_testMSG').html('🎉 Test is over 🎉');
                    $('#typing_speed_testMSGbttn').removeClass('hidden');
                    userUpdateScore(finalWPM);
                    gameOn = false;
                    $(document).off('keydown');
                    return;
                } else {
                    $('.gasam.tst.chars').removeClass('active');
                    currentCharNumber ++;
                    $('.gasam.tst.chars.char-'+currentCharNumber).addClass('active');
                }
            }


            if (event.key === 'Enter') {
                if (gameOn) {
                    if (!$('.gasam.tst.chars').hasClass('active')) {
                        startTime = Date.now();
                        $('.char-0.gasam.tst.chars').addClass('active');
                        $('#typing_speed_testMSGcontainer').slideUp(100);
                    }
                }
            }
        }
    });

    function wordsCountEngine(mistakesCount, startTime) {
        var timeNow = Date.now();
        var timeDifference = timeNow - startTime;
        var fractionMultiplier = 60000 / timeDifference;

        if (mistakesCount == previousMistakesCount) {
            acceptedCharsCount ++;
        }
        previousMistakesCount = mistakesCount;

        var wordsCount = acceptedCharsCount / 5;
        var wordsPerMinute = Math.floor(wordsCount * fractionMultiplier);
        return wordsPerMinute;
    }
}



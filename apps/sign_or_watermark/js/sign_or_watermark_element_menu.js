let clickedInside = false;

document.addEventListener('mousedown', function(event) {
    const element_menu_container = document.querySelector('.sign_or_watermark.elem_menu.main-container');
    // Check if the click started inside any of the `.sign_or_watermark.add_element` elements
    document.querySelectorAll('.sign_or_watermark.watermarkElement').forEach(added_element => {

        if (added_element.contains(event.target) ) {
            $('.sign_or_watermark.watermarkElement').removeClass('active');
            added_element.classList.add('active');
            showElementMenu(added_element);
        }

        if (added_element.contains(event.target) || element_menu_container.contains(event.target)) {
            clickedInside = true; // Mark as clicked inside

        }
    });
});

document.addEventListener('mouseup', function(event) {
    if (!clickedInside) {
        document.querySelectorAll('.sign_or_watermark.watermarkElement').forEach(added_element => {
            if (!added_element.contains(event.target)) {
                hideElementMenu(added_element);
                added_element.classList.remove('active');
            }
        });
    }
    clickedInside = false; // Reset after every click
});

document.querySelector('#sign_or_watermark_delete_elem').addEventListener('click', function() {

    if ($('.sign_or_watermark.watermarkElement.active')) {
        $('.sign_or_watermark.watermarkElement.active').remove();
        $('.sign_or_watermark.elem_menu.main-container').addClass('hidden');
        $('.sign_or_watermark.elem_menu_container').hide();
    }
});

function showElementMenu(thisElement) {

console.log(thisElement);

    $('.sign_or_watermark.elem_menu.main-container').removeClass('hidden');
    $('.sign_or_watermark.elem_menu_container.text_menu').hide();

    if (thisElement.classList.contains('watermarkText')) {

        $('.sign_or_watermark.elem_menu_container.text_menu').show();

        var font_family = thisElement.getAttribute('font-family');
        var text_opacity = thisElement.getAttribute('opacity');

        document.querySelectorAll('.sign_or_watermark.watermarkText.active').forEach(added_element => {
            manipulateTextFont(added_element);
            $('#colorGrid').css('background-color', $('.sign_or_watermark.watermarkText.active').attr('fill'));
            $('#fontSizeInput').val($('.sign_or_watermark.watermarkText.active').attr('font-size'));
            var font = $('.sign_or_watermark.watermarkText.active').attr('font-family');
            var displayHTML = `
                <div class="font-preview-display" style="font-family: '${font}';">Ag</div>
                <div class="font-name-display">${font}</div>
            `;
            $('#fontDisplayholder').html(displayHTML);
        });

        // Set font size from dropdown
        document.querySelectorAll('.dropdown-item').forEach(item => {
            item.addEventListener('click', function() {
                $('#increaseFont').off('click');
                $('#decreaseFont').off('click');
                var chosen_val = this.getAttribute('data-size');
                document.getElementById('fontSizeInput').value = chosen_val;

                const activethisElement = document.querySelector('.sign_or_watermark.watermarkText.active');
                if (activethisElement) {
                    activethisElement.setAttribute('font-size', chosen_val);
                }
            });
        });
    } else if (thisElement.classList.contains('watermarkImage')) {
        $('.sign_or_watermark.elem_menu_container.image_menu').show();
    }
}

function hideElementMenu(textElement) {
    $('.sign_or_watermark.elem_menu.main-container').addClass('hidden');
}


function manipulateTextFont(textElement) {
    const fontSizeInput = document.getElementById('fontSizeInput');

    function increaseFontHandler() {
        var currentValue = textElement.getAttribute('font-size');
        fontSizeInput.value = parseInt(currentValue) + 1;
        textElement.setAttribute('font-size', fontSizeInput.value);
    };

    function decreaseFontHandler() {
        var currentValue = textElement.getAttribute('font-size');
        fontSizeInput.value = parseInt(currentValue) - 1;
        textElement.setAttribute('font-size', fontSizeInput.value);
    };

    // Clear previous listeners and bind new ones
    $('#increaseFont').off('click').on('click', increaseFontHandler);
    $('#decreaseFont').off('click').on('click', decreaseFontHandler);
};


const colors = [
    '#FFFFFF', '#F9F9F9', '#F2F2F2', '#E5E5E5', '#D6D6D6', '#C1C1C1', '#A8A8A8', '#8C8C8C', '#707070', '#545454',
    '#383838', '#1C1C1C', '#000000', '#FF0000', '#FF6600', '#FFCC00', '#99FF00', '#00FF66', '#00CCCC', '#0066FF',
    '#6600FF', '#CC00FF', '#FF00CC', '#FF0066', '#FF3300', '#FF6600', '#FF9900', '#FFCC00', '#FFFF00', '#CCFF00',
    '#66FF00', '#00FF00', '#00FF66', '#00FFCC', '#00CCFF', '#0066FF', '#3300FF', '#6600FF', '#9900FF', '#CC00FF'
];

const colorGrid = document.getElementById('colorGrid');
const selectedColorDisplay = document.getElementById('selected-color');

colors.forEach(color => {
    const cell = document.createElement('li');
    cell.className = 'color-cell';
    cell.style.backgroundColor = color;
    cell.addEventListener('click', () => {
        colorGrid.style.backgroundColor = color;
        $('.sign_or_watermark.watermarkText.active').attr('fill', color );
    });
    selectedColorDisplay.appendChild(cell);
});

$(document).ready(function () {
    var $dropdownColorBttn = $('#colorGrid');
    var $dropdownColorMenu = $dropdownColorBttn.next('#selected-color');

    $dropdownColorBttn.on('show.bs.dropdown', function () {
        $dropdownColorMenu.addClass('grid-layout');
    });

    $dropdownColorBttn.on('hide.bs.dropdown', function () {
        $dropdownColorMenu.removeClass('grid-layout');
    });

});


const fonts = [
    'Arial', 'Helvetica', 'Times New Roman', 'Courier New', 'Verdana',
    'Georgia', 'Palatino', 'Garamond', 'Bookman', 'Comic Sans MS',
    'Trebuchet MS', 'Arial Black', 'Impact'
];

const fontGrid = document.getElementById('font-grid');
const searchBar = document.getElementById('search-bar');

function createFontGrid(fonts) {
    fontGrid.innerHTML = '';
    fonts.forEach(font => {
        const fontItem = document.createElement('div');
        fontItem.className = 'font-item';
        fontItem.innerHTML = `
            <div class="font-preview" style="font-family: '${font}';">Ag</div>
            <div class="font-name">${font}</div>
        `;
        fontGrid.appendChild(fontItem);
        fontItem.addEventListener('click', () => {
            $('#fontDisplay').css('font-family', font );
            var displayHTML = `
                <div class="font-preview-display" style="font-family: '${font}';">Ag</div>
                <div class="font-name-display">${font}</div>
            `;
            $('#fontDisplayholder').html(displayHTML);
            $('.sign_or_watermark.watermarkText.active').attr('font-family', font );
        });
    });
}

function filterFonts(query) {
    return fonts.filter(font =>
        font.toLowerCase().includes(query.toLowerCase())
    );
}

searchBar.addEventListener('input', (e) => {
    const filteredFonts = filterFonts(e.target.value);
    createFontGrid(filteredFonts);
});

createFontGrid(fonts);

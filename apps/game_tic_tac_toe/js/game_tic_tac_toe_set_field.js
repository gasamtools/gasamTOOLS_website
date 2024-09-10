document.addEventListener("DOMContentLoaded", () => {
    function updatePathBasedOnSvgWidth() {
        // Get the SVG element
        var svgElement = document.getElementById('game_tic_tac_toe_svg_element');

        // Get the width of the SVG element
        var svgWidth = svgElement.clientWidth;
        var segment = Math.floor(svgWidth / 3);
        var numberOfPaths = 12;

        for (var i=0; i < numberOfPaths; i++) {
            if (i < 6) {
                var mx = segment * Math.floor(i/2);
                var my = segment + (segment * (i % 2));
                var lx = segment + segment * Math.floor(i/2);
                var ly = segment + (segment * (i % 2));
            }
            if (i >= 6) {
                var mx = segment + (segment * (i % 2));
                var my = segment * (i % 3);
                var lx = segment + (segment * (i % 2));
                var ly = segment + segment * (i % 3);
            }
            var pathData = `M${mx},${my}L${lx},${ly}`;
            var pathElement = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            pathElement.setAttribute('d', pathData);
            pathElement.setAttribute('class', "game_tic_tac_toe path grid");
            svgElement.appendChild(pathElement);
        }

        $('td.game_tic_tac_toe.td').css('height', segment+'px')

    }

    // Call the function to set the initial path
    updatePathBasedOnSvgWidth();


});
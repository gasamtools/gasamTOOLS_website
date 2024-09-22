document.addEventListener('DOMContentLoaded', function() {
    const elements_watermarkText = document.querySelectorAll('.sign_or_watermark.watermarkText');
    elements_watermarkText.forEach(element_watermarkText => {
        if (element_watermarkText) {
            addDoubleClickListener(element_watermarkText);
            enableMoving(element_watermarkText);
        }
    });
});

function addDoubleClickListener(textElement) {
    textElement.addEventListener('dblclick', function() {

        //deleteHandlesForElement(textElement);
        // get last class
        const textElementLastClass = textElement.classList.toString(); // Converts the classList to a string
        // Get current text content
        const currentText = textElement.textContent.trim().replace(/\s+/g, ' ');

        // Get bounding box to match the input element's position and size
        const svg = document.getElementById('watermarkCanvas');
        const svgRect = svg.getBoundingClientRect();
        const textRect = textElement.getBBox();
        const x = textRect.x;
        const y = textRect.y;
        const width = textRect.width;
        const height = textRect.height;

        // Create foreignObject element
        const input = document.createElementNS('http://www.w3.org/2000/svg', 'foreignObject');
        input.setAttribute('x', x);
        input.setAttribute('y', y);
        input.setAttribute('width', width);
        input.setAttribute('height', height);
        input.setAttribute('class', 'sign_or_watermark_editable-text');

        // Create HTML input element
        const htmlInput = document.createElement('input');
        htmlInput.setAttribute('type', 'text');
        htmlInput.setAttribute('value', currentText);
        htmlInput.style.width = '100%';
        htmlInput.style.height = '100%';
        htmlInput.style.border = 'none';
        htmlInput.style.margin = '0';
        htmlInput.style.padding = '0';
        htmlInput.style.boxSizing = 'border-box';
        htmlInput.style.position = 'absolute';
        htmlInput.style.top = '0';
        htmlInput.style.left = '0';
        htmlInput.style.whiteSpace = 'nowrap';
        htmlInput.style.overflow = 'hidden';

        // Copy CSS attributes from textElement to htmlInput
        const computedStyles = window.getComputedStyle(textElement);
        htmlInput.style.fontSize = computedStyles.fontSize;
        htmlInput.style.fontFamily = computedStyles.fontFamily;
        htmlInput.style.color = computedStyles.fill;
        htmlInput.style.opacity = computedStyles.opacity;
        htmlInput.style.textAlign = 'center';

        input.appendChild(htmlInput);
        textElement.parentNode.replaceChild(input, textElement);

        htmlInput.focus();

        // Adjust size based on content
        htmlInput.addEventListener('input', function() {
            const tempSpan = document.createElement('span');
            tempSpan.style.fontSize = htmlInput.style.fontSize;
            tempSpan.style.fontFamily = htmlInput.style.fontFamily;
            tempSpan.style.visibility = 'hidden';
            tempSpan.style.whiteSpace = 'nowrap';
            tempSpan.textContent = htmlInput.value;

            document.body.appendChild(tempSpan);
            const newWidth = tempSpan.getBoundingClientRect().width + 10;
            document.body.removeChild(tempSpan);

            input.setAttribute('width', newWidth);
            htmlInput.style.width = '100%';
        });

        // Capture htmlInput position and size
        htmlInput.addEventListener('blur', function() {
            const inputRect = htmlInput.getBoundingClientRect();
            const inputX = inputRect.left - svgRect.left;
            const inputY = inputRect.top - svgRect.top;

            // Re-create the text element with new content
            const newTextElement = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            newTextElement.setAttribute('class', textElementLastClass);
            newTextElement.setAttribute('x', inputX);
            newTextElement.setAttribute('y', inputY + 37);
            newTextElement.setAttribute('font-size', htmlInput.style.fontSize);
            newTextElement.setAttribute('font-family', htmlInput.style.fontFamily);
            newTextElement.setAttribute('fill', htmlInput.style.color);
            newTextElement.setAttribute('opacity', htmlInput.style.opacity);
            newTextElement.setAttribute('text-anchor', 'start');
            newTextElement.textContent = htmlInput.value.trim().replace(/\s+/g, ' ');

            input.parentNode.replaceChild(newTextElement, input);

            // Reattach the double-click listener and moving functionality
            addDoubleClickListener(newTextElement);
            enableMoving(newTextElement);
            //manipulateTextFont(newTextElement);

        });
    });
}

function enableMoving(thisElement) {
    const svg = document.getElementById('watermarkCanvas');

    // Create handles for this specific text element
    const handles = createHandlesForElement(thisElement);
    if (thisElement.classList.contains('watermarkImage')) {
        enableResizing(thisElement, handles);
    }


    let isDragging = false;
    let startX, startY, startLeft, startTop;

    function showHandles() {
        handles.forEach(handle => handle.style.display = 'block');
        updateHandles();
    }

    function hideHandles() {
        handles.forEach(handle => handle.style.display = 'none');
    }

    function onMouseDown(event) {
        event.preventDefault();

        if (event.target === thisElement) {
            if (isDragging) {
                return;
            }
            showHandles();
            isDragging = true;
            startX = event.clientX;
            startY = event.clientY;
            startLeft = parseFloat(thisElement.getAttribute('x'));
            startTop = parseFloat(thisElement.getAttribute('y'));
            svg.addEventListener('mousemove', onMouseMove);
            svg.addEventListener('mouseup', onMouseUp);

        } else {
            hideHandles();
        }
    }

    function onMouseMove(event) {
        if (isDragging) {
            const dx = event.clientX - startX;
            const dy = event.clientY - startY;
            thisElement.setAttribute('x', startLeft + dx);
            thisElement.setAttribute('y', startTop + dy);
            updateHandles();
        }
    }

    function onMouseUp() {
        isDragging = false;
        svg.removeEventListener('mousemove', onMouseMove);
        svg.removeEventListener('mouseup', onMouseUp);

    }

    function updateHandles() {
        const bbox = thisElement.getBBox();
        handles[0].setAttribute('cx', bbox.x);
        handles[0].setAttribute('cy', bbox.y);
        handles[1].setAttribute('cx', bbox.x + bbox.width);
        handles[1].setAttribute('cy', bbox.y + bbox.height);
    }

    thisElement.addEventListener('mousedown', onMouseDown);

    // Hide handles initially
    hideHandles();


    // Add click event listener to the document to hide handles when clicking outside
    document.addEventListener('click', function(event) {
        if (!thisElement.contains(event.target) && !handles.some(handle => handle.contains(event.target))) {
            hideHandles();
        }
    });
}

function createHandlesForElement(textElement) {
    const svg = document.getElementById('watermarkCanvas');
    const handles = [];

    for (let i = 0; i < 2; i++) {
        const handle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        handle.setAttribute('r', '5');
        handle.setAttribute('fill', 'blue');
        handle.style.display = 'none';
        handle.classList.add('selection-corner');
        handle.classList.add(i === 0 ? 'handle-top-left' : 'handle-bottom-right');
        svg.appendChild(handle);
        handles.push(handle);
    }

    return handles;
}

function deleteHandlesForElement(textElement) {
        // Select all <circle> elements inside the SVG
    const circles = document.querySelectorAll('svg circle');

    // Loop through each circle and remove it
    circles.forEach(circle => {
        circle.remove();  // Alternatively: circle.parentNode.removeChild(circle);
    });
}
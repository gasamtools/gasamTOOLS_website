function enableResizing(element, handles) {
    const svg = document.getElementById('watermarkCanvas');
    let isResizing = false;
    let currentHandle = null;
    let startX, startY, startBBox;

    function onHandleMouseDown(event) {
        event.stopPropagation();
        event.preventDefault();
        isResizing = true;
        currentHandle = event.target;
        startX = event.clientX;
        startY = event.clientY;
        startBBox = element.getBBox();

        svg.addEventListener('mousemove', onMouseMove);
        svg.addEventListener('mouseup', onMouseUp);
    }

    function onMouseMove(event) {
        if (!isResizing) return;

        const dx = event.clientX - startX;
        const dy = event.clientY - startY;

        let newX = startBBox.x;
        let newY = startBBox.y;
        let newWidth = startBBox.width;
        let newHeight = startBBox.height;

        if (currentHandle === handles[0]) { // Top-left handle
            newX = Math.min(startBBox.x + dx, startBBox.x + startBBox.width - 20);
            newY = Math.min(startBBox.y + dy, startBBox.y + startBBox.height - 20);
            newWidth = startBBox.x + startBBox.width - newX;
            newHeight = startBBox.y + startBBox.height - newY;
        } else if (currentHandle === handles[1]) { // Bottom-right handle
            newWidth = Math.max(dx + startBBox.width, 20);
            newHeight = Math.max(dy + startBBox.height, 20);
        }

        element.setAttribute('x', newX);
        element.setAttribute('y', newY);
        element.setAttribute('width', newWidth);
        element.setAttribute('height', newHeight);

        updateHandles();
    }

    function onMouseUp() {
        isResizing = false;
        currentHandle = null;
        svg.removeEventListener('mousemove', onMouseMove);
        svg.removeEventListener('mouseup', onMouseUp);
    }

    function updateHandles() {
        const bbox = element.getBBox();
        handles[0].setAttribute('cx', bbox.x);
        handles[0].setAttribute('cy', bbox.y);
        handles[1].setAttribute('cx', bbox.x + bbox.width);
        handles[1].setAttribute('cy', bbox.y + bbox.height);
    }

    // Add resize functionality to existing handles
    handles.forEach(handle => {
        handle.addEventListener('mousedown', onHandleMouseDown);
        handle.style.cursor = 'nwse-resize';
    });

    // Initial update of handles
    updateHandles();
}
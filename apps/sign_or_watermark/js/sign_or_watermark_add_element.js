document.addEventListener('DOMContentLoaded', function() {
    //const parentElement = document.getElementById('watermarkCanvas');
    let added_element_count = 0;
    addNewElementListener(added_element_count);
});

function addNewElementListener(added_element_count) {
    const parentElement = document.getElementById('watermarkCanvas');
    const elements_add_element = document.querySelectorAll('.sign_or_watermark.add_element');

    elements_add_element.forEach(add_element => {
        if (add_element) {
            add_element.addEventListener('click', function() {



                const thisElementLastClass = add_element.classList[add_element.classList.length - 1];

                if (thisElementLastClass == 'add_text') {
added_element_count ++;
console.log(added_element_count);
                    var textElements = parentElement.querySelectorAll('.sign_or_watermark.watermarkText');
                    var newElementClass = 'sign_or_watermark watermarkElement watermarkText element-'+added_element_count+' wt-' + (textElements.length + 1);

                    const newText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                    newText.setAttribute('x', '0');
                    newText.setAttribute('y', '40');
                    newText.setAttribute('class', newElementClass);
                    newText.setAttribute('font-size', '40');
                    newText.setAttribute('font-family', 'Arial');
                    newText.setAttribute('fill', '#000');
                    newText.setAttribute('opacity', '1');
                    newText.textContent = "Your Text";

                    parentElement.appendChild(newText);

                    // Add interaction to the new element
                    addDoubleClickListener(newText);
                    enableMoving(newText);
                    //manipulateTextFont(newText);
                }
                else if (thisElementLastClass == 'add_picture') {

                    var imageElements = parentElement.querySelectorAll('.sign_or_watermark.watermarkImage');
                    var nextElemClass = imageElements.length + 1;


                    const fileInput = document.getElementById('logoInput');
                    fileInput.click();
                    fileInput.addEventListener('change', (event) => {
                        const file = event.target.files[0];
                        if (file) {
                            const reader = new FileReader();

                            // When the file is read, display the image inside the SVG
                            reader.onload = function(e) {

                                const imgDataURL = e.target.result;
                                const newImage = document.createElementNS('http://www.w3.org/2000/svg', 'image');
                                newImage.setAttributeNS(null, 'href', imgDataURL);  // Set image source (for Firefox and modern browsers)
                                newImage.setAttributeNS(null, 'preserveAspectRatio', 'none');
                                newImage.setAttributeNS(null, 'x', 0);              // Set x position
                                newImage.setAttributeNS(null, 'y', 0);              // Set y position
                                newImage.setAttributeNS(null, 'width', 400);        // Set width of the image
                                //newImage.setAttributeNS(null, 'height', 300);       // Set height of the image

                                // Append the image to the SVG container
                                if ($('.sign_or_watermark.watermarkImage.wi-'+nextElemClass).length === 0) {
                                    added_element_count ++;
                                    var newElementClass = 'sign_or_watermark watermarkElement watermarkImage element-'+added_element_count+' wi-' + nextElemClass;
                                    newImage.setAttribute('class', newElementClass);
                                    parentElement.appendChild(newImage);

console.log(added_element_count);
                                }
                                enableMoving(newImage);
                                //enableResizing(newImage);

                            };

                            // Read the image file as a data URL
                            reader.readAsDataURL(file);


                        }
                    });

                }



            });
        }
    });
}
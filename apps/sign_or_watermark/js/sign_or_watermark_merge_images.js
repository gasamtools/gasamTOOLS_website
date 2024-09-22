document.addEventListener('DOMContentLoaded', function() {

    const mergeButton = document.getElementById('sign_or_watermark_merge_button');
    const processedImage = document.getElementById('processedImagePreview');
    const imagePreview = document.getElementById('imagePreview');
    const finalSvg = document.getElementById('watermarkCanvasFinal');
    const downloadImage = document.getElementById('sign_or_watermark_download_image_button');


    mergeButton.addEventListener('click', function() {

        const imageHref = imagePreview.getAttribute('href');
        const virtual_img = new Image();
        virtual_img.src = imageHref;

        if (!virtual_img.complete || !virtual_img.naturalWidth) {
            console.error('Image not loaded yet');
            return;
        }

        // Get the actual dimensions of the image
        const imgWidth = virtual_img.naturalWidth;
        const imgHeight = virtual_img.naturalHeight;

        const rszdbox = imagePreview.getBBox();
        const rszdWidth = rszdbox.width;
        const rszdHeight = rszdbox.height;

        const svg = document.getElementById('watermarkCanvas');

        const watermarkData = {
            js_function: 'sign_or_watermark_merge_images',
            imgWidth: imgWidth,
            imgHeight: imgHeight,
        };

        var count = 0;
        const elements_watermarkText = document.querySelectorAll('.sign_or_watermark.watermarkText');
        elements_watermarkText.forEach(currentTextElement => {

            // extracting number from the 'element-...' class of element
            let element_number = null;
            for (const className of currentTextElement.classList) {
                const match = className.match(/element-(\d+)/);
                if (match) {
                    element_number = match[1]; // Extracted number
                    break; // Exit loop once the number is found
                }
            }

            if (currentTextElement) {

                var bbox = currentTextElement.getBBox();
                var currentTextElemData = {
                    text: currentTextElement.textContent,
                    x: bbox.x / rszdWidth,
                    y: bbox.y / rszdHeight,
                    width: bbox.width / imgWidth,
                    height: bbox.height / imgHeight,
                    fontSize: parseFloat(currentTextElement.getAttribute('font-size')) / rszdHeight,
                    fontFamily: currentTextElement.getAttribute('font-family'),
                    color: currentTextElement.getAttribute('fill'),
                    opacity: currentTextElement.getAttribute('opacity'),
                }

                if (element_number) {
                    watermarkData[`element_${element_number}_text`] = currentTextElemData;
                } else {
                    watermarkData['element_0_text'] = currentTextElemData;
                }


            }
        });

        count = 0;
        const elements_watermarkImages = document.querySelectorAll('.sign_or_watermark.watermarkImage');
        elements_watermarkImages.forEach(currentImageElement => {

                    // extracting number from the 'element-...' class of element
            let element_number = null;
            for (const className of currentImageElement.classList) {
                const match = className.match(/element-(\d+)/);
                if (match) {
                    element_number = match[1]; // Extracted number
                    break; // Exit loop once the number is found
                }
            }

            if (currentImageElement) {

                var bbox = currentImageElement.getBBox();
                var currentImageElemData = {
                    x: bbox.x / rszdWidth,
                    y: bbox.y / rszdHeight,
                    width: bbox.width / rszdWidth,
                    height: bbox.height / rszdHeight,
                    url: currentImageElement.getAttribute('href'),
                }

                if (element_number) {
                    watermarkData[`element_${element_number}_image`] = currentImageElemData;
                } else {
                    watermarkData['element_0_image'] = currentImageElemData;
                }
            }
        });

console.log(watermarkData);

        var csrfToken = $('meta[name="csrf-token"]').attr('content');
        fetch(GASAM_sign_or_watermark_URL, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(watermarkData),
        })
        .then(response => response.json())
        .then(data => {
            processedImage.setAttribute('href', data['img_src']);
            $('.sign_or_watermark.step-container.second').hide();
            $('.sign_or_watermark.step-container.third').css('display', 'flex').show();

            const updatedStoredImage = document.getElementById('processedImagePreview');
            updatedStoredImage.onload = function() {
                const rszdbox = updatedStoredImage.getBBox();
                const rszdWidth = rszdbox.width;
                const rszdHeight = rszdbox.height;
                finalSvg.setAttribute('height', rszdHeight);
            };
            downloadImage.setAttribute('href', data['download_img']);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});
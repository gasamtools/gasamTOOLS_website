document.addEventListener("DOMContentLoaded", () => {
    const watermarkForm = document.getElementById('watermarkForm');
    const storedImage = document.getElementById('imagePreview');
    const UploadFileButton = document.getElementById('UploadFileButton');
    const svg = document.getElementById('watermarkCanvas');

    watermarkForm.addEventListener('submit', function(e) {
        e.preventDefault();


        // Get CSRF token from meta tag
        var csrfToken = $('meta[name="csrf-token"]').attr('content');

        const formData = new FormData(this);
        formData.append('js_function', 'sign_or_watermark_ini'); // Append additional data if needed

        fetch(GASAM_sign_or_watermark_URL, {
            method: 'PUT',
            headers: {
                'X-CSRFToken': csrfToken  // Include the CSRF token in the headers
                // 'Content-Type': 'multipart/form-data' // Do not set Content-Type header manually; FormData sets it
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            storedImage.setAttribute('href', data['img_src']);

            $('.sign_or_watermark.step-container.first').hide();
            $('.sign_or_watermark.step-container.second').css('display', 'flex').show();

            const updatedStoredImage = document.getElementById('imagePreview');
            updatedStoredImage.onload = function() {
                const rszdbox = updatedStoredImage.getBBox();
                const rszdWidth = rszdbox.width;
                const rszdHeight = rszdbox.height;
                svg.setAttribute('height', rszdHeight);
            };

        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    const fileNameDisplay = document.getElementById('fileName');
    document.getElementById('imageInput').addEventListener('change', function(event) {
        const file = event.target.files[0]; // Get the file
        const validFileTypes = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'];

        if (file && !validFileTypes.includes(file.type)) {
          document.getElementById('error-message').textContent = 'Invalid file type. Please upload an image or PDF.';
          event.target.value = ''; // Clear the input

        } else {
          document.getElementById('error-message').textContent = ''; // Clear error message
        }

        if (file) {
            fileNameDisplay.textContent = `Selected file: ${file.name}`;
            UploadFileButton.disabled = false;
        } else {
            fileNameDisplay.textContent = '';
        }
    });
});
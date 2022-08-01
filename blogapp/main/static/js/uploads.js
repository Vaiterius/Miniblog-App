document.addEventListener("DOMContentLoaded", function() {
    const postSubmitButton = document.querySelector(".submit-post");

    postSubmitButton.addEventListener("click", function() {
        tinymce.activeEditor.uploadImages().then(() => {
            document.forms[0].submit();
        });
    });
});
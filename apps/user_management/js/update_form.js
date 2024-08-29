document.addEventListener("DOMContentLoaded", () => {

    var forms = document.getElementsByClassName('gasam form');

    for (var i = 0; i < forms.length; i++) {
        forms[i].addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent the form from submitting the traditional way

            // Get CSRF token from meta tag
            var csrfToken = $('meta[name="csrf-token"]').attr('content');

            const formData = new FormData(this);
            const formObject = {'js_function': 'update_form'};
            formData.forEach((value, key) => {
                formObject[key] = value;
            });


            var form = this; // 'this' refers to the form that triggered the event
            var classList = form.classList; // Get the classList of the form
            var target = classList[classList.length - 2];
            var user = classList[classList.length - 1];
            var condition = classList[classList.length - 3];
            if (target == 'user_apps') {
                var button = $('button.gasam.' + target + '.' + user + '.' + condition);
                var available_select = $('select.gasam.user_apps-select.available.' + user);
                var added_select = $('select.gasam.user_apps-select.added.' + user);
            } else {
                var button = $('button.gasam.' + target + '.' + user);
            }
            var buttonHTML = button.html();
            button.addClass('btn-loading').attr('disabled', true);
            button.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...');


            function performFetch(buttonHTML) {
                fetch(GASAM_apps_app_management_scripts_URL, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json' ,
                        'X-CSRFToken': csrfToken  // Include the CSRF token in the headers
                    },
                    body: JSON.stringify(formObject)
                })
                .then(response => response.json())
                .then(data => {
                    button.removeClass('btn-loading').attr('disabled', false);
                    if (data['target'] == 'approved') {
                        var this_bttn_html = data['status'].charAt(0).toUpperCase() + data['status'].slice(1).toLowerCase();
                        button.html(this_bttn_html);
                        $('.gasam.input.status.approved.'+user).val(data['status']);
                        $('.gasam.p.status.approved.'+user).html(data['response']);

                        if (data['status'] == 'approve') {
                            $('tr.gasam.user_management.'+user).addClass('not-approved')
                        } else {
                            $('tr.gasam.user_management.'+user).removeClass('not-approved')
                        }
                    } else if (data['target'] == 'delete_user') {
                        $('tr.gasam.user_management.'+user).remove()
                    } else if (data['target'] == 'user_apps') {

                        available_select.removeClass('highlight-border');
                        added_select.removeClass('highlight-border');

                        if (data['user_apps_available']) {
                            var optionToMove = available_select.find('option[value="'+data['user_apps_available']+'"]');
                            if (optionToMove.length) {
                                optionToMove.remove();
                                added_select.append(optionToMove);
                            }
                            var remove_app_button = $('.gasam.user_apps-bttn.added.user_apps.'+user);
                            if (remove_app_button.prop('disabled')) {
                                   remove_app_button.prop('disabled', false);
                                   remove_app_button.removeClass('btn-secondary');
                                   var existingClasses = remove_app_button.attr('class');
                                   remove_app_button.attr('class', 'btn-danger' + ' ' + existingClasses);
                            }
                        } else if (data['user_apps_added']) {
                            var optionToMove = added_select.find('option[value="'+data['user_apps_added']+'"]');
                            if (optionToMove.length) {
                                optionToMove.remove();
                                available_select.append(optionToMove);
                            }

                            var options = added_select.find('option');
                            var hasOptionsWithValues = options.filter(function() {
                                return $(this).val().trim() !== '';
                            }).length > 0;
                            if (!hasOptionsWithValues) {
                                   button.prop('disabled', true);
                                   button.removeClass('btn-danger');
                                   var existingClasses = button.attr('class');
                                   button.attr('class', 'btn-secondary' + ' ' + existingClasses);
                            }
                        }

                        $('div.row.gasam.user_apps.'+user).html(data['user_apps_html'])
                        button.html(buttonHTML);
                    } else {
                        button.html(buttonHTML);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }

            if (formObject['target'] == 'user_apps') {
                if (formObject['user_apps_available'] =='' || formObject['user_apps_added'] =='' ) {
                    if (formObject['user_apps_available'] =='') {
                        available_select.addClass('highlight-border');
                    }
                    if (formObject['user_apps_added'] =='') {
                        added_select.addClass('highlight-border');
                    }
                    button.removeClass('btn-loading').attr('disabled', false);
                    button.html(buttonHTML);
                } else {
                    performFetch(buttonHTML);
                }
            } else {
                performFetch(buttonHTML);
            }

        });
    }
});
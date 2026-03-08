(function($) {
    $(document).ready(function() {
        // Handle tab navigation from URL hash
        const hash = window.location.hash;
        if (hash) {
            const tabId = hash.substring(1); // Remove the # symbol
            
            // Try to find and activate the tab
            const tab = $(`.admin-tab[data-tab="${tabId}"]`);
            if (tab.length) {
                activateTab(tab);
            } else {
                // Try to find fieldset with matching ID
                const fieldset = $(`fieldset[id="${tabId}"]`);
                if (fieldset.length) {
                    expandFieldset(fieldset);
                    $('html, body').animate({
                        scrollTop: fieldset.offset().top - 100
                    }, 500);
                }
            }
        }
        
        // Handle tab clicks
        $('.admin-tab').on('click', function(e) {
            e.preventDefault();
            activateTab($(this));
            
            // Update URL hash without page reload
            const tabId = $(this).data('tab');
            if (history.pushState) {
                history.pushState(null, null, '#' + tabId);
            } else {
                window.location.hash = tabId;
            }
        });
        
        // Handle fieldset collapse toggle
        $('fieldset.collapse h2').on('click', function() {
            const fieldset = $(this).closest('fieldset');
            toggleFieldset(fieldset);
        });
        
        // If URL hash points to a fieldset, expand it
        if (hash) {
            const fieldset = $(hash);
            if (fieldset.length && fieldset.hasClass('collapse')) {
                expandFieldset(fieldset);
            }
        }
        
        // Function to activate a tab
        function activateTab(tab) {
            const tabContainer = tab.closest('.admin-tabs');
            const tabContents = tabContainer.siblings('.tab-contents');
            const tabId = tab.data('tab');
            
            // Update tab active states
            tabContainer.find('.admin-tab').removeClass('active');
            tab.addClass('active');
            
            // Update content active states
            tabContents.find('.admin-tab-content').removeClass('active');
            $(`#tab-content-${tabId}`).addClass('active');
        }
        
        // Function to expand/collapse fieldset
        function toggleFieldset(fieldset) {
            fieldset.toggleClass('collapsed');
            const content = fieldset.find('.fieldset-content');
            if (fieldset.hasClass('collapsed')) {
                content.slideUp();
            } else {
                content.slideDown();
            }
        }
        
        // Function to expand a fieldset
        function expandFieldset(fieldset) {
            if (fieldset.hasClass('collapsed')) {
                fieldset.removeClass('collapsed');
                fieldset.find('.fieldset-content').slideDown();
            }
        }
    });
})(django.jQuery);
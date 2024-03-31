document.addEventListener("DOMContentLoaded", function() {
    const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');

    // Add event listener to each sidebar menu item
    allSideMenu.forEach(item => {
        item.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default link behavior

            // Remove 'active' class from all sidebar menu items
            allSideMenu.forEach(i => {
                i.parentElement.classList.remove('active');
            });

            // Add 'active' class to the clicked sidebar menu item
            item.parentElement.classList.add('active');

            // Hide all main sections
            document.querySelectorAll('main').forEach(section => {
                section.classList.add('hidden');
            });

            // Show the corresponding main section based on the clicked category
            const category = item.querySelector('.text').textContent.toLowerCase().trim();
            document.getElementById(`main-${category}`).classList.remove('hidden');
        });
    });

    // TOGGLE SIDEBAR
    const menuBar = document.querySelector('#content nav .bx.bx-menu');
    const sidebar = document.getElementById('sidebar');

    menuBar.addEventListener('click', function () {
        sidebar.classList.toggle('hide');
    });

    const searchButton = document.querySelector('#content nav form .form-input button');
    const searchButtonIcon = document.querySelector('#content nav form .form-input button .bx');
    const searchForm = document.querySelector('#content nav form');

    searchButton.addEventListener('click', function (e) {
        if(window.innerWidth < 576) {
            e.preventDefault();
            searchForm.classList.toggle('show');
            if(searchForm.classList.contains('show')) {
                searchButtonIcon.classList.replace('bx-search', 'bx-x');
            } else {
                searchButtonIcon.classList.replace('bx-x', 'bx-search');
            }
        }
    });

    if(window.innerWidth < 768) {
        sidebar.classList.add('hide');
    }

    window.addEventListener('resize', function () {
        if(this.innerWidth > 576) {
            searchButtonIcon.classList.replace('bx-x', 'bx-search');
            searchForm.classList.remove('show');
        }
    });
});

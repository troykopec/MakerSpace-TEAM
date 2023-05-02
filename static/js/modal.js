
          const scrollmenu = document.querySelector('.scrollmenu');
          let isDragging = false;
          let lastX;
          let selected = null; 
          const scrollMenu = document.querySelector('.scrollmenu');
          const leftArrow = document.querySelector('.scrollmenu__arrow--left');
          const rightArrow = document.querySelector('.scrollmenu__arrow--right');
          const eventButtons = document.querySelectorAll('.event-button');
          const buttonContainer = document.querySelector('.button-container');

          let reservations = [];
          
          
            fetch('/get_all_reservations')
              .then(response => response.json())
              .then(data => {
                reservations = data;
                console.log(reservations)
              })
              .catch(error => {
                console.error('Error:', error);
              });
          


              eventButtons.forEach(button => {
                button.addEventListener('click', () => {
                  // remove previously created buttons (if any)
                  buttonContainer.innerHTML = '';
              
                  const eventData = JSON.parse(button.dataset.event);
                  eventData.starts.forEach((start, i) => {
                  
                    const event_date_start = new Date(start.replace(/-/g, '/'));
                    const event_date_end = new Date(eventData['ends'][i].replace(/-/g, '/'));
                    const machine_id = eventData['machine-id'];
                    const event_id = eventData['event-id'][i].event_id;
                    const current_user = eventData['current-user'];
                    const is_admin = eventData['is-admin'];
                    const event_hour_start = event_date_start.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                    const event_hour_end = event_date_end.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                    const event_hour = (event_hour_start.replace(" AM", "").replace(" PM", "")) + " - " + event_hour_end;
                    let reservationFound = false;
                    for (let i = 0; i < reservations.length; i++) {
                      const reservation = reservations[i];
                      if (reservation.machineid === machine_id && reservation.selected_date === start && reservation.eventid === event_id) {
                        reservationFound = true;
                        break;
                      }
                    }
                    if (reservationFound && is_admin !== "Admin") {
                      const button = document.createElement('button');
                      button.textContent = event_hour;
                      button.classList.add('time_select', 'reserved');
                      button.disabled = true;
                      buttonContainer.appendChild(button);
                    } else {
                      const button = document.createElement('button');
                      button.textContent = event_hour;
                      button.classList.add('time_select');
                      button.dataset.eventDate_start = event_date_start; // set the event date as a data attribute on the button
                      button.dataset.machineId = machine_id; // set the machine ID as a data attribute on the button
                      button.dataset.eventId = event_id;
                      button.dataset.currentUser = current_user;
                      button.dataset.eventDate_end = event_date_end;
                      button.addEventListener('click', () => {
                        // remove the 'select' class from all buttons
                        buttonContainer.querySelectorAll('.time_select').forEach(btn => {
                          btn.classList.remove('selected');
                        });
                        // add the 'select' class to the clicked button
                        button.classList.add('selected');
                      });
                      buttonContainer.appendChild(button);
                    }
                  });
                });
              });

          document.getElementById('book-reservation').addEventListener('click', () => {
            const selectedButton = document.querySelector('.time_select.selected');
            if (selectedButton) {
              const selectedTime_start = new Date(selectedButton.dataset.eventDate_start);
              const selectedTime_end = new Date(selectedButton.dataset.eventDate_end);
              const machineId = selectedButton.dataset.machineId;
              const eventId = selectedButton.dataset.eventId;
              const currentUser = selectedButton.dataset.currentUser;
              // Send an AJAX request to Python backend
              const xhr = new XMLHttpRequest();
              xhr.open('POST', '/reserve/add', true);
              xhr.setRequestHeader('Content-Type', 'application/json');
              xhr.onreadystatechange = () => {
                if (xhr.readyState === 4 && xhr.status === 200) {
                  // handle the response from the server here
                  window.location.href = '/scheduled_reservations';
                  const response = JSON.parse(xhr.responseText);
                  console.log(response);
                }
              };
              xhr.send(JSON.stringify({ 
                  event_date_start: selectedTime_start,
                  event_date_end: selectedTime_end,
                  machine_id: machineId,
                  current_user: currentUser,
                  event_id: eventId
              }));
            } else {
              alert('Please select a time.');
            }
          });

          document.getElementById('del-reservation').addEventListener('click', () => {
            const selectedButton = document.querySelector('.time_select.selected');
            if (selectedButton) {
              const selectedTime_start = new Date(selectedButton.dataset.eventDate_start);
              const selectedTime_end = new Date(selectedButton.dataset.eventDate_end);
              const machineId = selectedButton.dataset.machineId;
              const eventId = selectedButton.dataset.eventId;
              const currentUser = selectedButton.dataset.currentUser;
              // Send an AJAX request to Python backend
              const xhr = new XMLHttpRequest();
              xhr.open('POST', '/delete_API_reservation', true);
              xhr.setRequestHeader('Content-Type', 'application/json');
              xhr.onreadystatechange = () => {
                if (xhr.readyState === 4 && xhr.status === 200) {
                  // handle the response from the server here
                  window.location.href = '/schedule';
                  const response = JSON.parse(xhr.responseText);
                  console.log(response);
                }
              };
              xhr.send(JSON.stringify({ 
                  event_date_start: selectedTime_start,
                  event_date_end: selectedTime_end,
                  machine_id: machineId,
                  current_user: currentUser,
                  event_id: eventId
              }));
            } else {
              alert('Please select a time.');
            }
          });


          // add event listeners to left and right arrows
          leftArrow.addEventListener('click', () => {
            // get the first visible element in the scrollmenu
            const firstVisibleElement = getFirstVisibleElement(scrollMenu);

            // get the number of visible elements in the scrollmenu
            const visibleElements = getVisibleElements(scrollMenu);

            // get the width of the first visible element
            const firstVisibleElementWidth = firstVisibleElement.offsetWidth;

            // scroll to the left by the total width of the visible elements
            scrollMenu.scrollTo({
            left: scrollMenu.scrollLeft - ((firstVisibleElementWidth + 10) * (visibleElements + 1)),
            behavior: 'smooth'
            });
          });

          rightArrow.addEventListener('click', () => {
            // get the first visible element in the scrollmenu
            const firstVisibleElement = getFirstVisibleElement(scrollMenu);

            // get the number of visible elements in the scrollmenu
            const visibleElements = getVisibleElements(scrollMenu);

            // get the width of the first visible element
            const firstVisibleElementWidth = firstVisibleElement.offsetWidth;

            // scroll to the right by the total width of the visible elements
            scrollMenu.scrollTo({
            left: scrollMenu.scrollLeft + ((firstVisibleElementWidth + 10) * (visibleElements + 1)),
            behavior: 'smooth'
            });
          });

          // helper function to get the first visible element in the scrollmenu
          function getFirstVisibleElement(scrollMenu) {
            const scrollMenuRect = scrollMenu.getBoundingClientRect();
            const scrollMenuChildren = scrollMenu.children;

            for (let i = 0; i < scrollMenuChildren.length; i++) {
              const childRect = scrollMenuChildren[i].getBoundingClientRect();

              if (childRect.left >= scrollMenuRect.left && childRect.right <= scrollMenuRect.right) {
                return scrollMenuChildren[i];
              }
            }

            return null;
          }

          // helper function to get the number of visible elements in the scrollmenu
          function getVisibleElements(scrollMenu) {
            const scrollMenuRect = scrollMenu.getBoundingClientRect();
            const scrollMenuChildren = scrollMenu.children;
            let visibleElements = 0;

            for (let i = 0; i < scrollMenuChildren.length; i++) {
              const childRect = scrollMenuChildren[i].getBoundingClientRect();

              if (childRect.left >= scrollMenuRect.left && childRect.right <= scrollMenuRect.right) {
                visibleElements++;
              }
            }

            return visibleElements;
          }



          scrollmenu.addEventListener('mousedown', e => {
            e.preventDefault(); // Prevents default behavior of selecting and dragging the element
            isDragging = true;
            lastX = e.clientX;
          });

          document.addEventListener('mouseup', e => {
            isDragging = false;
            scrollmenu.style.removeProperty('cursor'); // Remove cursor property
          });

          document.addEventListener('mousemove', e => {
            if (isDragging) {
              const delta = e.clientX - lastX;
              scrollmenu.scrollLeft -= delta;
              lastX = e.clientX;
            }
          });


          // add click event listener to each item
          const items = document.querySelectorAll('.scrollmenu a');
          items.forEach(item => {
            let startX;
            let isDragging = false;

            item.addEventListener('mousedown', e => {
              startX = e.clientX;
              isDragging = false;
            });

            item.addEventListener('mousemove', e => {
              if (isDragging) {
                e.preventDefault(); // prevent default dragging behavior
              }
              if (!isDragging && Math.abs(e.clientX - startX) > 5) {
                isDragging = true;
              }
            });



          let scrollTimeout = null;
          let snapTarget = null;
          let snapOffset = null;

          scrollmenu.addEventListener('scroll', () => {
            // Clear previous timeout to prevent multiple scrolls in rapid succession
            clearTimeout(scrollTimeout);

            // Find the snap target
            const snapTargets = document.querySelectorAll('.scrollmenu a');
            const containerWidth = scrollmenu.offsetWidth;
            const containerLeft = scrollmenu.offsetLeft;
            let minOffsetDiff = Infinity;
            for (let i = 0; i < snapTargets.length; i++) {
              const target = snapTargets[i];
              const targetOffset = target.offsetLeft - containerLeft;
              const offsetDiff = Math.abs(scrollmenu.scrollLeft - targetOffset);
              const middleOffset = targetOffset + (target.offsetWidth / 2) - (containerWidth / 2);
              const middleDiff = Math.abs(scrollmenu.scrollLeft - middleOffset);
              if (middleDiff < minOffsetDiff) {
                snapTarget = target;
                snapOffset = middleOffset;
                minOffsetDiff = middleDiff;
              }
            }

            // Scroll to the snap target after a short delay
            scrollTimeout = setTimeout(() => {
              if (snapTarget !== null) {
                if (window.innerWidth > 1082){
                if (selected === snapTargets[0] || selected === snapTargets[1] || selected === snapTargets[2] || snapTargets[snapTargets.length - 1] || snapTargets[snapTargets.length - 2] || snapTargets[snapTargets.length - 3]) {
                }
                else {
                scrollmenu.scrollTo({
                  left: snapOffset,
                  behavior: 'smooth'
                });
                // Clear previous selected item and add selected class to new item
                if (selected) {
                  selected.classList.remove('selected');
                }
                snapTarget.classList.add('selected');
                selected = snapTarget;
                snapTarget = null;
                snapOffset = null;
              }
              } else {
                if (selected === snapTargets[0] || selected === snapTargets[1] || snapTargets[snapTargets.length - 1] || snapTargets[snapTargets.length - 2]) {
                }
                else {
                scrollmenu.scrollTo({
                  left: snapOffset,
                  behavior: 'smooth'
                });
                // Clear previous selected item and add selected class to new item
                if (selected) {
                  selected.classList.remove('selected');
                }
                snapTarget.classList.add('selected');
                selected = snapTarget;
                snapTarget = null;
                snapOffset = null;
              }
              }


              }
            }, 100);
          });

            item.addEventListener('mouseup', e => {
              if (!isDragging) { // select only if not dragging
                if (selected) {
                  selected.classList.remove('selected'); // remove selected class from previous selection
                }
                item.classList.add('selected'); // add selected class to current selection
                selected = item; // set selected item to current selection
                centerSelectedElement()
              }
              isDragging = false;
            });

            item.addEventListener('mouseleave', e => {
              isDragging = false;
            });
          });




          function centerSelectedElement() {
            const containerWidth = scrollmenu.offsetWidth;
            const scrollLeft = scrollmenu.scrollLeft;
            const itemOffsetLeft = selected.offsetLeft - scrollmenu.offsetLeft;
            const itemWidth = selected.offsetWidth;

            let centerOffset = containerWidth / 2 - itemWidth / 2;
            if (itemOffsetLeft + itemWidth / 2 < containerWidth / 2) {
              centerOffset = itemOffsetLeft - centerOffset;
            } else {
              centerOffset = itemOffsetLeft + itemWidth / 2 - containerWidth / 2;
            }

            scrollmenu.scrollTo({
              left: centerOffset,
              behavior: 'smooth'
            });
          }

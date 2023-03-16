
          const scrollmenu = document.querySelector('.scrollmenu');
          let isDragging = false;
          let lastX;
          let selected = null; 
          const scrollMenu = document.querySelector('.scrollmenu');
          const leftArrow = document.querySelector('.scrollmenu__arrow--left');
          const rightArrow = document.querySelector('.scrollmenu__arrow--right');
          const eventButtons = document.querySelectorAll('.event-button');
          const buttonContainer = document.querySelector('.button-container');

          eventButtons.forEach(button => {
            button.addEventListener('click', () => {
              // remove previously created buttons (if any)
              buttonContainer.innerHTML = '';
          
              const eventData = JSON.parse(button.dataset.event);
              eventData.forEach(summary => {
                const button = document.createElement('button');
                button.textContent = summary;
                button.classList.add('time_select');
                button.addEventListener('click', () => {
                  // remove the 'select' class from all buttons
                  buttonContainer.querySelectorAll('.time_select').forEach(btn => {
                    btn.classList.remove('selected');
                  });
                  // add the 'select' class to the clicked button
                  button.classList.add('selected');
                });
                buttonContainer.appendChild(button);
              });
            });
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

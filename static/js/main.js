// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    let hoverDetail = null;
  
    // Attach hover listeners to each product card
    document.querySelectorAll('.product-card').forEach(card => {
      const itemId = card.getAttribute('data-item-id');
  
      card.addEventListener('mouseenter', function(e) {
        // Fetch the hover snippet
        fetch(`/item/${itemId}/hover`)
          .then(response => response.text())
          .then(html => {
            // Parse the HTML and grab the root element
            const wrapper = document.createElement('div');
            wrapper.innerHTML = html.trim();
            hoverDetail = wrapper.firstElementChild;
  
            // Add to document
            document.body.appendChild(hoverDetail);
            positionHover(e);
          })
          .catch(err => {
            console.error('Error loading item details:', err);
          });
      });
  
      card.addEventListener('mousemove', function(e) {
        if (hoverDetail) {
          positionHover(e);
        }
      });
  
      card.addEventListener('mouseleave', function() {
        if (hoverDetail) {
          hoverDetail.remove();
          hoverDetail = null;
        }
      });
    });
  
    // Position the hover-detail near the cursor, keeping it onscreen
    function positionHover(e) {
      const padding = 10;
      const popupWidth = hoverDetail.offsetWidth;
      const popupHeight = hoverDetail.offsetHeight;
      let x = e.pageX + padding;
      let y = e.pageY + padding;
  
      // If the popup would overflow right edge, flip left
      if (x + popupWidth > window.innerWidth) {
        x = e.pageX - popupWidth - padding;
      }
      // If the popup would overflow bottom edge, flip upward
      if (y + popupHeight > window.innerHeight) {
        y = e.pageY - popupHeight - padding;
      }
  
      hoverDetail.style.position = 'absolute';
      hoverDetail.style.left = `${x}px`;
      hoverDetail.style.top = `${y}px`;
      hoverDetail.style.zIndex = 1000;
    }
  });
  
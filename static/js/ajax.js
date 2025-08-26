// static/js/ajax.js

document.addEventListener('DOMContentLoaded', () => {
    let hoverDetailEl = null;
  
    // Helper: position the hover-detail box near the cursor
    function positionHover(e) {
      const padding = 8;
      const popupWidth = hoverDetailEl.offsetWidth;
      const popupHeight = hoverDetailEl.offsetHeight;
      let x = e.pageX + padding;
      let y = e.pageY + padding;
  
      // Flip horizontally if overflowing
      if (x + popupWidth > window.innerWidth) {
        x = e.pageX - popupWidth - padding;
      }
      // Flip vertically if overflowing
      if (y + popupHeight > window.innerHeight) {
        y = e.pageY - popupHeight - padding;
      }
  
      hoverDetailEl.style.left = `${x}px`;
      hoverDetailEl.style.top = `${y}px`;
    }
  
    // Attach hover listeners to each product-card
    document.querySelectorAll('.product-card').forEach(card => {
      const itemId = card.dataset.itemId;
  
      card.addEventListener('mouseenter', e => {
        fetch(`/item/${itemId}/hover`)
          .then(res => {
            if (!res.ok) throw new Error('Network response was not ok');
            return res.text();
          })
          .then(html => {
            // Create a container for the returned snippet
            const wrapper = document.createElement('div');
            wrapper.innerHTML = html.trim();
            hoverDetailEl = wrapper.firstElementChild;
            
            // Style it and append to body
            hoverDetailEl.style.position = 'absolute';
            hoverDetailEl.style.zIndex = '1000';
            document.body.appendChild(hoverDetailEl);
  
            // Initial positioning
            positionHover(e);
          })
          .catch(err => console.error('Error fetching hover details:', err));
      });
  
      card.addEventListener('mousemove', e => {
        if (hoverDetailEl) {
          positionHover(e);
        }
      });
  
      card.addEventListener('mouseleave', () => {
        if (hoverDetailEl) {
          hoverDetailEl.remove();
          hoverDetailEl = null;
        }
      });
    });
  });
  
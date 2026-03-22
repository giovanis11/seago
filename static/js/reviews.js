const stars = document.querySelectorAll('.star-btn');
const ratingInput = document.querySelector('#rating-value');

if (stars.length > 0) {
  stars.forEach(star => {
    star.addEventListener('mouseover', function() {
      const val = this.dataset.value;
      stars.forEach(s => {
        s.classList.toggle('bi-star-fill', s.dataset.value <= val);
        s.classList.toggle('bi-star', s.dataset.value > val);
        s.style.color = s.dataset.value <= val ? '#bb2d3c' : '#ccc';
      });
    });

    star.addEventListener('mouseout', function() {
      const current = ratingInput.value;
      stars.forEach(s => {
        s.classList.toggle('bi-star-fill', s.dataset.value <= current);
        s.classList.toggle('bi-star', s.dataset.value > current);
        s.style.color = s.dataset.value <= current ? '#bb2d3c' : '#ccc';
      });
    });

    star.addEventListener('click', function() {
      ratingInput.value = this.dataset.value;
    });
  });

  document.querySelector('#submit-review')?.addEventListener('click', function() {
    const rating = ratingInput.value;
    const comment = document.querySelector('#review-comment').value;
    const boatId = document.querySelector('#submit-review').dataset.boatId;
    const msgDiv = document.querySelector('#review-message');
    const csrfToken = document.querySelector('#submit-review').dataset.csrf;

    if (rating == 0) {
      msgDiv.innerHTML = '<span class="text-danger">Please select a rating.</span>';
      return;
    }

    fetch(`/reviews/create/${boatId}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `rating=${rating}&comment=${encodeURIComponent(comment)}`
    })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        msgDiv.innerHTML = `<span class="text-danger">${data.error}</span>`;
      } else {
        msgDiv.innerHTML = '<span class="text-success">Review submitted! Refresh to see it.</span>';
        document.querySelector('#review-comment').value = '';
        ratingInput.value = 0;
        stars.forEach(s => {
          s.classList.remove('bi-star-fill');
          s.classList.add('bi-star');
          s.style.color = '#ccc';
        });
      }
    });
  });
}